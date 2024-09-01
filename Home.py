import streamlit as st
#import streamlit_authenticator as stauth
import utilidades as util
#from streamlit_cookies_controller import CookieController


st.set_page_config(page_title='Avicudatos - Inicio', page_icon='🐔')   

# Se agrega logo
HORIZONTAL = 'src\images\horizontal_logo.png'

st.logo(HORIZONTAL)

st.header('Avicudatos 🐔', divider='rainbow')

if 'usuario' in st.session_state:
    
    usuario = st.session_state['usuario']
    
    util.generarMenu(usuario)
    
    #controller = CookieController()
    
    st.subheader(f'Analizando el rendimiento de las aves de :red[{usuario}]')

    #Genera este texto si el usuario inició sesión
    st.markdown('''
            Bienvenido a :red[AVICUDATOS], la plataforma innovadora diseñada para transformar la avicultura de pollos de engorde. 
            Aquí, evaluamos meticulosamente el desempeño de sus granjas, proporcionando una visión detallada de cada galpón y camada. 
            Con AVICUDATOS, no solo podrá ingresar y gestionar sus operaciones avícolas con facilidad, sino que también tendrá acceso 
            a análisis de rendimiento en tiempo real, comparativas de rentabilidad y mediciones precisas frente a los datos de referencia 
            de la industria. Todo esto, adaptado a las diversas razas de pollos, asegurando que reciba información personalizada y 
            relevante para maximizar su éxito. 
            \n¡Descubra cómo AVICUDATOS puede elevar su producción avícola al próximo nivel!
            ''')
    
    
    
    # Se genera este texto y menús si el usuario no ha iniciado sesión
else:
    util.generarMenu()
    
    st.subheader(f'Analizamos el rendimiento de tus aves')
    
    st.markdown('''
            Bienvenido a :red[AVICUDATOS], la plataforma innovadora diseñada para transformar la avicultura de pollos de engorde. 
            Aquí, evaluamos meticulosamente el desempeño de sus granjas, proporcionando una visión detallada de cada galpón y camada. 
            Con AVICUDATOS, no solo podrá ingresar y gestionar sus operaciones avícolas con facilidad, sino que también tendrá acceso 
            a análisis de rendimiento en tiempo real, comparativas de rentabilidad y mediciones precisas frente a los datos de referencia 
            de la industria. Todo esto, adaptado a las diversas razas de pollos, asegurando que reciba información personalizada y 
            relevante para maximizar su éxito. 
            \n¡Descubra cómo AVICUDATOS puede elevar su producción avícola al próximo nivel!
            ''')
    
    st.write('**Aún no te haz registrado o no haz iniciado sesión**')