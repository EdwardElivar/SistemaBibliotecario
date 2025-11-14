#********************************************************************************
#   LIBRERIAS
#********************************************************************************

import os
import re
import json
import base64
import requests
import streamlit as st # type: ignore
from openai import OpenAI # pyright: ignore[reportMissingImports]


#*****************************************************************************************
#   GET_OPENAI_API_KEY - Obtiene la clave de la API de OpenAI desde el ambiente 
#                        donde se esté ejecutando la aplicación, local o StreamLit Cloud
#*****************************************************************************************

# Cliente OpenAI usando variable de entorno OPENAI_API_KEY
def get_openai_api_key():

    #TOKEN PARA STREAMLIT
    try:
        key = st.secrets.get("OPENAI_API_KEY", None)
        if key:
            return key
    except Exception:
        pass

    #TOKEN LOCAL ARCHIVO .ENV
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key

    raise ValueError("OPENAI_API_KEY no configurada.")

OPENAI_API_KEY = get_openai_api_key()
client = OpenAI(api_key=OPENAI_API_KEY)


#********************************************************************************
#   _CALL_OPENAI_FOR_COVER - Usamos OpenAI para escanear la portada del libro
#                            y extraer información
#********************************************************************************

def _call_openai_for_cover(image_bytes: bytes):

    import base64
    import json

    # ⬇⬇⬇ PARA DEBUG EN STREAMLIT CLOUD: lo que llega desde la cámara
    #st.markdown("### 🔍 DEBUG - Imagen que se envía a OpenAI")
    #st.write("Tamaño de la imagen (bytes):", len(image_bytes))
    #st.image(image_bytes, caption="Imagen capturada (raw)")
    # ⬆⬆⬆
    
        
    #Usamos OpenAI para intentar extraer titulo / autor / isbn desde la portada
    img_b64 = base64.b64encode(image_bytes).decode("utf-8")

    # ⬇⬇⬇ PARA DEBUG EN STREAMLIT CLOUD: base64 parcial
    #st.markdown("#### 🔍 DEBUG - Imagen en base64 (primeros 300 caracteres)")
    #st.code(img_b64[:300] + "...", language="text")
    # ⬆⬆⬆

    
    # Prompt para extraer la informacion de la portada
    system_prompt = """
    Eres un asistente para un sistema bibliotecario.
    Tu tarea es leer la portada de un libro (si existe) y devolver datos estructurados.

    INSTRUCCIONES IMPORTANTES:
    - Si no estás seguro, deja el campo vacío en lugar de adivinar.
    - NO inventes datos. Si un campo no se ve claramente en la imagen, déjalo como cadena vacía.
    - Solo responde con un JSON valido, sin texto extra.
    - Si hay varios autores, usa solo el autor principal (el más destacado en la portada).
    - No traduzcas los datos: escribe el título y el autor exactamente como aparecen en la portada.

    Estructura exacta:
    {
      "titulo": string,
      "autor": string,
      "isbn": string
    }
    """

    # ⬇⬇⬇ PARA DEBUG EN STREAMLIT CLOUD: prompt que mando a OpenAI
    #st.markdown("#### 🔍 DEBUG - System prompt enviado a OpenAI")
    #st.code(system_prompt, language="markdown")
    # ⬆⬆⬆

    # =======================
    # PRINT: Lo que envio
    # =======================
    print("\n===== ENVÍO A OPENAI =====")
    print("System prompt:")
    print(system_prompt)
    print("\nUser prompt:")
    print("Analiza esta imagen y devuelve los datos del libro si es posible.")
    print("\nImagen Base64 (primeros 200 chars):")
    print(img_b64[:200] + "...")
    print("============================\n")

    #Solicitud a la API de OpenAI modelo gpt-4.1-mini para analizar la imagen en base64
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analiza esta imagen y devuelve los datos del libro si es posible."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                    },
                ],
            },
        ],
    )

    # ⬇⬇⬇ PARA DEBUG EN STREAMLIT CLOUD 
    #st.markdown("### 📥 DEBUG - Respuesta de OpenAI (objeto)")
    #st.write(resp)
    
    #st.markdown("#### 📥 DEBUG - resp.choices[0].message.content")
    #st.code(resp.choices[0].message.content, language="json")
    # ⬆⬆⬆

    print("*****************************************")
    print(OPENAI_API_KEY )
    print("*****************************************")
    # =======================
    # PRINT: Lo que recibes
    # =======================
    print("\n===== RESPUESTA COMPLETA DE OPENAI =====")
    print(resp)
    print("=========================================\n")

    print("\n===== RAW CONTENT =====")
    print(resp.choices[0].message.content)
    print("========================\n")

    print("*****************************************")
    print(OPENAI_API_KEY)
    print("*****************************************")

    raw = resp.choices[0].message.content.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None

    return {
        "titulo": (data.get("titulo") or "").strip(),
        "autor": (data.get("autor") or "").strip(),
        "isbn": (data.get("isbn") or "").replace("-", "").strip()
    }


