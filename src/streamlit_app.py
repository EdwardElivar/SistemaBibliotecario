#********************************************************************************
#   LIBRERIAS
#********************************************************************************

import hashlib
import streamlit as st # type: ignore
from pathlib import Path
import sys

# Ruta absoluta a la raíz del proyecto (donde está config.py)
ROOT_DIR = Path(__file__).resolve().parent.parent

# Aseguramos que la raíz esté en sys.path
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import asset_path, DB_PATH


from crud_libros import (
    init_db,
    insertar_libro,
    buscar_libro,
    actualizar_libro,
    eliminar_libro,
    obtener_todos,
)
from crud_usuarios import (
    init_users_table,
    create_user,
    verify_user,
)
from external_services import identificar_libro_por_imagen


#********************************************************************************
#   ESTILOS
#********************************************************************************

def set_global_style():
    st.markdown(
        """
        <style>
        /* Fondo general */
        body {
            background: radial-gradient(circle at top, #111827, #020817);
            color: #e5e7eb;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", -system-ui, sans-serif;
        }

        /* Centrado del contenido principal */
        .block-container {
            padding-top: 3rem !important;
            padding-bottom: 3rem !important;
            max-width: 520px !important;
        }

        /* Títulos */
        h1, h2, h3 {
            color: #e5e7eb !important;
            font-weight: 600 !important;
        }

        /* Botones */
        .stButton>button {
            width: 100%;
            border-radius: 999px;
            padding: 0.7rem 1.2rem;
            border: none;
            font-weight: 600;
            background: linear-gradient(90deg, #22c55e, #16a34a);
            color: #020817;
            box-shadow: 0 10px 25px rgba(34,197,94,0.25);
            transition: all 0.18s ease-in-out;
        }
        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 14px 30px rgba(34,197,94,0.32);
            background: linear-gradient(90deg, #22c55e, #22c55e);
        }

        /* Inputs */
        .stTextInput>div>div>input,
        .stPasswordInput>div>div>input,
        .stNumberInput>div>div>input {
            background-color: #020817;
            border-radius: 12px;
            border: 1px solid #374151;
            padding: 0.55rem 0.75rem;
            color: #e5e7eb;
        }
        .stTextInput>div>div>input:focus,
        .stPasswordInput>div>div>input:focus,
        .stNumberInput>div>div>input:focus {
            border-color: #22c55e;
            box-shadow: 0 0 0 1px rgba(34,197,94,0.35);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.25rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.4rem 0.9rem;
            border-radius: 999px;
            background: rgba(15,23,42,0.9);
            color: #9ca3af;
            border: 1px solid transparent;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(34,197,94,0.1);
            color: #22c55e !important;
            border-color: #22c55e33;
        }

        /* Card del login */
        .login-card {
            width: 90%;
            max-width: 440px;
            margin: 0 auto 2rem auto; /* ⬅️ Aumenta el espacio inferior */
            background:
                radial-gradient(circle at top left, rgba(34,197,94,0.08), transparent),
                rgba(9,9,11,0.94);
            border-radius: 20px;
            padding: 2.8rem 1.2rem 2.3rem 1.2rem;
            min-height: 280px;
            box-shadow: 0 8px 30px rgba(15,23,42,0.75);
            border: 1px solid rgba(75,85,99,0.45);
            backdrop-filter: blur(12px);
        }


        .login-logo {
            font-size: 2.6rem;
            margin-bottom: 0.35rem;
        }
        .brand-title {
            font-size: 1.25rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            color: #e5e7eb;
        }
        .brand-subtitle {
            font-size: 0.82rem;
            color: #9ca3af;
        }

        .login-image {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-bottom: 1.2rem;
        }

        .ia-illustration {
            width: 120px;
            height: auto;
            filter: drop-shadow(0 4px 10px rgba(34,197,94,0.4));
            animation: float 3s ease-in-out infinite;
            border-radius: 16px;
        }

        /* Animación sutil de flotación */
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-6px); }
            100% { transform: translateY(0px); }
        }

        /* Ocultar sidebar cuando no hay sesión */
        .no-sidebar .css-1d391kg, .no-sidebar [data-testid="stSidebar"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ================== CONFIGURACIÓN STREAMLIT ==================

st.set_page_config(
    page_title="Sistema Bibliotecario IA",
    page_icon="📚",
    layout="centered",
)

set_global_style()

# Estado inicial
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None


# ================== AUTENTICACIÓN ==================

def pantalla_login():

    # Oculta la sidebar mientras no haya sesión
    st.markdown('<div class="no-sidebar"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div style="display:flex; flex-direction:column; align-items:center; gap:1.5rem; margin-bottom:1.5rem;">
            <div class="login-logo">📚✨</div>
            <div class="brand-title">Sistema Bibliotecario Inteligente</div>
            <div class="brand-subtitle">
                Gestiona, escanea y registra tus libros con ayuda de IA.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        #st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.image(str(asset_path("images", "bookia.png")))
        #st.image("/workspaces/SIstemaBiblio/assets/images/bookia.png")
        tab_login, tab_register = st.tabs(["Iniciar sesión", "Crear cuenta"])

        # -------- LOGIN ----------
        with tab_login:
            st.markdown("### Bienvenido de vuelta")
            st.caption("Ingresa con tu cuenta para administrar la biblioteca.")

            user = st.text_input("Usuario", key="login_user")
            pwd = st.text_input("Contraseña", type="password", key="login_pwd")

            col1, col2 = st.columns([3, 2])
            with col1:
                recordar = st.checkbox("Mantener sesión iniciada", value=True)
            with col2:
                st.write("")  # espacio

            if st.button("Ingresar", key="btn_login"):
                ok, msg = verify_user(user, pwd)
                if ok:
                    st.session_state.logged_in = True
                    st.session_state.username = (user or "").strip().lower()
                    st.success(f"Bienvenido, {st.session_state.username}")
                    st.rerun()
                else:
                    st.error(msg)

        # -------- REGISTRO ----------
        with tab_register:
            st.markdown("### Crear nueva cuenta")
            st.caption("Regístrate para usar el sistema. Tus credenciales se guardan de forma segura.")

            new_user = st.text_input("Nombre de usuario", key="reg_user")
            new_pwd = st.text_input("Contraseña", type="password", key="reg_pwd1")
            new_pwd2 = st.text_input(
                "Confirmar contraseña", type="password", key="reg_pwd2"
            )

            if st.button("Crear cuenta", key="btn_register"):
                if new_pwd != new_pwd2:
                    st.error("Las contraseñas no coinciden.")
                else:
                    ok, msg = create_user(new_user, new_pwd)
                    if ok:
                        st.success(
                            msg
                            + " Ahora puedes iniciar sesión en la pestaña 'Iniciar sesión'."
                        )
                    else:
                        st.error(msg)

        st.markdown("</div>", unsafe_allow_html=True)



def cerrar_sesion():
    st.session_state.logged_in = False
    st.session_state.username = None
    for k in [
        "edit_isbn",
        "edit_titulo",
        "edit_autor",
        "edit_anio",
        "edit_editorial",
        "scan_data",
        "scan_image_hash",
    ]:
        st.session_state.pop(k, None)
    st.success("Sesión cerrada.")
    st.rerun()


# ================== MENÚ PRINCIPAL ==================

def menu_principal():

    
    st.sidebar.title(f"Usuario: {st.session_state.username}")
    opcion = st.sidebar.selectbox(
        "Menú",
        (
            "Buscar libro por ISBN",
            "Registrar libro",
            "Actualizar libro por ISBN",
            "Eliminar libro por ISBN",
            "Ver todos los libros",
            "Escanear libro con cámara (IA)",
            "Cerrar sesión",
        ),
    )
   

    return opcion


# ================== VISTAS CRUD ==================

def vista_buscar():
    st.header("🔎 Buscar libro por ISBN")
    isbn = st.text_input("ISBN del libro")
    if st.button("Buscar"):
        if not isbn:
            st.warning("Ingresa un ISBN.")
        else:
            libro = buscar_libro(isbn.strip())
            if libro:
                st.success("Libro encontrado:")
                st.write(f"**ISBN:** {libro[0]}")
                st.write(f"**Título:** {libro[1]}")
                st.write(f"**Autor:** {libro[2]}")
                st.write(f"**Año:** {libro[3]}")
                st.write(f"**Editorial:** {libro[4]}")
            else:
                st.error("No se encontró un libro con ese ISBN.")


def vista_registrar():
    st.header("📕 Registrar nuevo libro")
    isbn = st.text_input("ISBN")
    titulo = st.text_input("Título")
    autor = st.text_input("Autor")
    anio = st.number_input("Año", min_value=0, max_value=9999, step=1)
    editorial = st.text_input("Editorial")

    if st.button("Guardar libro"):
        if not titulo.strip():
            st.warning("El título es obligatorio.")
        else:
            ok, msg = insertar_libro(
                isbn.strip(),
                titulo.strip(),
                autor.strip(),
                int(anio),
                editorial.strip(),
            )
            if ok:
                st.success(msg)
            else:
                st.error(msg)


def vista_actualizar():
    st.header("✏️ Actualizar libro por ISBN")
    isbn = st.text_input("ISBN del libro a actualizar")

    if st.button("Cargar datos"):
        if not isbn:
            st.warning("Ingresa un ISBN.")
        else:
            libro = buscar_libro(isbn.strip())
            if libro:
                st.session_state.edit_isbn = libro[0]
                st.session_state.edit_titulo = libro[1]
                st.session_state.edit_autor = libro[2]
                st.session_state.edit_anio = libro[3]
                st.session_state.edit_editorial = libro[4]
            else:
                st.error("No se encontró un libro con ese ISBN.")

    if "edit_isbn" in st.session_state:
        st.subheader(f"Editando libro ISBN: {st.session_state.edit_isbn}")

        nuevo_titulo = st.text_input(
            "Título",
            value=st.session_state.get("edit_titulo", ""),
            key="edit_titulo",
        )
        nuevo_autor = st.text_input(
            "Autor",
            value=st.session_state.get("edit_autor", ""),
            key="edit_autor",
        )
        anio_val = int(st.session_state.get("edit_anio", 0) or 0)
        nuevo_anio = st.number_input(
            "Año",
            min_value=0,
            max_value=9999,
            value=anio_val,
            step=1,
            key="edit_anio",
        )
        nuevo_editorial = st.text_input(
            "Editorial",
            value=st.session_state.get("edit_editorial", ""),
            key="edit_editorial",
        )

        if st.button("Actualizar libro"):
            ok, msg = actualizar_libro(
                st.session_state.edit_isbn,
                nuevo_titulo.strip(),
                nuevo_autor.strip(),
                int(nuevo_anio),
                nuevo_editorial.strip(),
            )
            if ok:
                st.success(msg)
                for k in [
                    "edit_isbn",
                    "edit_titulo",
                    "edit_autor",
                    "edit_anio",
                    "edit_editorial",
                ]:
                    st.session_state.pop(k, None)
            else:
                st.error(msg)


def vista_eliminar():
    st.header("🗑️ Eliminar libro por ISBN")
    isbn = st.text_input("ISBN del libro a eliminar")
    if st.button("Eliminar"):
        if not isbn:
            st.warning("Ingresa un ISBN.")
        else:
            ok, msg = eliminar_libro(isbn.strip())
            if ok:
                st.success(msg)
            else:
                st.error(msg)


def vista_todos():
    st.header("📚 Listado de todos los libros")
    data = obtener_todos()
    if not data:
        st.info("No hay libros registrados.")
    else:
        st.dataframe(
            {
                "ISBN": [d[0] for d in data],
                "Título": [d[1] for d in data],
                "Autor": [d[2] for d in data],
                "Año": [d[3] for d in data],
                "Editorial": [d[4] for d in data],
            },
            use_container_width=True
        )


# ================== VISTA: ESCANEAR LIBRO CON IA ==================

def vista_escanear_libro():
    import hashlib
    import streamlit as st  # type: ignore
    from crud_libros import insertar_libro
    from external_services import identificar_libro_por_imagen

    data, err = None, None

    # ===== Estilos globales de la vista =====
    st.markdown(
        """
        <style>
        /* ----- CONTENEDOR GENERAL ----- */
        .scan-wrapper {
            margin-top: 1.5rem;
            padding: 1px;
            border-radius: 26px;
            background: radial-gradient(circle at top, rgba(34,197,94,0.18), transparent);
        }
        .scan-card {
            position: relative;
            background: radial-gradient(circle at top left, rgba(15,23,42,0.98), #020817);
            border-radius: 24px;
            padding: 1.8rem 1.6rem 1.6rem 1.6rem;
            border: 1px solid rgba(56,189,248,0.14);
            box-shadow: 0 18px 65px rgba(15,23,42,0.95);
            overflow: hidden;
        }

        /* ----- TÍTULOS ----- */
        .scan-title {
            font-size: 1.35rem;
            font-weight: 600;
            color: #e5e7eb;
            margin: 0;
        }
        .scan-subtitle {
            font-size: 0.82rem;
            color: #9ca3af;
            margin-top: 0.15rem;
        }

        /* ----- BADGE "Módulo Vision-IA activo" ----- */
        .scan-badge-wrap {
            display:flex;
            justify-content:center;
            width:100%;
            margin-bottom:0.4rem;
        }
        .scan-badge {
            display:flex;
            align-items:center;
            gap:0.35rem;
            padding:0.25rem 0.9rem;
            border-radius:999px;
            font-size:0.75rem;
            color:#22c55e;
            border:1px solid rgba(34,197,94,0.6);
            background:radial-gradient(circle at top, rgba(34,197,94,0.18), rgba(2,6,23,0.98));
            box-shadow:0 0 16px rgba(34,197,94,0.35);
        }

        .scan-divider {
            height:1px;
            background:linear-gradient(to right,
                transparent,
                rgba(148,163,253,0.16),
                rgba(34,197,94,0.55),
                rgba(56,189,248,0.18),
                transparent);
            margin:0.9rem 0 1.1rem 0;
        }

        /* ----- OVERLAY FUTURISTA SOBRE LA CÁMARA ----- */
        .scan-cam-wrapper {
            position: relative;
            margin-top: 0.2rem;
        }
        .full-scan-overlay {
            position: relative;
            margin-top: -440px; /* superpone sobre la cámara */
            height: 400px;      /* ajusta según tu cámara */
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            pointer-events: none; /* no bloquea clics */
        }
        .laser-line {
            position: absolute;
            width: 90%;
            height: 3px;
            background: linear-gradient(90deg,
                rgba(34,197,94,0),
                rgba(34,197,94,1),
                rgba(56,189,248,0.9),
                rgba(34,197,94,0)
            );
            box-shadow: 0 0 20px rgba(34,197,94,0.9);
            border-radius: 999px;
            animation: vertical-scan 3s linear infinite;
        }
        @keyframes vertical-scan {
            0%   { transform: translateY(-110px); opacity: 0; }
            10%  { opacity: 1; }
            50%  { transform: translateY(110px); opacity: 1; }
            90%  { opacity: 1; }
            100% { transform: translateY(-110px); opacity: 0; }
        }

        /* ----- BOTONES CENTRADOS ----- */
        .scan-center-btn {
            display:flex;
            justify-content:center;
            align-items:center;
            width:100%;
            margin-top:1.5rem;
            margin-bottom:0.5rem;
        }
        .scan-center-btn .stButton>button {
            width: 50%;
            border-radius: 999px;
            padding: 0.9rem 1.4rem;
            font-size: 1.05rem;
            font-weight: 600;
            color: #020817;
            background: linear-gradient(90deg,#22c55e,#16a34a);
            box-shadow: 0 0 25px rgba(34,197,94,0.5);
            border: none;
            transition: all 0.25s ease-in-out;
        }
        .scan-center-btn .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow: 0 0 35px rgba(34,197,94,0.85);
        }

        /* ----- TARJETA DE DATOS DETECTADOS ----- */
        .data-card {
            background: radial-gradient(circle at top, rgba(15,23,42,0.98), rgba(2,6,23,1));
            border-radius: 18px;
            padding: 1rem 1.1rem 0.9rem 1.1rem;
            border: 1px solid rgba(34,197,94,0.22);
            margin-top: 1.2rem;
        }
        .data-card h3 {
            margin: 0 0 0.45rem 0;
            font-size: 1rem;
            color: #22c55e;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ===== ENCABEZADO =====
    st.markdown(
        """
        <div style='text-align:center; margin-top:1rem;'>
            <h2 style='color:#22c55e; text-shadow:0 0 15px rgba(34,197,94,0.7); margin-bottom:0.1rem;'>
                Escáner Inteligente de Libros
            </h2>
            <p style='color:#9ca3af; font-size:0.9rem; margin:0;'>
                Captura una foto de la portada y deja que la IA intente identificar el libro automáticamente.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ===== VARIABLES DE SESIÓN =====
    if "scan_data" not in st.session_state:
        st.session_state.scan_data = None
    if "scan_image_hash" not in st.session_state:
        st.session_state.scan_image_hash = None
    if "scan_guardado_ok" not in st.session_state:
        st.session_state.scan_guardado_ok = False

    # contador para resetear la cámara creando una nueva key cuando se necesite
    if "camera_counter" not in st.session_state:
        st.session_state.camera_counter = 0

    # Mensaje de éxito persistente después de guardar
    if st.session_state.scan_guardado_ok:
        st.success("📚 Libro guardado correctamente en tu biblioteca.")
        # Lo apagamos para que no se quede para siempre
        st.session_state.scan_guardado_ok = False


    # ===== CÁMARA + OVERLAY =====
    st.markdown("<div class='scan-cam-wrapper'>", unsafe_allow_html=True)

    camera_key = f"cam_portada_{st.session_state.camera_counter}"
    img = st.camera_input("Captura la portada del libro", key=camera_key)

    st.markdown(
        """
        <div class="full-scan-overlay">
            <div class="laser-line"></div>
        </div>
        </div> <!-- cierre scan-cam-wrapper -->
        """,
        unsafe_allow_html=True,
    )

    # Si cambia la imagen, limpiar datos previos
    if img is not None:
        new_hash = hashlib.md5(img.getvalue()).hexdigest()
        if new_hash != st.session_state.scan_image_hash:
            st.session_state.scan_image_hash = new_hash
            st.session_state.scan_data = None

    # ===== BOTÓN IDENTIFICAR CON IA =====
    scan_clicked = False
    if img is not None:
        st.markdown("<div class='scan-center-btn'>", unsafe_allow_html=True)
        scan_clicked = st.button("🔍 Identificar libro con OpenAI", key="btn_identificar_ia")
        st.markdown("</div>", unsafe_allow_html=True)

    # ===== PROCESO DE ESCANEO =====
    if img is not None and scan_clicked:
        with st.spinner("🤖 Analizando portada con IA..."):
            data, error = identificar_libro_por_imagen(img.getvalue())

        if error:
            st.error(error)
            st.session_state.scan_data = None

        elif not data or not isinstance(data, dict):
            st.warning("📕 Libro no identificado. Intenta tomar una foto más cercana y con buena iluminación.")
            st.session_state.scan_data = None

        else:
            # Normalizar campos
            titulo = (data.get("titulo") or "").strip()
            autor = (data.get("autor") or "").strip()
            isbn = (data.get("isbn") or "").strip()
            editorial = (data.get("editorial") or "").strip()
            try:
                anio_val = int(data.get("anio") or 0)
            except Exception:
                anio_val = 0

            hay_algo = any([titulo, autor, isbn, editorial, anio_val])

            score = 0
            if titulo:
                score += 1
            if autor:
                score += 1
            if isbn:
                score += 1

            if not hay_algo:
                st.warning(
                    "📕 Libro no identificado. No se detectaron datos confiables en la imagen.\n"
                    "Asegúrate de que la portada sea legible y ocupe la mayor parte de la foto."
                )
                st.session_state.scan_data = None
            else:
                # 👉 Guardamos también portada y descripción
                st.session_state.scan_data = {
                    "titulo": titulo,
                    "autor": autor,
                    "isbn": isbn,
                    "editorial": editorial,
                    "anio": anio_val,
                    "portada_url": (data.get("portada_url") or "").strip(),
                    "descripcion": (data.get("descripcion") or "").strip(),
                }

                if score >= 2 or (isbn and (titulo or autor)):
                    st.success("✨ Libro identificado. Revisa y ajusta los datos antes de guardar, solo si es necesario")
                else:
                    st.info(
                        "⚠️ Se detectaron datos parciales de la portada. "
                        "Completa la información faltante antes de guardar."
                    )

    # ===== DATOS DETECTADOS =====
    if st.session_state.scan_data:
        d = st.session_state.scan_data

        st.markdown("<div class='data-card'>", unsafe_allow_html=True)
        st.markdown("<h3>📘 Datos detectados / editables</h3>", unsafe_allow_html=True)

        isbn = st.text_input("ISBN", d.get("isbn", ""), key="scan_isbn")
        titulo = st.text_input("Título", d.get("titulo", ""), key="scan_titulo")
        autor = st.text_input("Autor", d.get("autor", ""), key="scan_autor")

        try:
            anio_val = int(d.get("anio") or 0)
        except Exception:
            anio_val = 0

        anio = st.number_input(
            "Año de publicación",
            min_value=0,
            max_value=9999,
            value=anio_val,
            key="scan_anio",
        )
        editorial = st.text_input("Editorial", d.get("editorial", ""), key="scan_editorial")

        st.markdown("</div>", unsafe_allow_html=True)

        # =============================================================
        # CARD PORTADA + DESCRIPCIÓN (primeros 350 caracteres)
        # =============================================================
        portada = d.get("portada_url")
        descripcion = (d.get("descripcion") or "").strip()

        if portada or descripcion:
            st.markdown(
                """
                <style>
                    .book-card {
                        background: radial-gradient(circle at top left, rgba(15,23,42,0.98), #020617);
                        border-radius: 20px;
                        padding: 1.3rem 1.4rem;
                        border: 1px solid rgba(56,189,248,0.35);
                        box-shadow: 0 18px 55px rgba(15,23,42,0.85);
                        margin-top: 1.6rem;
                        transition: all 0.25s ease-out;
                    }
                    .book-card:hover {
                        transform: translateY(-3px) scale(1.01);
                        box-shadow: 0 24px 70px rgba(56,189,248,0.55);
                        border-color: rgba(34,197,94,0.7);
                    }
                    .desc-text {
                        text-align: justify;
                        color: #e5e7eb;
                        line-height: 1.6;
                        font-size: 0.95rem;
                        margin-top: 0.3rem;
                    }
                    .desc-header {
                        font-size: 1rem;
                        font-weight: 600;
                        color: #a5b4fc;
                        margin-bottom: 0.4rem;
                        text-shadow: 0 0 12px rgba(129,140,248,0.45);
                    }
                </style>
                """,
                unsafe_allow_html=True,
            )

            #st.markdown("<div class='book-card'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 2])

            with col1:
                if portada:
                    st.image(portada, caption="Portada del libro")

            with col2:
                if descripcion:
                    resumen = descripcion[:350] + ("..." if len(descripcion) > 350 else "")
                    st.markdown("<div class='desc-header'>Descripción</div>", unsafe_allow_html=True)
                    st.markdown(f"<p class='desc-text'>{resumen}</p>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
        # =============================================================

        # ===== BOTÓN GUARDAR =====
        st.markdown("<div class='scan-center-btn'>", unsafe_allow_html=True)
        if st.button("💾 Guardar libro en biblioteca", key="btn_guardar_libro"):
            if not titulo.strip():
                st.warning("El título es obligatorio.")
            else:
                ok, msg = insertar_libro(
                    isbn.strip(),
                    titulo.strip(),
                    autor.strip(),
                    int(anio),
                    editorial.strip(),
                )
                if ok:

                    # después de guardar correctamente:
                    st.session_state.scan_guardado_ok = True
                    st.session_state.scan_data = None
                    st.session_state.scan_image_hash = None

                    # incrementamos el contador para "resetear" la cámara (nueva key => widget vacío)
                    st.session_state.camera_counter += 1

                else:
                    st.error(msg)
        st.markdown("</div>", unsafe_allow_html=True)


    # ===== CIERRE CONTENEDORES =====
    st.markdown("</div></div>", unsafe_allow_html=True)







# ================== INICIALIZACIÓN Y FLUJO PRINCIPAL ==================

# Crear tablas necesarias (libros + usuarios, con admin por defecto)
init_db()
init_users_table()

if not st.session_state.logged_in:
    pantalla_login()
else:

    opcion = menu_principal()

    if opcion == "Buscar libro por ISBN":
        vista_buscar()
    elif opcion == "Registrar libro":
        vista_registrar()
    elif opcion == "Actualizar libro por ISBN":
        vista_actualizar()
    elif opcion == "Eliminar libro por ISBN":
        vista_eliminar()
    elif opcion == "Ver todos los libros":
        vista_todos()
    elif opcion == "Escanear libro con cámara (IA)":
        vista_escanear_libro()
    elif opcion == "Cerrar sesión":
        cerrar_sesion()
