import streamlit as st
import utilidades as util
import pandas as pd
from datetime import datetime
from psycopg2 import sql

st.set_page_config(page_title="Avicudatos - Faena", page_icon='🐔')

# Se agrega logo
HORIZONTAL = 'src\images\\avicudatos_sin_fondo.png'

st.logo(HORIZONTAL)

st.header('Avicudatos 🐔', divider='rainbow')

#Si no hay usuario registrado se va a Home
if 'usuario' not in st.session_state:
    st.switch_page('Home.py')

util.generarMenu(st.session_state['usuario'])
# Configuration of the page

st.title("Sacrifica tus camadas ")

user_id = st.session_state['id_usuario']

st.write(
    """Registra las faenas que realices a tus camadas, tendrás más control de tus rendimientos🐓""")

st.subheader('Camadas que puedes sacrificar')

#Consulta las granjas y galpones
df_granjas, df_galpones = util.listaGranjaGalpones(user_id)

#Consultamos las camadas
with st.container():
    df_camadas = util.consultarCamadasActiva(user_id)
    df_camadas_merged = pd.merge(df_camadas, df_galpones, how='left', left_on='galpon_id', right_on='galpon_id')
    df_camadas_merged = df_camadas_merged.rename(columns={'cantidad':'Ingresados', 'fecha_inicio':'Fecha ingreso', 'fecha_estimada_sacrificio':'Sacrificio estimado', 'muertes':'Muertes', 'descartes':'Descartes', 'faenados':'Sacrificados'})
    df_camadas_merged['Fecha ingreso'] = pd.to_datetime(df_camadas_merged['Fecha ingreso']).dt.date
    df_camadas_merged['Dias'] = (datetime.now().date() - df_camadas_merged['Fecha ingreso']).apply(lambda x: x.days)
    df_camadas_merged['Disponibles'] =df_camadas_merged['Ingresados'] - df_camadas_merged['Muertes'] - df_camadas_merged['Descartes'] - df_camadas_merged['Sacrificados']

    # Muestras las camadas activas o mensaje si no hay ninguna
    if (df_granjas.shape[0] == 0):
        st.info('No tienes granjas registradas. Puedes crearlas en **Tu granja**', icon=':material/notifications:')
        st.stop()
    elif df_galpones.shape[0] == 0:
        st.info('No tienes galpones registrados. Puedes crearlas en el apartado gestionar de **Tu granja**', icon=':material/notifications:')
        st.stop()
    elif df_camadas.shape[0] == 0:
        st.info('Aún no haz registrado camadas. Puedes agregarlas en **gestionar**', icon=':material/notifications:')
        st.sidebar.write(f'Actualmente **NO** tienes camadas activas, pero aquí las puedes agregar:point_right:')
    else:
        st.write(f'Cuentas con **{df_camadas.shape[0]}** camadas activas y las puedes sacrificar ')
        st.dataframe(df_camadas_merged[['Granja','Galpón','Fecha ingreso','Sacrificio estimado','Dias', 'Disponibles', 'Sacrificados']], hide_index=True, use_container_width=True)
with st.container(border=True):
    if st.toggle('Sacrificar aves'):
        camada_sacrificio = st.selectbox('Selecciona la camada a sacrificar', options=df_camadas_merged['Galpón'])
        camada_sacrificio_id = int(df_camadas_merged['id'][df_camadas_merged['Galpón'] == camada_sacrificio][0])
        fecha_sacrificio = st.date_input('Ingresa fecha de sacrifio')
        hora_sacrificio = st.time_input('Ingrese hora de sacrificio')
        cant_sacrificio = st.number_input('Ingresa la cantidad de aves sacrificadas', value=None, step=1, min_value=1, key='cantSacrificio')
        peso_sacrificio = st.number_input('Ingresa la cantidad de Kilos producidos', value=None, step=0.01, min_value=0.01, key='pesoSacrificio')
        #aceptar_sinPeso = st.checkbox('Registar aves sacrificadas sin peso')
        if cant_sacrificio != None:
            
            if st.button('Registrar la Sacrificio', key='btnSacrificio'):
                resultado_sacrificio = util.agregarSacrificio(camada_sacrificio_id, fecha_sacrificio, hora_sacrificio, cant_sacrificio, peso_sacrificio)
                if resultado_sacrificio == True:
                    st.success(f'Se registró el sacrificio de {cant_sacrificio} aves exitosamente', icon=':material/done_all:')
                    st.rerun()
    