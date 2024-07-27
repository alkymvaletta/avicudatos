import streamlit as st
import utilidades as util
import login

#util.generarMenu()

HORIZONTAL = 'src\images\horizontal_logo.png'

st.logo(HORIZONTAL)

#st.set_page_config(page_title= 'Avicudatos - Inicio de Sesión', initial_sidebar_state= 'expanded')

st.header('Avicudatos 🐔', divider='rainbow')

st.title("Inicio de Sesión")
if 'usuario' in st.session_state:
    util.generarMenu(st.session_state['usuario'])
else:
    util.generarMenu()
    with st.form('frmLogin'):
        ingUser = st.text_input('Usuario:')
        ingPassword = st.text_input('Contraseña:', type='password')
        btnLogin = st.form_submit_button('Ingresar', type='primary')
        if btnLogin:
            if login.validarUsuario(ingUser,ingPassword):
                st.session_state['usuario'] = ingUser
                #st.page_link('Home.py')
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.", icon=':material/gpp_maybe:')