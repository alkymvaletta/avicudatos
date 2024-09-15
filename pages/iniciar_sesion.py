import streamlit as st
import utilidades as util

HORIZONTAL = 'src\images\\avicudatos_sin_fondo.png'

st.logo(HORIZONTAL)

st.set_page_config(page_title= 'Avicudatos - Inicio de Sesión', page_icon='🐔')

st.header('Avicudatos 🐔', divider='rainbow')

st.title("Inicio de Sesión")
if 'usuario' in st.session_state:
    util.generarMenu(st.session_state['usuario'])
else:
    util.generarMenu()
    with st.form('frmLogin'):
        ingUser = (st.text_input('Usuario:')).upper()
        ingPassword = st.text_input('Contraseña:', type='password')
        btnLogin = st.form_submit_button('Ingresar', type='primary')
        
        if btnLogin:
            resultado = util.validarUsuario(ingUser,ingPassword)
            if resultado['success']:
                st.session_state['usuario'] = ingUser
                st.session_state['id_usuario'] = resultado['id']
                st.switch_page('Home.py')
            else:
                st.error("Usuario o contraseña incorrectos.", icon=':material/gpp_maybe:')