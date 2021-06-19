# Мониторинг стиралки
Быстрый способ узнать, что происходит, без ssh на сервер.

## Как поднять
Инструкции одноразовые, их выполнять только после падения mongodb на graylog.
### Стримы
Нужны, чтобы делить логи от разных сервисов.
TODO: дока на это

### Пайплайны и экстракторы
Парсят куски сообщений и обогащают ивенты полезными полями.
TODO: дока на это.

### Основное
1. В этой папке выполнить `docker-compose up`.
2. Логин/пароль admin/admin, идем с ним на `localhost:9000`, логинимся.
3. `System` -> `Sidecars` -> `Create or reuse a token for the graylog-sidecar user`
4. Token name ставим в `filebeat`. Копируем токен, открываем `docker-compose.yml`,
   вставляем токен в `GS_SERVER_API_TOKEN`.
5. Заново деплоим мониторинг: `docker-compose up -d`. Должен перезапуститься только `graylog-sidecar-all-filesd`.
6. Настраиваем заливку логов: `System` -> `Sidecars` -> `Configuration` (наверху) ->
   зеленая кнопка `Create configuration`. Имя `filebeat` (можно другое), collector
   ставим `filebeat on Linux`, в `Configuration` вставляем содержимое [`filebeat.yml`](filebeat.yml). Тыкаем
   на `Create`.
7. Конфиги готовы, их теперь можно раскатить на filebeat. Логика такая: graylog хранит все конфиги и рассылает
   их на машины `filebeat+sidecar` (типа единое место хранения). Поэтому идем в `System` -> `Sidecars` -> выбираем
   единственную запись -> `Manage sidecar` -> тык на `filebeat` -> сверху справа `Configure` -> выбираем наш созданный
   `filebeat` (или как вы его там назвали). _Это раскатит конфиг._
8. Осталось сказать Graylog, чтобы слушал входящие логи. Идем
   в `System` -> `Inputs`. В выпадающем меню "Select input" выбираем `Beats` -> `Launch new input`. Ставим 
   флаг `Global`, `title` ставим `log files`, листаем до конца вниз и жмем `Save`.
9. Вы великолепны, теперь все лог-файлы льются в graylog.