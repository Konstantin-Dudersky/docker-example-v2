ARG NGINX_VER
FROM nginx:${NGINX_VER}
# контекст - родительская папка
COPY webapp/nginx.conf /etc/nginx/nginx.conf
COPY webapp/dist/webapp /usr/share/nginx/html
EXPOSE 80
