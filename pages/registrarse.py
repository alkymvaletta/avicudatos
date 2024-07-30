import streamlit as st
import utilidades as util

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
        new_nombre = (st.text_input("Nombre", key="new_nombre", max_chars=30)).lower()
        new_apellido = (st.text_input("Apellido", key="new_apellido", max_chars=30)).lower()
        new_email = (st.text_input("Email", key="new_email", max_chars=30)).lower()
        new_username = (st.text_input("Nombre de Usuario", key="new_username", help='No se distinge entre mayúsculas y minúsculas')).upper()
        new_password = st.text_input("Contraseña", type="password", key="new_password", help='Debe tener al menos 8 caracteres')
        new_password_confi = st.text_input("Confirme Contraseña", type="password")
        
        btnRegistar = st.form_submit_button('Registrar', type='primary')
        
        if btnRegistar:
            errores = []

            if new_password != new_password_confi:
                errores.append('Las contraseñas no coinciden.')

            if len(new_nombre) == 0:
                errores.append('El nombre no puede estar vacío.')

            if len(new_apellido) == 0:
                errores.append('El apellido no puede estar vacío.')

            if len(new_password) < 8:
                errores.append('La clave debe tener al menos 8 caracteres.')

            if util.validador_email(new_email) == False:
                errores.append('El email ingresado no es válido.')

            if errores:
                for error in errores:
                    st.error(error, icon=':material/gpp_maybe:')
            else:
                if util.agregarUsuario(new_nombre, new_apellido, new_email, new_username, new_password):
                    st.success('**El usuario se ha registrado satisfactoriamente**')
                else:
                    st.error('**El usuario NO se pudo registrar**', icon=':material/warning:')

#test = st.text_input('Email de prueba')
#st.write(util.validador_email(test))