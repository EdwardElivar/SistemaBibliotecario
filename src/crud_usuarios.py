#********************************************************************************
#   LIBRERIAS
#********************************************************************************

import os
import sqlite3
from datetime import datetime
import bcrypt   # type: ignore

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
    return sqlite3.connect(DB_PATH) # Usamos SQLITE3 para base de datos

#********************************************************************************
#   INIT_USERS_TABLE - Crea tabla Usuarios y un Admin por defecto
#********************************************************************************

def init_users_table():

    """Crea la tabla de usuarios si no existe"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    conn.commit()

    """Crea usuario admin por defecto si no hay usuarios"""
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    count = cursor.fetchone()[0]
    if count == 0:
        password = "admin123"
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, created_at) VALUES (?, ?, ?)",
            ("admin", password_hash.decode("utf-8"), datetime.utcnow().isoformat()),
        )
        conn.commit()

    conn.close()

#********************************************************************************
#   CREATE_USER - Crea Usuario en el sistema, modulo de Registro 
#********************************************************************************

def create_user(username: str, password: str):

    """Registra un nuevo usuario con password hasheado."""
    username = (username or "").strip().lower()
    password = (password or "").strip()

    if not username or not password:
        return False, "Usuario y contraseña son obligatorios."

    if len(username) < 3:
        return False, "El usuario debe tener al menos 3 caracteres."

    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."

    conn = get_connection()
    cursor = conn.cursor()

    # Verificar si ya existe el usuario que se esta intentando crear
    cursor.execute("SELECT 1 FROM usuarios WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "El usuario ya existe."

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    cursor.execute(
        "INSERT INTO usuarios (username, password_hash, created_at) VALUES (?, ?, ?)",
        (username, password_hash.decode("utf-8"), datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    return True, "Usuario registrado correctamente."

#********************************************************************************
#   VERIFY_USER - Verifica credenciales 
#********************************************************************************

def verify_user(username: str, password: str):

    """Valida credenciales contra la BD."""
    username = (username or "").strip().lower()
    password = (password or "").strip()

    if not username or not password:
        return False, "Usuario o contraseña incorrectos."

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash FROM usuarios WHERE username = ?", (username,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False, "Usuario o contraseña incorrectos."

    stored_hash = row[0].encode("utf-8")
    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        return True, "OK"

    return False, "Usuario o contraseña incorrectos."
