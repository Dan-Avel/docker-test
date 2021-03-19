FROM nginx

COPY /src/nginx.conf /etc/nginx/
WORKDIR /src

COPY requirements.txt /src/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src /src/