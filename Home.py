import streamlit as st
import streamlit_authenticator as stauth
import utilidades as util
from hash.hash_fun import encriptar_pass
from hash.hash_fun import verificar_pass

util.generarMenu()

# Se agrega logo
HORIZONTAL = 'src\images\horizontal_logo.png'

st.logo(HORIZONTAL)

#st.set_page_config(page_title='Avicudatos - Inicio', page_icon='🐔', layout='centered')

st.header('Avicudatos 🐔', divider='rainbow')
st.subheader('Analizamos el rendimiento de tus aves')

st.markdown('''
        Bienvenido a :red[AVICUDATOS], la plataforma innovadora diseñada para transformar la avicultura de pollos de engorde. 
        Aquí, evaluamos meticulosamente el desempeño de sus granjas, proporcionando una visión detallada de cada galpón y camada. 
        Con AVICUDATOS, no solo podrá ingresar y gestionar sus operaciones avícolas con facilidad, sino que también tendrá acceso 
        a análisis de rendimiento en tiempo real, comparativas de rentabilidad y mediciones precisas frente a los datos de referencia 
        de la industria. Todo esto, adaptado a las diversas razas de pollos, asegurando que reciba información personalizada y 
        relevante para maximizar su éxito. 
        \n¡Descubra cómo AVICUDATOS puede elevar su producción avícola al próximo nivel!
         ''')

test = st.text_input('Introduzca un texto para probar: ')
encriptado = encriptar_pass(test)
st.write(encriptado)

check = bytes(st.text_input('Test de contraseña: '), 'utf-8')

st.write(f'Es el pass igual {verificar_pass(check, encriptado)}')

st.page_link('pages/login.py', label= 'Iniciar Sesión', icon=':material/login:')


# #test = test + 'Nhame+&*C0$74'
# test = test.encode('utf-8')

# hashed = bcrypt.hashpw(test, bcrypt.gensalt())

# st.write(hashed)

# x = st.text_input('Introduzca un HASH para probar: ')

# x_encode = x.encode('utf-8')

# resultado = bcrypt.checkpw(x_encode, hashed)

#st.write(resultado)


st.write('Aquí inicia mi tesis')
