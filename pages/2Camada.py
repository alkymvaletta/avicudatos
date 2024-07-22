import streamlit as st
import sqlalchemy
import psycopg2
from psycopg2 import sql
from PIL import Image
import os
import secrets

# Se agrega logo
HORIZONTAL = 'src\images\horizontal_logo.png'

st.logo(HORIZONTAL)

# Configuración de la página
st.set_page_config(page_title="Avicudatos - Camadas", page_icon="🐣")
st.title("Camadas")

# Configuración de la conexión con la base de datos
conn = st.connection('postgresql', type='sql')

# Se configura el sidebar 
st.sidebar.header("Camadas")
cant_camadas_activas = 2 #Esto es un test
st.sidebar.write(f'Actualmente tienes {cant_camadas_activas} camadas activas y aquí las puedes gestionar :point_right:')

# Se configura el texto de la página principal
st.write(
    """Gestiona tus camadas, registra sus consumos, medicaciones, los pesajes, la mortalidad, 
        los descartes que se presenten y los costos asociados a la camada""")

st.subheader('Tus camadas activas')

st.write('Aqui va el DF con la lista de camadas activas')

st.subheader('Gestiona las necesidades de la camada')


### Se agregan la gestión de consumibles 
if st.checkbox('**Consumibles**'):
    
    st.write('Registra aquí el consumo de alimento, agua o grit que se le suministre a la camada')
    
    # Se agrega la gestión de los alimentos de la camada
    if st.checkbox('Alimento'):
        st.write('Aqui se gestiona el alimento')
    
    # Se agrega la gestión del consumo de agua de la camada
    if st.checkbox('Agua'):
        st.write('Aqui se gestiona el agua')
    
    # Se agrega la gestión de suministro del Grit a la camada
    if st.checkbox('Grit'):
        st.write('Resgistra aquí el suministro de piedrecillas que el ave debe consumir para ayudar en la digestión del alimento')

if st.checkbox('**Medicamentos**'):
    st.write('Registra los medicamentos')

### Se agrega la gestión de la mortalidad
if st.checkbox('**Mortalidad y descarte**'):
    
    # Se agrega la gestión de la mortalidad de los pollos en la camada
    if st.checkbox('Mortalidad'):
        st.write('Aqui se registraría las muertes')
    
    # Se agrega la gestión de la descarte de los pollos en la camada
    if st.checkbox('Descartes'):
        st.write('Aqui se registraría las muertes')

## Se agrega la gestión de los pesajes de los pollos de la camada
if st.checkbox('**Pesajes**'):
    st.write('Aqui se gestiona el alimento')

## Se agrega la gestión de los costos relacionados con la camada
if st.checkbox('**Costos**'):
    st.write('Aqui se gestiona el alimento')