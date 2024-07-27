import streamlit as st
import psycopg2

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


# def conectarDB():
#     db_config = st.secrets['database']
#     conn = psycopg2.connect(
#         host = db_config['host'],
#         port=db_config['port'],
#         database=db_config['database'],
#         user=db_config['username'],
#         password=db_config['password']
#     )
    