FROM nginx

COPY /src/nginx.conf /etc/nginx/
WORKDIR /src

COPY ./src/nginx /src/