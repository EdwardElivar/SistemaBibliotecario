![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-red)
![License](https://img.shields.io/badge/license-MIT-green)

# 🌟 Sistema Bibliotecario con IA usando la API de OpenAI

## 📚 Índice
- [Datos de la versión](#datos-de-la-versión)
- [Descripción](#descripción)
- [Características principales](#características-principales)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Próximas mejoras](#próximas-mejoras)
- [Créditos y licencias](#créditos-y-licencias)
- [Demo en línea](#demo-en-línea)
- [Extras](#extras)


## Datos de la versión

- **Versión:** 1.0.
- **Autor:** Paul Edwar Muñoz Elivar.
- **Backend:** Python 3.
- **FrontEnd:** StreamLit.
- **Base de Datos:** SQLite3.
- **IA:** OpenAI GPT-4 Visión + Google Books API.

---

## Descripción

El **Sistema Bibliotecario Inteligente con IA** es una aplicación web desarrollada con **Streamlit** que permite:

- Registrarse y Autenticarse con usuarios registrados y mantener la sesión de manera segura.   
- Registrar, Actualizar, Borrar y Buscar Libros de manera manual, por medio del ISBN del libro, desde una interfaz moderna y sencilla.
- Escanear portadas de libros con la cámara de tu dispositivo.  
- Identificar automáticamente **título, autor, ISBN, año y editorial** usando **inteligencia artificial** por medio de OpenAI y Google Books.   

La aplicación combina visión artificial con procesamiento de lenguaje natural para asistir en la gestión de bibliotecas personales o institucionales.

---
## Características principales 

| Módulo | Descripción |
|--------|--------------|
| 🔑 **Login / Registro** | Permite crear usuarios y autenticarse con contraseña cifrada mediante `bcrypt`. |
| 📸 **Escaneo inteligente** | Usa la cámara para reconocer portadas de libros con IA y autocompletar los campos. |
| 📚 **Gestión de libros (CRUD)** | Registra, actualiza, elimina o busca libros por ISBN. |
| 🤖 **Integración con OpenAI** | Analiza la imagen para identificar texto, título y autor. |
| 🌐 **Google Books API** | Valida y completa los datos obtenidos por IA con información real de Google Books. |
| 💾 **Base de datos SQLite3** | Almacena usuarios y libros de forma local y ligera. |

---

## Tecnologías utilizadas

- **Python 3.10+**
- **Streamlit**
- **OpenAI Python SDK**
- **SQLite3**
- **bcrypt**
- **Requests**
- **Google Books API**

---

## Estructura del proyecto

```bash
SistemaBibliotecario/
│
├── src/
│   ├── streamlite_app.py          # Interfaz principal de la aplicación alojada en StreamLite Cloud
│   ├── crud_libros.py             # Operaciones CRUD de libros
│   ├── crud_usuarios.py           # Manejo de usuarios (login / registro)
│   ├── database.py                # Conexión con SQLite3
│   ├── external_services.py       # Integraciones con OpenAI y Google Books
│   ├── assets/
│   │   └── bookia.png             # Imagen del logo o robot IA
│   └── __init__.py
│
├── requirements.txt               # Dependencias del proyecto
├── README.md                      # Este archivo
└── .streamlit/
    └── secrets.toml               # Llaves privadas (solo en despliegue)
```
---

## Instalación y ejecución

---
## Próximas mejoras

- [ ] Agregar autenticación con Google.
- [ ] Implementar analítica de libros leídos por usuario.
- [ ] Exportar base de datos a formato CSV o Google Sheets.
- [ ] Optimizar rendimiento en Streamlit Cloud.

---

## Créditos y licencias

Desarrollado por **Paul Edwar Muñoz Elivar** como parte de un proyecto de IA aplicada.  
Licencia: [MIT License](LICENSE)

Si usas parte del código, por favor menciona la fuente o comparte mejoras mediante Pull Requests.

---

## Demo en línea

[Probar en Streamlit Cloud](https://sistembiblio3-4rgzt6tgddfsosc9fxpbgz.streamlit.app/)

---

## Extras 

- **OPENAI_API_KEY** = your_api_key_here
- **GOOGLE_BOOKS_API_KEY** = your_api_key_here



