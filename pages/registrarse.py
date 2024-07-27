import streamlit as st
import utilidades as util
import login

#util.generarMenu()

HORIZONTAL = 'src\images\horizontal_logo.png'

st.logo(HORIZONTAL)

#st.set_page_config(page_title= 'Avicudatos - Inicio de Sesión', initial_sidebar_state= 'expanded')

st.header('Avicudatos 🐔', divider='rainbow')

st.title("Crear nuevo usuario")

if 'usuario' in st.session_state:
    util.generarMenu(st.session_state['usuario'])
else:
    util.generarMenu()
    
    with st.form('frmLogin'):
        st.subheader("Registro")
        new_nombre = st.text_input("Nombre", key="new_nombre")
        new_apellido = st.text_input("Apellido", key="new_apellido")
        new_email = st.text_input("Email", key="new_email")
        new_username = st.text_input("Nombre de Usuario", key="new_username")
        new_password = st.text_input("Contraseña", type="password", key="new_password")
        new_password_confi = st.text_input("Confirme Contraseña", type="password")
        btnRegistar = st.form_submit_button('Registrar', type='primary')
        if btnRegistar:
            if new_password != new_password_confi:
                st.error("Las contraseñas no coinciden.", icon=':material/gpp_maybe:')
            if login.agregarUsuario(new_nombre, new_apellido, new_email, new_username, new_password):
                st.session_state['usuario'] = ingUser
                #st.page_link('Home.py')
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.", icon=':material/gpp_maybe:')