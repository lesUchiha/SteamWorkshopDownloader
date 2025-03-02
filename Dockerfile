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

# Copiar los archivos PHP (frontend)
WORKDIR /var/www/html
COPY public/ .

# Configurar el API
WORKDIR /var/www/api
# Copiar el archivo de requirements.txt desde la carpeta api
COPY api/requirements.txt .
# Instalar las dependencias de Python usando el archivo de requirements.txt
RUN pip3 install -r requirements.txt
# Copiar el resto del código del API
COPY api/ .

# Copiar la configuración de supervisord
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Exponer el puerto que Railway asigna (usualmente se usa la variable $PORT, pero aquí usamos 8000)
EXPOSE 8000

CMD ["/usr/bin/supervisord"]
