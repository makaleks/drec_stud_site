# Мониторинг стиралки
Быстрый способ узнать, что происходит, без ssh на сервер.

## Как поднять
Инструкции одноразовые, их выполнять только после падения mongodb на graylog.

### Пароли
Заполняем .env по примеру .env.example

### Стримы
Нужны, чтобы делить логи от разных сервисов.
Фильтры в них ставим по `filebeat_log_file_path` contains:
- vk_bot
- backend
- frontend

Три стрима получится.

### Пайплайны
Парсят куски сообщений и обогащают ивенты полезными полями.

Список:
1. `nginx logs` - `extract IP`. Парсит всю инфу из access log
2. `payment logs` - `parse payment`. Парсит пополнения бабла
3. `VK bot door commands` - `parse loguru logs` -> `parse door command`. Парсят команды, который бот шлет двери.
4. `VK bot open request` - `parse loguru logs` -> `parse open request`. Парсят запросы из ВК на открытие двери.

Стоит обогатить другими пайплайнами по мере возможности.

**НЕ ЗАБУДЬТЕ выставить порядок пайплайнов в `System` -> `Configuration` (пайплайны в самом конце!)**.

### Основное
1. В этой папке выполнить `docker-compose up`.
2. Логин/пароль admin/admin, идем с ним на `localhost:9000`, логинимся.
3. `System` -> `Sidecars` -> `Create or reuse a token for the graylog-sidecar user`
4. Token name ставим в `filebeat`. Копируем токен, открываем `docker-compose.yml`,
   вставляем токен в `.env` в поле `GS_SERVER_API_TOKEN`.
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