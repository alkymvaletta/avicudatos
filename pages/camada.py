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
    st.info('Aún no haz registrado camadas. Puedes agregarlas en **gestionar**', icon=':material/notifications:')
    st.sidebar.write(f'Actualmente **NO** tienes camadas activas, pero aquí las puedes agregar:point_right:')
else:
    st.dataframe(df_camadas_merged[['Granja','Galpón','Cantidad','Dias','Fecha ingreso', 'Faena estimada']], hide_index=True, use_container_width=True)
    st.sidebar.write(f'Actualmente tienes {df_camadas.shape[0]} camadas activas y aquí las puedes gestionar :point_right:')

df_razas = util.listaRazas()

st.subheader('Agrega o elimina camadas')

with st.container(border=True):
    if st.toggle('**Gestionar camadas**'):
        tab1, tab2 = st.tabs(['Agregar camada', 'Eliminar camada'])
        # Opción para agregar una camada
        with tab1:
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
        
        if df_camadas_merged.shape[0] >0:
            with tab2: #st.checkbox(':red[**Eliminar una camada**]', key='del_camada', value=False):
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
        else:
            with tab2:
                st.info('Aún no haz registrado camadas que puedas eliminar', icon=':material/notifications:')

### Se agregan la gestión de consumibles
if df_camadas.shape[0] > 0:
    st.subheader('Registra la operación de la camada')
    camada_operar = st.selectbox('Selecciona la camada a operar' ,options=df_camadas_merged['Galpón'])
    camada_operar_id = int(df_camadas_merged['id'][df_camadas_merged['Galpón'] == camada_operar].values[0])
    
    with st.container(border=True):
        if st.toggle('**Consumibles**'):
            
            st.write('Registra aquí el consumo de alimento, agua o grit que se le suministre a la camada')
            tab_alimento, tab_agua, tab_grit = st.tabs(['Alimento', 'Agua', 'Grit'])
            # Se agrega la gestión de los alimentos de la camada
            with tab_alimento:
                st.write('Registra la cantidad y tipo de alimento suministrado')
                cantidad_alimento = st.number_input('Cantidad de alimento suministrado en kilogramos', min_value=0.1)
                tipo_alimento = st.selectbox('Seleccione el tipo de alimento a suministrar', options=['opt1', 'opt2'])
                fecha_alimento = st.date_input('Ingrese la fecha de suministro', key='fechaAlimento')
                hora_alimento = st.time_input('Ingrese la hora de suministro', key='horaAlimento')
                st.write('Aqui se gestiona el alimento')
                st.button('Ingresar datos de alimento', key='btnalimento')
            
            # Se agrega la gestión del consumo de agua de la camada
            with tab_agua:
                st.write('Registra el consumo de agua de tu camada')
                cantidad_agua = st.number_input('Cantidad de agua suministrado en litros', min_value=0.1)
                fecha_agua = st.date_input('Ingrese la fecha de suministro', key='fechaAgua')
                hora_agua = st.time_input('Ingrese la hora de suministro', key='horaAgua')
                st.button('Ingresar datos de alimento', key='btnagua')
                st.write('Aqui se gestiona el agua')
            
            # Se agrega la gestión de suministro del Grit a la camada
            with tab_grit:
                st.write('Resgistra aquí el suministro de piedrecillas que el ave debe consumir para ayudar en la digestión del alimento')
                suministro_grit = st.selectbox('Se suministró grit a las aves', options=['Si', 'No'])
                fecha_grit = st.date_input('Ingrese la fecha de suministro', key='fechaGrit')
                st.button('Ingresar datos del grit', key='btngrit')

    with st.container(border=True):
        if st.toggle('**Medicamentos**'):
            st.write('Registra los medicamentos')

    ### Se agrega la gestión de la mortalidad
    with st.container(border=True):
        if st.toggle('**Mortalidad y descarte**'):
        
            # Se agrega la gestión de la mortalidad de los pollos en la camada
            tab_mortalidad, tab_descarte = st.tabs(['Mortalidad', 'Descarte'])
            with tab_mortalidad:
                cantidad_mortalidad = st.number_input('Ingrese la cantidad de aves muertas', min_value=1, step=1)
                causa_mortalidad = st.selectbox('Seleccione las posibles causas de muerte', options=['opt1', 'opt2'])
                fecha_mortalidad = st.date_input('Ingrese fecha de la muerte', key='fechaMortalidad')
                if st.checkbox('Agregar comentario'):
                    comentario_mortalidad = st.text_input('Ingrese comentario:')
                st.button('Ingresar datos de mortalidad', key='btnMortalidad')

            # Se agrega la gestión de la descarte de los pollos en la camada
            with tab_descarte:
                cantidad_descarte = st.number_input('Ingrese la cantidad de aves descartadas', min_value=1, step=1)
                fecha_descarte = st.date_input('Ingrese fecha de la muerte', key='fechaDescarte')
                razon_descarte = st.text_input('Ingrese la razón de descarte')
                st.button('Ingresar datos de descarte', key='btnDescarte')
                

    ## Se agrega la gestión de los pesajes de los pollos de la camada
    with st.container(border=True):
        if st.toggle('**Pesajes**'):
            fecha_pesaje = st.date_input('Fecha de la medición', key='fechaPesaje')
            tamano_muestra_pesaje = st.number_input('Indique la cantidad de pollos a pesar', min_value=1, step=1)
            pesos = []
            for i in range(tamano_muestra_pesaje):
                pesos.append(st.number_input(f'Ingrese el dato {i+1}', step=1, min_value=0, max_value=7000))
            st.write(pesos)
            st.write(sum(pesos)/len(pesos))
            

    ## Se agrega la gestión de los costos relacionados con la camada
    with st.container(border=True):
        if st.toggle('**Costos**'):
            st.write('Aqui se gestiona el alimento')