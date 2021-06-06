FROM nginx
WORKDIR /app
COPY nginx.conf /etc/nginx/nginx.conf
COPY media/ /app/media
# NOTE: collected_static генерится на бекенде (ну вот так, да)
# пока что передаем в nginx через volume mount
# НЕ ЗАБУДЬЕ передать collected_static в /app/collected_static
