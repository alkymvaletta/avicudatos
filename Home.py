import streamlit as st
import streamlit_authenticator as stauth
from hash.hash_fun import encriptar_pass
from hash.hash_fun import verificar_pass

HORIZONTAL = 'src\images\horizontal_logo.png'
#HORIZONTAL = 'src\images\avicudatos.png'

st.logo(HORIZONTAL)

st.set_page_config(page_title='Inicio', page_icon='🐔', layout='centered')

st.header('Avicudatos 🐔', divider='rainbow')
st.subheader('Analizamos el rendimiento de tus aves')


test = st.text_input('Introduzca un texto para probar: ')
encriptado = encriptar_pass(test)
st.write(encriptado)

check = bytes(st.text_input('Test de contraseña: '), 'utf-8')

st.write(f'Es el pass igual {verificar_pass(check, encriptado)}')


# #test = test + 'Nhame+&*C0$74'
# test = test.encode('utf-8')

# hashed = bcrypt.hashpw(test, bcrypt.gensalt())

# st.write(hashed)

# x = st.text_input('Introduzca un HASH para probar: ')

# x_encode = x.encode('utf-8')

# resultado = bcrypt.checkpw(x_encode, hashed)

#st.write(resultado)


st.write('Aquí inicia mi tesis')
