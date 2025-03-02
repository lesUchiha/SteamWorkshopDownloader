FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Instalar PHP, Python, Nginx y dependencias necesarias
RUN apt-get update && apt-get install -y \
    php-cli php-fpm php-mysqli \
    python3 python3-pip python3-venv \
    nginx supervisor \
    && rm -rf /var/lib/apt/lists/*

# Configurar el API
WORKDIR /var/www/api

# Copiar requirements.txt
COPY api/requirements.txt /var/www/api/requirements.txt

# Mostrar el contenido del archivo para debug
RUN cat /var/www/api/requirements.txt

# Crear un entorno virtual e instalar dependencias correctamente
RUN python3 -m venv venv
RUN /var/www/api/venv/bin/pip install --upgrade pip
RUN /var/www/api/venv/bin/pip install -r /var/www/api/requirements.txt

# Copiar el código del API
COPY api/ .

# Configurar supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000

CMD ["/usr/bin/supervisord"]
