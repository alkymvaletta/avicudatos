from pathlib import Path
import json
import streamlit as st
import bcrypt
import sqlalchemy as sa
import psycopg2
from psycopg2 import sql, errors
from streamlit.source_util import _on_pages_changed, get_pages
from datetime import date

st.set_page_config(page_title='Avicudatos - Inicio', page_icon='🐔', layout='centered')


DEFAULT_PAGE = "Home.py"


def add_user_to_db(nombre, apellido, email, username, password):
    db_config = st.secrets['database']
    conn = psycopg2.connect(
        host = db_config['host'],
        port=db_config['port'],
        database=db_config['database'],
        user=db_config['username'],
        password=db_config['password']
    )
    try:
        c = conn.cursor()
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        fecha_union = date.today()
        c.execute('''
            INSERT INTO usuario (nombre, apellido, email, username, password, fecha_union) 
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (nombre, apellido, email, username, hashed_password, fecha_union))
        conn.commit()
        conn.close()
        return True
    except errors.UniqueViolation:
        conn.rollback()
        conn.close()
        st.error("El nombre de usuario o email ya existe. Por favor, elija otro.")
        return False
    except Exception as e:
        conn.close()
        st.error(f"Error al agregar usuario a la base de datos: {e}")
        return False



def authenticate_user_in_db(username, password):
    db_config = st.secrets['database']
    conn = psycopg2.connect(
        host = db_config['host'],
        port=db_config['port'],
        database=db_config['database'],
        user=db_config['username'],
        password=db_config['password']
    )
    try:
        c = conn.cursor()
        c.execute('SELECT password FROM usuario WHERE username = %s', (username,))
        result = c.fetchone()
        if result and bcrypt.checkpw(password.encode('utf-8'), bytes(result[0])):
            c.execute('UPDATE usuario SET ultimo_login = %s WHERE username = %s', (date.today(), username))
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False
    except Exception as e:
        conn.close()
        st.error(f"Error al autenticar usuario: {e}")
        return False


def get_all_pages():
    default_pages = get_pages(DEFAULT_PAGE)
    pages_path = Path("pages.json")
    if pages_path.exists():
        saved_default_pages = json.loads(pages_path.read_text())
    else:
        saved_default_pages = default_pages.copy()
        pages_path.write_text(json.dumps(default_pages, indent=4))

    return saved_default_pages

def clear_all_but_first_page():
    current_pages = get_pages(DEFAULT_PAGE)

    if len(current_pages.keys()) == 1:
        return

    get_all_pages()

    key, val = list(current_pages.items())[0]
    current_pages.clear()
    current_pages[key] = val

    _on_pages_changed.send()

def show_all_pages():
    current_pages = get_pages(DEFAULT_PAGE)
    saved_pages = get_all_pages()
    missing_keys = set(saved_pages.keys()) - set(current_pages.keys())

    for key in missing_keys:
        current_pages[key] = saved_pages[key]

    _on_pages_changed.send()
    

HORIZONTAL = 'src\images\horizontal_logo.png'

st.logo(HORIZONTAL)

st.header('Avicudatos 🐔', divider='rainbow')
st.subheader('Analizamos el rendimiento de tus aves')

# Gestión del estado de la sesión
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'authenticated_username' not in st.session_state:
    st.session_state.authenticated_username = None

clear_all_but_first_page()

#st.title("Página de Inicio de Sesión")

if not st.session_state.logged_in:
    

    # Autenticación de usuarios existentes
    st.subheader("Inicio de Sesión")
    login_username = st.text_input("Nombre de Usuario", key="login_username")
    login_password = st.text_input("Contraseña", type="password", key="login_password")
    if st.button("Iniciar Sesión"):
        if authenticate_user_in_db(login_username, login_password):
            st.session_state.logged_in = True
            st.session_state.authenticated_username = login_username
            show_all_pages()
            st.success(f"Inicio de sesión exitoso! Bienvenido {login_username}")
        else:
            st.error("Nombre de usuario o contraseña incorrectos.")
            clear_all_but_first_page()
    st.subheader("Aún no eres usuario")
    if st.button('Registrarse'):
        st.write('Crea el usuario')
    
    # Registro de nuevos usuarios
    st.subheader("Registro")
    new_nombre = st.text_input("Nombre", key="new_nombre")
    new_apellido = st.text_input("Apellido", key="new_apellido")
    new_email = st.text_input("Email", key="new_email")
    new_username = st.text_input("Nombre de Usuario", key="new_username")
    new_password = st.text_input("Contraseña", type="password", key="new_password")
    new_password_confi = st.text_input("Confirme Contraseña", type="password")
    
    #Verificación de contraseña
    if new_password != new_password_confi:
        st.warning('Contraseñas no coindicen', icon=':material/warning:')
    else:
        if st.button("Registrar"):
            if new_nombre and new_apellido and new_email and new_username and new_password:
                if add_user_to_db(new_nombre, new_apellido, new_email, new_username, new_password):
                    st.success("Usuario registrado exitosamente!")
            else:
                st.error("Por favor, complete todos los campos.")
else:
    st.success(f"Bienvenido {st.session_state.authenticated_username}!")
    st.markdown("¡Aquí comienza tu nuevo reto Bienvenid@ a avicuidatos!")
    st.subheader("Contenido exclusivo para usuarios autenticados")
    

    # Ejemplo de sección oculta
    st.write("Esta sección es visible solo para usuarios autenticados.")

    # Opción para cerrar sesión
    if st.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.session_state.authenticated_username = None
        st.success("Has cerrado sesión exitosamente.")
        clear_all_but_first_page()
        st.rerun()
