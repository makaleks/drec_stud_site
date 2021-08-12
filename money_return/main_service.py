import os
import time

import psycopg2
from contextlib import contextmanager
from psycopg2.extensions import cursor, connection
from loguru import logger


@contextmanager
def get_connection() -> connection:
    try:
        with psycopg2.connect(
                host=os.environ.get("POSTGRES_HOST", "postgres"),
                dbname=os.environ.get("POSTGRES_DB", "drec_stud_site"),
                user=os.environ.get("POSTGRES_USER", "postgres"),
                password=os.environ.get("POSTGRES_PASSWORD", "postgres")
        ) as conn:    # type: connection
            yield conn
    except Exception as e:
        logger.error(f'error in database: {e}')


def read_query_data(query: str):
    with get_connection() as conn:  # type: connection
        with conn.cursor() as curr: # type: cursor
            curr.execute(query)
            data = curr.fetchall()
            return data


if __name__ == '__main__':
    GET_BAD_ORDERS = """
    SET TIMEZONE='Europe/Moscow';
    WITH data AS (
        SELECT
               washing_order.id,
               datetimetz_pl(date_start, time_start)            AS start_time,
               CASE
                   WHEN time_end < time_start
                       THEN datetimetz_pl(date(date_start + INTERVAL '1 day'), time_end)
                   ELSE datetimetz_pl(date_start, time_end) END AS end_time,
               payed,
               uu.account_id
        FROM washing_order
        INNER JOIN washing_washingmachine ww on ww.id = washing_order.item_id
        INNER JOIN user_user uu on uu.id = washing_order.user_id
        WHERE ww.is_active = false
    )
    SELECT *
    FROM data
    WHERE start_time <= now()
    AND end_time >= now();
    """
    while True:
        bad_clients = read_query_data(GET_BAD_ORDERS)
        logger.info(f'found bad orders: {bad_clients}')
        for order_id, start_time, end_time, payed, account_id in bad_clients:
            logger.info(f'handling order with id={order_id} where account_id={account_id} payed {payed} RUB')
            with get_connection() as conn:      # type: connection
                try:
                    with conn.cursor() as curr:     # type: cursor
                        # Пометить заказ как с вернувшимися деньгами (не стоит удалять)
                        curr.execute("""
                        UPDATE washing_order
                        SET payed = 0
                        WHERE id = %s
                        """, (order_id, ))
                        # Вернуть деньги
                        curr.execute("""
                        UPDATE user_user
                        SET account = account + %s
                        WHERE account_id=%s
                        """, (payed, account_id, ))
                    conn.commit()
                except Exception as e:
                    logger.error(e)
                    conn.rollback()
                    logger.info('rolled back the transaction')
        logger.info('sleeping 20 minutes')
        time.sleep(20 * 60)

