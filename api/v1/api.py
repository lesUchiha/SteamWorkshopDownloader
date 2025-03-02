from fastapi import FastAPI, HTTPException, Query, Path
import httpx
import re
import asyncio
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO

app = FastAPI()

# Permitir CORS para facilitar pruebas (ajusta según tus necesidades)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Formato de la URL externa:
# http://workshop9.abcvg.info/archive/{workshopId}/{appid}.zip
EXTERNAL_DOWNLOAD_URL = "http://workshop9.abcvg.info/archive/{workshopId}/{appid}.zip"
STEAM_WORKSHOP_THUMBNAIL_URL = "http://steamworkshop.download/download/view/{appid}"

def extract_appid_from_url(url: str) -> str:
    """
    Extrae el appid de una URL de Steam Workshop.
    Ejemplo:
      https://steamcommunity.com/sharedfiles/filedetails/?id=2689118821  
    Extrae "2689118821".
    """
    match = re.match(r"https://steamcommunity\.com/sharedfiles/filedetails/\?id=(\d+)", url)
    if match:
        return match.group(1)
    else:
        raise HTTPException(status_code=400, detail="La URL del mod no es válida.")

async def fetch_external_file(download_url: str):
    """
    Hace un GET a la URL externa para obtener el contenido del archivo.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(download_url, timeout=30.0)  # Aumentamos el tiempo de espera
            if response.status_code == 200:
                size = response.headers.get("Content-Length", "Desconocido")  # Tamaño del archivo
                return response.content, size
            else:
                raise HTTPException(status_code=404, detail="El mod no está disponible o fue bloqueado.")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Error al obtener los datos del mod.")
        except httpx.TimeoutException:
            raise HTTPException(status_code=408, detail="La solicitud al mod excedió el tiempo de espera.")

async def fetch_thumbnail(appid: str):
    """
    Obtiene la portada (thumbnail) del mod usando steamworkshop.download.
    """
    async with httpx.AsyncClient() as client:
        try:
            # Hacer la solicitud a la URL para obtener la imagen
            thumb_url = STEAM_WORKSHOP_THUMBNAIL_URL.format(appid=appid)
            response = await client.get(thumb_url)
            if response.status_code == 200:
                # Devolver la imagen de la portada como una respuesta binaria
                return StreamingResponse(BytesIO(response.content), media_type="image/jpeg")
            else:
                raise HTTPException(status_code=404, detail="No se pudo obtener la portada del workshop.")
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Error al obtener la portada del mod.")

@app.get("/download")
async def prepare_download(
    workshopUrl: str = Query(..., description="URL del mod en Steam Workshop, por ejemplo: https://steamcommunity.com/sharedfiles/filedetails/?id=2689118821"),
    workshopId: str = Query(..., description="WorkshopId que se usará en la URL externa")
):
    # Extraer el appid de la URL de Steam
    appid = extract_appid_from_url(workshopUrl)
    # Crear un identificador compuesto: workshopId-appid
    mod_identifier = f"{workshopId}-{appid}"
    # Construir la URL de descarga interna de la API
    download_api_url = f"http://127.0.0.1:8000/download_mod/{mod_identifier}.zip"
    
    # Obtener la portada (thumbnail)
    thumbnail_url = await fetch_thumbnail(appid)
    
    return JSONResponse(content={"download_url": download_api_url, "thumbnail_url": thumbnail_url.url})

@app.get("/download_mod/{mod}.zip")
async def download_mod_file(
    mod: str = Path(..., description="Identificador compuesto en formato workshopId-appid")
):
    # Se espera que 'mod' tenga el formato "workshopId-appid"
    parts = mod.split("-")
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="El identificador del mod es inválido.")
    workshopId, appid = parts
    # Construir la URL externa con el formato correcto
    external_url = EXTERNAL_DOWNLOAD_URL.format(workshopId=workshopId, appid=appid)
    
    # Obtener el contenido del archivo de forma asíncrona (timeout total de 30 segundos)
    file_content, file_size = await asyncio.wait_for(fetch_external_file(external_url), timeout=30.0)
    
    # Crear el nombre del archivo como el appid
    filename = f"{appid}.zip"
    
    # Retornar el archivo para descarga directa
    response = StreamingResponse(
        BytesIO(file_content),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(file_size)  # Incluir el tamaño del archivo
        }
    )
    
    return response
