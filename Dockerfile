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

# Copiar los archivos PHP y establecer el directorio para el frontend
WORKDIR /var/www/html
COPY public/ .

# Establecer el directorio de trabajo para la API
WORKDIR /var/www/api
# Copiar la carpeta 'api' (incluyendo requirements.txt y el código)
COPY api/ .

# Instalar dependencias de Python para la API
RUN pip3 install -r requirements.txt

# Copiar la configuración de supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Exponer el puerto que Railway proveerá (Railway asigna el puerto mediante $PORT)
EXPOSE 8000

CMD ["/usr/bin/supervisord"]
