# Usa una imagen base con PHP (puedes elegir la versión que necesites)
FROM php:8.0-cli

# Instala dependencias adicionales si es necesario (por ejemplo, extensiones de PHP)
RUN docker-php-ext-install mysqli

# Copia el contenido del directorio 'public' a la carpeta donde se servirán los archivos
WORKDIR /var/www/html
COPY public/ .

# Expone el puerto que Railway proveerá en la variable de entorno $PORT
EXPOSE 8000

# Inicia el servidor PHP incorporado
CMD ["php", "-S", "0.0.0.0:8000", "-t", "/var/www/html"]
