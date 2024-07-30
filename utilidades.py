import streamlit as st
import psycopg2
import bcrypt
import re
from psycopg2 import errors
from datetime import date

def generarMenu(usuario = None):
    with st.sidebar:
        if usuario == None:
            st.write(f'**Bienvenido avicultor**')
            st.page_link('Home.py', label= 'Inicio', icon= ':material/home:')
            st.subheader('Iniciar sesión o Registrarse')
            st.page_link('pages/iniciar_sesion.py', label= 'Inicia sesión', icon= ':material/login:')
            st.page_link('pages/registrarse.py', label= 'Crea una cuenta', icon=':material/person_add:')
        else:
            st.write(f'Bienvenido, **{usuario}**')
            st.page_link('Home.py', label= 'Inicio', icon= ':material/home:')
            st.subheader('Gestiona tu granja')
            st.page_link('pages/granja.py', label='Tu granja', icon=':material/agriculture:')
            st.page_link('pages/camada.py', label='Tus camadas', icon=':material/gite:')
            st.page_link('pages/faenas.py', label='Faenas', icon=':material/food_bank:')
            st.subheader('Vende tu producto')
            st.page_link('pages/ventas.py', label='Ventas', icon=':material/payments:')
            st.subheader('Evalúa tu desempeño')
            st.page_link('pages/estadistica.py', label='Analíticas', icon=':material/analytics:')
            btnSalir=st.button("Cerrar Sesión")
            if btnSalir:
                st.session_state.clear() # Se borra el session_state
                st.page_link('Home.py')
                st.rerun()


def validador_email(email):
    if re.search(r'[\w.]+\@[\w.]+\.+[\w.]', email):
        return True
    else:
        return False

def agregarUsuario(nombre, apellido, email, username, password):
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
        st.error("El email ingresado ya ya se encuentra registrado", icon=':material/gpp_maybe:')
        return False
    except Exception as e:
        conn.close()
        st.error(f"Error al agregar usuario a la base de datos: {e}")
        return False



def validarUsuario(username, password):
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

# def conectarDB():
#     db_config = st.secrets['database']
#     conn = psycopg2.connect(
#         host = db_config['host'],
#         port=db_config['port'],
#         database=db_config['database'],
#         user=db_config['username'],
#         password=db_config['password']
#     )
    