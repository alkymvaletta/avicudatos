import streamlit as st
import utilidades as util
from psycopg2 import sql


# Se agrega logo
HORIZONTAL = 'src\images\horizontal_logo.png'

st.set_page_config(page_title= 'Avicudatos - Granjas y galpones', page_icon='🐔')

st.logo(HORIZONTAL)

util.generarMenu(st.session_state['usuario'])

#Configuración de Pagina
#st.set_page_config(page_title="Avicudatos - Granja", page_icon="🏠", layout='centered')
st.title("Granja y galpones")
st.sidebar.header("Mi Granja")

st.write(
    """Integramos los datos de para que gestiones tus granjas y los galpones que tengas para cada uno de estas""")

## Sección que muestra las granjas del Usuario y los galpones de cada uno

st.header('Tus granjas')

st.write('Agrega o elimina granjas y galpones de acuerdo a tus necesidades')

st.write('Aqui van las granjas activas ')


    

## Se hace check box para gestionar las granjas

if st.checkbox('**Gestionar**'):
    
    # Se abre la opción para agregar granjas 
    if st.checkbox('**Agregar granjas**'):
        st.write('Se muestran las granjas')
        
        
    # Se abre la opción para agregar galpones
    if st.checkbox('**Agregar galpones**'):
        st.write('Se muestran los galpones ')