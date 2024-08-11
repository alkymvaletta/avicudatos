import streamlit as st
import pandas as pd
import utilidades as util
#import datetime
from psycopg2 import sql
from datetime import datetime
#from PIL import Image


# Se agrega logo
HORIZONTAL = 'src\images\horizontal_logo.png'

st.set_page_config(page_title="Avicudatos - Camadas", page_icon='🐔')

st.logo(HORIZONTAL)

#Si no hay usuario registrado se va a Home
if 'usuario' not in st.session_state:
    st.switch_page('Home.py')

util.generarMenu(st.session_state['usuario'])

user_id = st.session_state['id_usuario']
# Configuración de la página

st.title("Camadas")
if 'granjas' and 'galpon' in st.session_state:
    st.write('No hay sesion state en granja')
else:
    df_granjas, df_galpones = util.listaGranjaGalpones(user_id)

# Se configura el sidebar 
st.sidebar.header("Camadas")

# Se configura el texto de la página principal
st.write(
    """Gestiona tus camadas, registra sus consumos, medicaciones, los pesajes, la mortalidad, 
        los descartes que se presenten y los costos asociados a la camada""")

st.subheader('Tus camadas activas')

lista_granjas = sorted(df_galpones['Granja'].unique())

#Consultamos las camadas
df_camadas = util.consultarCamadas(user_id)
df_camadas_merged = pd.merge(df_camadas, df_galpones, how='left', left_on='galpon_id', right_on='galpon_id')
df_camadas_merged = df_camadas_merged.rename(columns={'cantidad':'Cantidad', 'fecha_inicio':'Fecha ingreso', 'fecha_estimada_sacrificio':'Faena estimada'})
df_camadas_merged['Fecha ingreso'] = pd.to_datetime(df_camadas_merged['Fecha ingreso']).dt.date
df_camadas_merged['Dias'] = (datetime.now().date() - df_camadas_merged['Fecha ingreso']).apply(lambda x: x.days)

# Muestras las camadas activas o mensaje si no hay ninguna
if df_camadas.shape[0] == 0:
    st.warning('Aún no haz registrado camadas. Puedes agregarlas en **gestionar**', icon=':material/notifications:')
    st.sidebar.write(f'Actualmente **NO** tienes camadas activas, pero aquí las puedes agregar:point_right:')
else:
    st.dataframe(df_camadas_merged[['Granja','Galpón','Cantidad','Dias','Fecha ingreso', 'Faena estimada']], hide_index=True, use_container_width=True)
    st.sidebar.write(f'Actualmente tienes {df_camadas.shape[0]} camadas activas y aquí las puedes gestionar :point_right:')

df_razas = util.listaRazas()

st.subheader('Agrega o elimina camadas')
with st.container(border=True):
    if st.toggle('**Gestionar camadas**'):
        # Opción para agregar una camada
        if st.checkbox(':green[**Agregar una camada**]', key='add_camada'):
            granja_camada = st.selectbox('Selecciona la granja', options=lista_granjas)
            granja_camada_id = int(df_galpones['granja_id'][df_galpones['Granja'] == granja_camada].values[0])
            galpon_camada = st.selectbox('Selecciona el galpón', options=df_galpones['Galpón'][df_galpones['Granja'] == granja_camada])
            galpon_camada_id = int(df_galpones['galpon_id'][df_galpones['Galpón'] == galpon_camada].values[0])
            cant_camada = st.number_input('Ingresa el tamaño de la camada', step=1, min_value=1)
            raza_camada = st.selectbox('Selecciona la raza', options=df_razas['nombre'].values)
            raza_camada_id = int(df_razas['id'][df_razas['nombre'] == raza_camada].values[0])
            fecha_ent_camada = st.date_input('Ingresa fecha de inicio de camada')
            fecha_faena_camada = util.sumaDias(fecha_ent_camada)
            
            if cant_camada > df_galpones['Capacidad'][df_galpones['galpon_id'] == galpon_camada_id].values[0]:
                st.warning('El tamaño de la camada excede la capacidad del galpón')
                continuar = st.checkbox('Estas seguro que deseas continuar')
                if st.button('Agregar camada', disabled=not continuar):
                    resultado_agg_camada = util.agregarCamada(granja_camada_id, 
                                                        galpon_camada_id, 
                                                        cant_camada, 
                                                        raza_camada_id, 
                                                        fecha_ent_camada,
                                                        fecha_faena_camada,
                                                        user_id)
                    if resultado_agg_camada == True:
                        st.success('Se agregó la camada exitosamente', icon=':material/done_all:')
                        st.rerun()
            else:
                if st.button('Agregar camada'):
                    resultado_agg_camada = util.agregarCamada(granja_camada_id, 
                                                        galpon_camada_id, 
                                                        cant_camada, 
                                                        raza_camada_id, 
                                                        fecha_ent_camada,
                                                        fecha_faena_camada,
                                                        user_id)
                    if resultado_agg_camada == True:
                        st.success('Se agregó la camada exitosamente', icon=':material/done_all:')
                        st.rerun()

        #Opción para Eliminar una camada
        if st.checkbox(':red[**Eliminar una camada**]', key='del_camada', value=False):
            granja_eliminar_camada = st.selectbox('Selecciona la camada a eliminar', options=df_camadas_merged['Granja'])
            galpon_eliminar_camada = st.selectbox('Selecciona la camada a eliminar', options=df_camadas_merged['Galpón'][df_camadas_merged['Granja'] == granja_eliminar_camada])
            galpon_eliminar_camada_id = int(df_camadas_merged['id'][df_camadas_merged['Galpón'] == galpon_eliminar_camada].values[0])
            st.write(f'El galpón seleccionado tiene un total de **{df_camadas_merged["Cantidad"].values[0]}** aves')
            aceptar_eliminar = st.checkbox('Comprendo que al **Eliminar** el proceso no se puede deshacer', key='camada_eliminar')
            if st.button('Eliminar camada', disabled=not(aceptar_eliminar), type='primary'):
                resultado_eliminar_camada = util.quitarCamada(galpon_eliminar_camada_id)
                if resultado_eliminar_camada:
                    st.success('Se eliminó la camada exitosamente', icon=':material/done_all:')
                    st.rerun()
                else:
                    resultado_eliminar_camada

