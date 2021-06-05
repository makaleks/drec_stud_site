# Стиралка-сайт
Создан в стенах [ФРТК](https://github.com/makaleks/drec_stud_site), дальше доработан [ребятами](CONTRIBUTORS.md).

Состоит из нескольких микросервисов:
1. Бекенд сайта: `backend/`, написан на Django, [readme](backend/README.md).
2. nginx: `nginx/`, раздает статику. Пока не знаем, как генерить, поэтому просто лежит в VCS.
3. Чат-бот ВК: `vk_bot/`, написан на [vk_bottle](https://github.com/timoniq/vkbottle), [readme](vk_bot/README.md).
4. Postgres DB: `postgres/`, хранит все данные сайта, в `postgres/sql` лежат init-скрипты.
5. Backup service: ежедневные, еженедельные и ежемесячные бекапы с ротацией ([подробнее](https://registry.hub.docker.com/r/prodrigestivill/postgres-backup-local)). 
   Кладет бекапы в `postgres/db_backups/`.
6. money return service: `machine_closed_watchdog/`, костыль, 
   который раз в 30 минут ходит в БД и возвращает деньги всем, 
   кто записался на машинку, закрытую админом, а также обнуляет оплату за заказ.
7. redis: хранит пароли для экстренной авторизации, они раздаются через чат-бота. 
   Самая неавтоматизированная часть сейчас, все выгрузки в него идут руками.
   
# Запуск
1. В `backend/` заполняем `backend_setting_additions.py` по примеру `backend_setting_additions_example.py`
2. В `vk_bot` заполняем `.env` по примеру `.env.example`

Потом дергаем
```shell
docker-compose up
```

Появится сайт, но в нем нет ни сервисов, ни юзеров. Создать их - ваша ответственность.

**Про создание пользователей можно почитать в [readme на backend](backend/README.md).**