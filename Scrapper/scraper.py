# scraper.py

import requests
from bs4 import BeautifulSoup

# URL del Workshop de Steam (modificada según sea necesario)
STEAM_WORKSHOP_URL = "https://steamcommunity.com/sharedfiles/filedetails/?id={appid}"

# Ruta a la imagen predeterminada cuando no se encuentra la imagen de preview
DEFAULT_IMAGE_URL = "src/images/no_images.jpg"

def scrape_preview_image_and_size(appid: str):
    """
    Realiza scraping para obtener la imagen de preview, tamaño y fecha de publicación del mod en Steam Workshop.
    Si no se encuentra la imagen o la información, devuelve valores predeterminados.
    """
    url = STEAM_WORKSHOP_URL.format(appid=appid)
    
    try:
        # Obtener la página HTML del Workshop
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Error: No se pudo obtener la página del mod, código de estado {response.status_code}")
            return DEFAULT_IMAGE_URL, None, None  # Devolvemos valores predeterminados en caso de error
        
        # Parsear la página con BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar la imagen de preview usando la clase 'workshopItemPreviewImageMain'
        preview_image = None
        preview_image_tag = soup.find('img', class_='workshopItemPreviewImageMain')
        if preview_image_tag and 'src' in preview_image_tag.attrs:
            preview_image = preview_image_tag['src']
        
        # Buscar el tamaño del mod y la fecha de publicación
        size = None
        posted_date = None
        
        details_container = soup.find('div', class_='detailsStatsContainerRight')
        
        if details_container:
            # Tamaño del archivo
            size_tag = details_container.find('div', class_='detailStatsSize')
            if size_tag:
                size = size_tag.get_text(strip=True)
            
            # Fecha de publicación
            posted_tag = details_container.find('div', class_='detailStatsDate')
            if posted_tag:
                posted_date = posted_tag.get_text(strip=True)
        
        return preview_image if preview_image else DEFAULT_IMAGE_URL, size, posted_date
        
    except requests.RequestException as e:
        print(f"Error en la solicitud: {e}")
        return DEFAULT_IMAGE_URL, None, None  # Devolvemos valores predeterminados en caso de error
