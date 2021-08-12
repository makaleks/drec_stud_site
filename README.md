# Стиралка-сайт
Создан в стенах [ФРТК](https://github.com/makaleks/drec_stud_site), дальше доработан [ребятами](CONTRIBUTORS.md).

Состоит из нескольких микросервисов:
1. Бекенд сайта: `backend/`, написан на Django, [readme](backend/README.md).
2. Фронтенд: `frontend/`, раздает статику. Генерится целиком из `backend/src/static`, потом через volume mount
   прокидывается в `nginx` по пути `/app/collected_static`. Внутри лежит `swdc` для исторических причин,
   фактически же ничего из него не используется в деплое.
3. Чат-бот ВК: `vk_bot/`, написан на [vk_bottle](https://github.com/timoniq/vkbottle), [readme](vk_bot/README.md).
4. Postgres DB: `postgres/`, хранит все данные сайта, в `postgres/sql` лежат init-скрипты.
5. Backup service: ежедневные, еженедельные и ежемесячные бекапы с ротацией ([подробнее](https://registry.hub.docker.com/r/prodrigestivill/postgres-backup-local)). 
   Кладет бекапы в `postgres/db_backups/`.
6. money return service: `money_return/`, костыль, 
   который раз в 30 минут ходит в БД и возвращает деньги всем, 
   кто записался на машинку, закрытую админом, а также обнуляет оплату за заказ.
7. redis: хранит пароли для экстренной авторизации, они раздаются через чат-бота. 
   Самая неавтоматизированная часть сейчас, все выгрузки в него идут руками.
   
# Запуск
## Минимум
1. В `backend/` заполняем `backend_setting_additions.py` по примеру `backend_setting_additions_example.py`
2. В `vk_bot` заполняем `.env` по примеру `.env.example`.
3. При необходимости правим картиночки в `backend/src/static/img`, там же можно прочие фронтендовские
   штуки поменять.

Потом дергаем:
```shell
docker-compose up
```

Появится сайт, но в нем нет ни сервисов, ни юзеров. Создать их - ваша ответственность.

## Заполнение данными
Если у вас есть бекап прошлой БД, то можно заполнить им сразу данные.
Положите `.sql` файл (это надо `.sql.gz` распаковать) в [`postgres/sql/10_db_data.sql`](postgres/sql).

Добавьте 
```sql
\c drec_stud_site;
```
в самое начало файла `10_db_data.sql`.

Все, теперь при `docker-compose up` бекап будет раскатан.
_Работает на том, что `postgres/sql/` монтируется в `/docker-entrypoint-initdb.d/` постгреса._

**Про создание пользователей можно почитать в [readme на backend](backend/README.md).**

## Логирование
Каждый сервис пишет логи в свою папку:
1. `backend/logs`;
2. `frontend/logs`;
3. `vk_bot/logs`.

В боте логи ротируются каждый день. Помимо этого есть мониторинг (см. его [README.md](monitoring/README.md))