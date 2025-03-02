FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Instalar PHP, Python, Nginx y supervisord
RUN apt-get update && apt-get install -y \
    php-cli php-fpm php-mysqli \
    python3 python3-pip \
    nginx supervisor \
    && rm -rf /var/lib/apt/lists/*

# Configurar Nginx copiando el archivo de configuración
COPY nginx.conf /etc/nginx/nginx.conf

# Copiar los archivos PHP
WORKDIR /var/www/html
COPY public/ .

# Copiar la API
WORKDIR /var/www
COPY api/ api/

# Instalar dependencias de Python para la API
RUN pip3 install -r requirements.txt

# Copiar la configuración de supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Exponer el puerto (Railway asigna el puerto a través de la variable PORT)
EXPOSE 8000

CMD ["/usr/bin/supervisord"]
