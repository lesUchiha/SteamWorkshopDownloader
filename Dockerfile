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

# Copiar y verificar que el archivo existe
COPY api/requirements.txt /var/www/api/requirements.txt

# Mostrar el contenido del archivo para debug
RUN cat /var/www/api/requirements.txt

# Instalar dependencias en un entorno virtual
RUN python3 -m venv venv
RUN . venv/bin/activate && pip install --upgrade pip
RUN . venv/bin/activate && pip install -r requirements.txt

# Copiar el código del API
COPY api/ .

# Configurar supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000

CMD ["/usr/bin/supervisord"]
