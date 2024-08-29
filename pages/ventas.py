import streamlit as st
import utilidades as util
import time
import pandas as pd
from psycopg2 import sql
from PIL import Image

# Se agrega logo
HORIZONTAL = 'src\images\horizontal_logo.png'

#Configuración de la página
st.set_page_config(page_title="Avicudatos - Ventas", page_icon='🐔')

st.logo(HORIZONTAL)

st.header('Avicudatos 🐔', divider='rainbow')

#Si no hay usuario registrado se va a Home
if 'usuario' not in st.session_state:
    st.switch_page('Home.py')

util.generarMenu(st.session_state['usuario'])

user_id = st.session_state['id_usuario']

st.title("Ventas de tus camadas")

## Establecemos conexion con la base de datos

df_presas = util.cosnultaQuery('SELECT * FROM tipo_presas')


st.write(
    """En este módulo se ingresarán los datos de las ventas de los pollos de engorde 🐓""")

df_granjas, df_galpones = util.listaGranjaGalpones(user_id)

df_camadas = util.consultarCamadas(user_id)
df_camadas_merged = pd.merge(df_camadas, df_galpones, how='left', left_on='galpon_id', right_on='galpon_id')
df_camadas_merged = df_camadas_merged.rename(columns={'cantidad':'Ingresados', 'fecha_inicio':'Fecha ingreso', 'fecha_estimada_sacrificio':'Sacrificio estimado', 'muertes':'Muertes', 'descartes':'Descartes', 'faenados':'Sacrificados'})
df_camadas_merged['todo'] = df_camadas_merged['Granja'].map(str) + ', '+ df_camadas_merged['Galpón']


def formVentas(n):      
    with st.container(border=True):
        
        #Datos de la venta
        camada_venta = st.selectbox('Seleccione la camada a vender', options=df_camadas_merged['todo'], key=f'ca{n}')
        camada_venta_id = int(df_camadas_merged['id'][df_camadas_merged['todo']==camada_venta][0])
        df_faenas = util.cosnultaQuery(f'SELECT * FROM PUBLIC.FAENA WHERE CAMADA_ID = {camada_venta_id}')
        df_faenas['diaYhora'] = df_faenas['fecha'].map(str) + ', ' + df_faenas['hora'].map(str)
        faena_venta = st.selectbox('Seleccione la faena a vender', options=df_faenas['diaYhora'], key=f'fa{n}')
        faena_venta_id = int(df_faenas['id'][df_faenas['diaYhora'] == faena_venta])
        cliente_venta = st.text_input('Cliente', key=f'{n+1}')
        fecha_venta = st.date_input('Fecha venta', key=f'date{n+1}')
        telefono_venta = st.number_input('Teléfono de contacto', key=f'tel{n+1}', step=1)
        
        # Columnas de descripción de la venta
        c2, c3, c4, c5 = st.columns(4, vertical_alignment='bottom')
        with c2:
            presa_venta = st.selectbox('Seleccione el tipo de presa',options=df_presas['nombre'], key=f'a{n+2}')
            presa_venta_id = int(df_presas['id'][df_presas['nombre'] == presa_venta])

        with c3:
            cantidad_venta = st.number_input('Ingrese la cantidad en Kg:', key=f'e{n+3}')
        
        with c4:
            valor_unitario_venta = st.number_input('Ingrese el valor unitario: ', step=1, key=f'i{n+4}')
        
        with c5:
            total_venta = round(cantidad_venta * valor_unitario_venta, 0)
            st.write('Total:')
            st.write(f'**{format(total_venta,",")}**')
        
        #Opción para agregar comentario a la venta
        if st.checkbox('Agregar un comentario', key=f'check{n+1}'):
            comentario_venta = st.text_area('Comentario:', key=f'coment{n}')
            if len(cliente_venta) == 0 or telefono_venta==0:
                st.warning('Existen campos vacios')
            
            else: 
                #Boton para registrar la venta con comentarios
                if st.button('Registrar ventas', key=f'b{n+5}'):
                    resultado_venta = util.registrarVenta(camada_venta_id,
                                                        faena_venta_id,
                                                        presa_venta_id, 
                                                        cantidad_venta,
                                                        valor_unitario_venta,
                                                        total_venta,
                                                        fecha_venta,
                                                        comentario_venta, 
                                                        cliente_venta,
                                                        telefono_venta,
                                                        )
                    if resultado_venta == True: 
                        st.success('Venta registrada con éxito', icon=':material/done_all:')
        else:
            if len(cliente_venta) == 0 or telefono_venta==0:
                st.warning('Existen campos vacios')
            
            else:
                #Boton para registrar la venta con comentarios
                if st.button('Registrar ventas', key=f'b{n+5}'):
                    resultado_venta = util.registrarVenta(camada_venta_id,
                                                        faena_venta_id,
                                                        presa_venta_id, 
                                                        cantidad_venta,
                                                        valor_unitario_venta,
                                                        total_venta,
                                                        fecha_venta,
                                                        cliente=cliente_venta,
                                                        telefono=telefono_venta
                                                        )
                    if resultado_venta == True: 
                        st.success('Venta registrada con éxito', icon=':material/done_all:')

# Agrega tantos formularios de venta como se indique
num_ventas = st.number_input('Ingrese la cantidad de ventas a registrar', step=1)
for i in range(num_ventas):
    formVentas(i)
