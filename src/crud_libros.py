#********************************************************************************
#   LIBRERIAS
#********************************************************************************

import os
import sqlite3

# Cargamos automáticamente el archivo .env con las variables de entorno, para Streamlit Cloud se carga como una variable SECRETA
from dotenv import load_dotenv # type: ignore
load_dotenv()  

# BIBLIO_DB_PATH Tiene la ruta a la DB y esta en el archivo .env, si no la encuentra crea/usa biblioteca_db.db)
DB_PATH = os.getenv("BIBLIO_DB_PATH", "data/biblioteca_db.db")
print(DB_PATH)

#********************************************************************************
#   GET_CONNECTION - Conexión con la base de datos, si no existe la crea
#                    SQLite3 ya viene instalado por default
#********************************************************************************

def get_connection():
    print(DB_PATH)
    return sqlite3.connect(str(DB_PATH))

#********************************************************************************
#   INIT_DB - Crea la tabla Libros
#********************************************************************************

def init_db():
    print(DB_PATH)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS libros (
            isbn TEXT PRIMARY KEY,
            titulo TEXT NOT NULL,
            autor TEXT,
            anio INTEGER,
            editorial TEXT
        );
        """
    )
    conn.commit()
    conn.close()

#********************************************************************************
#   INSERTAR_LIBRO - Registra un nuevo libro
#********************************************************************************

def insertar_libro(isbn, titulo, autor, anio, editorial):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO libros (isbn, titulo, autor, anio, editorial) VALUES (?, ?, ?, ?, ?)",
            (isbn, titulo, autor, anio, editorial),
        )
        conn.commit()
        return True, "Libro registrado correctamente."
    except sqlite3.IntegrityError:
        return False, "Ya existe un libro con ese ISBN."
    finally:
        conn.close()

#********************************************************************************
#   BUSCAR_LIBRO - Busca un libro por ISBN
#********************************************************************************

def buscar_libro(isbn):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT isbn, titulo, autor, anio, editorial FROM libros WHERE isbn = ?",
        (isbn,),
    )
    libro = cursor.fetchone()
    conn.close()
    return libro

#********************************************************************************
#   ACTUALIZAR_LIBRO - Actualiza los datos de un libro por ISBN
#********************************************************************************

def actualizar_libro(isbn, titulo, autor, anio, editorial):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE libros
        SET titulo = ?, autor = ?, anio = ?, editorial = ?
        WHERE isbn = ?
        """,
        (titulo, autor, anio, editorial, isbn),
    )
    conn.commit()
    cambios = cursor.rowcount
    conn.close()
    if cambios == 0:
        return False, "No se encontró un libro con ese ISBN."
    return True, "Libro actualizado correctamente."

#********************************************************************************
#   ELIMINAR_LIBRO - Elimina un libro por ISBN
#********************************************************************************

def eliminar_libro(isbn):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM libros WHERE isbn = ?", (isbn,))
    conn.commit()
    cambios = cursor.rowcount
    conn.close()
    if cambios == 0:
        return False, "No se encontró un libro con ese ISBN."
    return True, "Libro eliminado correctamente."

#********************************************************************************
#   OBTENER_TODOS - Obtiene toda la colección de libros registrados
#********************************************************************************

def obtener_todos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT isbn, titulo, autor, anio, editorial FROM libros ORDER BY titulo ASC"
    )
    data = cursor.fetchall()
    conn.close()
    return data
