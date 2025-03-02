FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Instalar PHP, Python y dependencias necesarias
RUN apt-get update && apt-get install -y \
    php-cli php-fpm php-mysqli \
    python3 python3-pip \
    nginx supervisor \
    && rm -rf /var/lib/apt/lists/*

# Configurar el API
WORKDIR /var/www/api

# Copiar el archivo de dependencias
COPY api/requirements.txt /var/www/api/requirements.txt

# Mostrar el contenido del archivo para debug
RUN cat /var/www/api/requirements.txt

# Instalar dependencias de Python de forma global
RUN pip3 install --no-cache-dir -r /var/www/api/requirements.txt

# Copiar el código del API
COPY api/ .

# Configurar supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000

CMD ["/usr/bin/supervisord"]