#********************************************************************************
#   LIMPIAR ISBN - Este método toma un valor de ISBN y lo limpia, normaliza y 
#                  valida, devolviendo un ISBN correcto
#********************************************************************************

def limpiar_isbn(isbn: str) -> str:
    
    #Normaliza ISBN dejando solo dígitos y X; acepta 10 o 13 caracteres.
    if not isbn:
        return ""
    isbn = isbn.upper()
    isbn = re.sub(r"[^0-9X]", "", isbn)
    if len(isbn) in (10, 13):
        return isbn
    return ""

#********************************************************************************
#   BUSCAR_EN_GOOGLE_BOOKS - Este método consulta la API de Google Books para 
#                            obtener datos adicionales deL libro (título, autor, editorial, año, portada, ISBN, etc.).
#********************************************************************************
GOOGLE_BOOKS_URL="https://www.googleapis.com/books/v1/volumes"

def buscar_en_google_books(isbn=None, titulo=None, autor=None):
    
    """Consulta Google Books para completar datos. Prioriza ISBN si existe."""
    if isbn:
        q = f"isbn:{isbn}"
    elif titulo and autor:
        q = f'intitle:"{titulo}" inauthor:"{autor}"'
    elif titulo:
        q = f'intitle:"{titulo}"'
    else:
        return None

    params = {"q": q, "maxResults": 5}


    # 🔍 DEBUG EN STREAMLIT - Lo que enviamos a Google Books
    st.markdown("### 🔍 DEBUG - Consulta enviada a Google Books")
    st.write("Query:", q)
    st.write("Parámetros:", params)
    st.write("URL:", GOOGLE_BOOKS_URL)
    
    
    # =======================
    # LOG: Lo que envio
    # =======================
    print("\n===== ENVÍO A GOOGLE BOOKS =====")
    print("URL:", GOOGLE_BOOKS_URL)
    print("Parámetros GET:", params)
    print("=================================\n")

    try:
        r = requests.get(GOOGLE_BOOKS_URL, params=params, timeout=10)

        # 🔍 DEBUG EN STREAMLIT - Respuesta HTTP
        st.markdown("### 📥 DEBUG - RAW Response de Google Books")
        st.write("Status:", r.status_code)
        st.write("Headers:", dict(r.headers))
        # Mostrar texto RAW (limitado)
        raw_text = r.text[:1500] + "..." if len(r.text) > 1500 else r.text
        st.code(raw_text, language="json")


        
        # =======================
        # LOG: Respuesta completa
        # =======================
        print("\n===== RESPUESTA DE GOOGLE BOOKS =====")
        print("Status code:", r.status_code)
        print("Headers:", dict(r.headers))
        print("Contenido RAW:")
        print(r.text[:2000] + "..." if len(r.text) > 2000 else r.text)  # límite por seguridad
        print("=====================================\n")


        r.raise_for_status()
        data = r.json()

        # 🔍 DEBUG JSON parseado
        st.markdown("### 📥 DEBUG - JSON parseado de Google Books")
        st.json(data)

    
    except Exception:
        return None



    
    items = data.get("items")
    if not items:
        return None

    # Tomamos el primer resultado que encuentre
    info = items[0].get("volumeInfo", {})

    autores = info.get("authors") or []
    autores_str = ", ".join(autores) if autores else ""

    # Algunos libros no tienen industryIdentifiers bien formados
    isbn_gb = ""
    for ident in info.get("industryIdentifiers", []):
        if ident.get("type") in ("ISBN_13", "ISBN_10"):
            isbn_gb = ident.get("identifier", "").strip()
            break

    # Portada (prioriza tamaños grandes y normaliza a https)
    image_links = info.get("imageLinks") or {}
    portada_url = (
        image_links.get("extraLarge")
        or image_links.get("large")
        or image_links.get("medium")
        or image_links.get("thumbnail")
        or image_links.get("smallThumbnail")
        or ""
    )
    if portada_url.startswith("http://"):
        portada_url = "https://" + portada_url[len("http://"):]

    st.markdown("### 📤 DEBUG - Resultado final enviado a la app")
    st.json(resultado)

    return {
        "titulo": (info.get("title") or "").strip(),
        "autor": autores_str.strip(),
        "isbn": isbn_gb or (isbn or "").strip(),
        "editorial": (info.get("publisher") or "").strip(),
        "anio": int(str(info.get("publishedDate", "0"))[:4]) if info.get("publishedDate") else 0,
        "portada_url": portada_url,   # url de la imagen de portada de google books
        "descripcion": (info.get("description") or "").strip(),
    }
    