### Se agregan la gestión de consumibles
if df_camadas.shape[0] > 0:
    st.subheader('Registra la operación de la camada')
    camada_operar = st.selectbox('Selecciona la camada a operar' ,options=df_camadas_merged['Galpón'])
    camada_operar_id = int(df_camadas_merged['id'][df_camadas_merged['Galpón'] == camada_operar].values[0])
    
    with st.container(border=True):
        if st.toggle('**Consumibles**'):
            
            st.write('Registra aquí el consumo de alimento, agua o grit que se le suministre a la camada')
            
            # Se agrega la gestión de los alimentos de la camada
            if st.checkbox('**Alimento**'):
                st.write('Registra la cantidad y tipo de alimento suministrado')
                cantidad_alimento = st.number_input('Cantidad de alimento suministrado en kilogramos', min_value=0.1)
                tipo_alimento = st.selectbox('Seleccione el tipo de alimento a suministrar', options=['opt1', 'opt2'])
                fecha_alimento = st.date_input('Ingrese la fecha de suministro')
                hora_alimento = st.time_input('Ingrese la hora de suministro')
                st.write('Aqui se gestiona el alimento')
                st.button('Ingresar datos de alimento')
            
            # Se agrega la gestión del consumo de agua de la camada
            if st.checkbox('**Agua**'):
                st.write('Registra el consumo de agua de tu camada')
                cantidad_agua = st.number_input('Cantidad de agua suministrado en litros', min_value=0.1)
                fecha_agua = st.date_input('Ingrese la fecha de suministro')
                hora_algua = st.time_input('Ingrese la hora de suministro')
                st.button('Ingresar datos de alimento')
                st.write('Aqui se gestiona el agua')
            
            # Se agrega la gestión de suministro del Grit a la camada
            if st.checkbox('**Grit**'):
                st.write('Resgistra aquí el suministro de piedrecillas que el ave debe consumir para ayudar en la digestión del alimento')
                suministro_grit = st.selectbox('Se suministró grit a las aves', options=['Si', 'No'])
                fecha_grit = st.date_input('Ingrese la fecha de suministro')
                st.button('Ingresar datos de alimento')
                
            
            
            

    with st.container(border=True):
        if st.toggle('**Medicamentos**'):
            st.write('Registra los medicamentos')

    ### Se agrega la gestión de la mortalidad
    with st.container(border=True):
        if st.toggle('**Mortalidad y descarte**'):
        
            # Se agrega la gestión de la mortalidad de los pollos en la camada
            if st.checkbox('Mortalidad'):
                st.write('Aqui se registraría las muertes')
            
            # Se agrega la gestión de la descarte de los pollos en la camada
            if st.checkbox('Descartes'):
                st.write('Aqui se registraría las muertes')

    ## Se agrega la gestión de los pesajes de los pollos de la camada
    with st.container(border=True):
        if st.toggle('**Pesajes**'):
            st.write('Aqui se gestiona el alimento')

    ## Se agrega la gestión de los costos relacionados con la camada
    with st.container(border=True):
        if st.toggle('**Costos**'):
            st.write('Aqui se gestiona el alimento')