#********************************************************************************
#   IDENTIFICAR_LIBRO_POR_IMAGEN - Recibe una imagen en bytes y usa OpenAI para 
#                                  leer la portada.
#********************************************************************************
def identificar_libro_por_imagen(image_bytes: bytes):

    """
    1) Usa OpenAI para leer la portada.
    2) Usa Google Books para completar. la información.
    3) Devuelve (data, error) donde data es dict o None.
    """

    # 1️ - Extraer posibles datos desde la portada con IA
    
    ia_data = _call_openai_for_cover(image_bytes)
    if ia_data is None:
        return None, "No se pudo interpretar la portada con IA."

    titulo_ia = ia_data.get("titulo", "")
    autor_ia = ia_data.get("autor", "")
    isbn_ia = ia_data.get("isbn", "")

    # 2️ - Consulta Google Books con lo que tengamos
    gb_data = buscar_en_google_books(
        isbn=isbn_ia or None,
        titulo=titulo_ia or None,
        autor=autor_ia or None,
    )

    # 3️ - Combina información 
    combinado = {
        "titulo": "",
        "autor": "",
        "isbn": "",
        "editorial": "",
        "anio": 0,
        "portada_url": "",
        "descripcion": "",
    }

    # Título
    if gb_data and gb_data.get("titulo"):
        combinado["titulo"] = gb_data["titulo"]
    else:
        combinado["titulo"] = titulo_ia

    # Autor
    if gb_data and gb_data.get("autor"):
        combinado["autor"] = gb_data["autor"]
    else:
        combinado["autor"] = autor_ia

    # ISBN
    if gb_data and gb_data.get("isbn"):
        combinado["isbn"] = gb_data["isbn"]
    else:
        combinado["isbn"] = isbn_ia

    # Editorial y año solo vienen de Google Books
    if gb_data:
        combinado["editorial"] = gb_data.get("editorial", "")
        combinado["anio"] = gb_data.get("anio", 0)
        combinado["portada_url"] = gb_data.get("portada_url", "")
        combinado["descripcion"] = gb_data.get("descripcion", "")

    # 4️ - Validar si realmente identificamos un libro
    tiene_algo = any([
        combinado["titulo"],
        combinado["autor"],
        combinado["isbn"],
    ])

    if not tiene_algo:
        # Si la Información no es confiable → consideramos el libro como no identificado
        return None, "Libro no identificado. No se encontraron datos."

    return combinado, None
