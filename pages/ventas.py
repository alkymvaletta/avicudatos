import streamlit as st
import utilidades as util
#import time
import pandas as pd
from datetime import datetime
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

df_camadas = util.consultarCamadasActiva(user_id)
df_camadas_merged = pd.merge(df_camadas, df_galpones, how='left', left_on='galpon_id', right_on='galpon_id')
df_camadas_merged = df_camadas_merged.rename(columns={'cantidad':'Ingresados', 'fecha_inicio':'Fecha ingreso', 'fecha_estimada_sacrificio':'Sacrificio estimado', 'muertes':'Muertes', 'descartes':'Descartes', 'faenados':'Sacrificados'})
df_camadas_merged['todo'] = df_camadas_merged['Granja'].map(str) + ', '+ df_camadas_merged['Galpón']

def verificarFaena(df):
    if df.shape[0] == 0:
        st.info('Aún no haz registrado sacrificios en la camada seleccionada', icon=':material/notifications:')
        return st.stop()
    
def formVentas(n):      
    with st.container(border=True):
        
        #Datos de la venta
        camada_venta = st.selectbox('Seleccione la camada a vender', options=df_camadas_merged['todo'], key=f'ca{n}')
        camada_venta_id = int(df_camadas_merged['id'][df_camadas_merged['todo']==camada_venta][0])
        df_faenas = util.cosnultaQuery(f'SELECT * FROM PUBLIC.FAENA WHERE CAMADA_ID = {camada_venta_id}')
        verificarFaena(df_faenas)
        df_faenas['diaYhora'] = df_faenas['fecha'].map(str) + ', ' + df_faenas['hora'].map(str)
        faena_venta = st.selectbox('Seleccione el sacrificio del que desea vender', options=df_faenas['diaYhora'], key=f'fa{n}')
        faena_venta_id = int(df_faenas['id'][df_faenas['diaYhora'] == faena_venta])
        cliente_venta = st.text_input('Cliente', key=f'{n+1}')
        identificacion_venta = st.number_input('Número identificación', key=f'ideC{n+1}', step=1)
        fecha_venta = st.date_input('Fecha venta', key=f'date{n+1}')
        telefono_venta = st.number_input('Teléfono de contacto', key=f'tel{n+1}', step=1)
        
        # Columnas de descripción de la venta
        c2, c3, c4, c5 = st.columns(4, vertical_alignment='bottom')
        with c2:
            presa_venta = st.selectbox('Seleccione el tipo de presa',options=df_presas['nombre'], key=f'a{n+2}')
            presa_venta_id = int(df_presas['id'][df_presas['nombre'] == presa_venta])

        with c3:
            cantidad_venta = st.number_input('Ingrese la cantidad en Kg:', key=f'e{n+3}', min_value=0.000)
        
        with c4:
            valor_unitario_venta = st.number_input('Ingrese el valor unitario: ', step=1, key=f'i{n+4}')
        
        with c5:
            total_venta = round(cantidad_venta * valor_unitario_venta, 0)
            st.write('Total:')
            st.write(f'**{format(total_venta,",")}**')
        
        #Opción para agregar comentario a la venta
        if st.checkbox('Agregar un comentario', key=f'check{n+1}'):
            comentario_venta = st.text_area('Comentario:', key=f'coment{n}')
            if len(cliente_venta) == 0 or telefono_venta==0 or identificacion_venta==0:
                st.warning('Existen campos vacios')
            
            else: 
                #Boton para registrar la venta con comentarios
                if st.button('Registrar ventas', key=f'b{n+5}'):
                    resultado_venta = util.registrarVenta(user_id,
                                                        camada_venta_id,
                                                        faena_venta_id,
                                                        presa_venta_id, 
                                                        cantidad_venta,
                                                        valor_unitario_venta,
                                                        total_venta,
                                                        fecha_venta,
                                                        identificacion_venta,
                                                        comentario_venta, 
                                                        cliente_venta,
                                                        telefono_venta
                                                        )
                    if resultado_venta == True: 
                        st.success('Venta registrada con éxito', icon=':material/done_all:')
        else:
            if len(cliente_venta) == 0 or telefono_venta==0 or identificacion_venta==0:
                st.warning('Existen campos vacios')
            
            else:
                #Boton para registrar la venta con comentarios
                if st.button('Registrar ventas', key=f'b{n+5}'):
                    resultado_venta = util.registrarVenta(user_id,
                                                        camada_venta_id,
                                                        faena_venta_id,
                                                        presa_venta_id, 
                                                        cantidad_venta,
                                                        valor_unitario_venta,
                                                        total_venta,
                                                        fecha_venta,
                                                        identificacion_venta,
                                                        cliente=cliente_venta,
                                                        telefono=telefono_venta
                                                        )
                    if resultado_venta == True: 
                        st.success('Venta registrada con éxito', icon=':material/done_all:')

# Agrega tantos formularios de venta como se indique
with st.container(border=True):
    if st.toggle('Registrar ventas'):
        num_ventas = st.number_input('Ingrese la cantidad de ventas a registrar', step=1, min_value=1)
        for i in range(num_ventas):
            formVentas(i)

with st.container(border=True):
    if st.toggle('Ver ventas realizadas'):
        
        
        #@st.cache_data(show_spinner=True)
        def consultarVentas():
            df_ventas = util.cosnultaQuery(f'''
                                        SELECT IDENTIFICACION_CLIENTE AS "N. Identificación",
                                            VENTAS.USER_ID,
                                            CAMADA_ID,
                                            FECHA AS "Fecha Venta",
                                            CAMADA.FECHA_INICIO AS "Fecha Inicio Camada",
                                            GRANJA_ID,
                                            FAENA_ID,
                                            NOMBRE AS "Tipo Presa",
                                            VENTAS.CANTIDAD as "Cantidad",
                                            VENTAS.PRECIO_UNITARIO as "Vlr. Unitario",
                                            PRECIO_TOTAL as "Total",
                                            COMENTARIOS,
                                            CLIENTE AS "Cliente",
                                            TELEFONO
                                        FROM PUBLIC.VENTAS
                                        JOIN PUBLIC.CAMADA ON CAMADA.ID = VENTAS.CAMADA_ID
                                        JOIN PUBLIC.TIPO_PRESAS ON TIPO_PRESAS.ID = VENTAS.PRESA
                                        WHERE VENTAS.USER_ID = {user_id}
                                        ORDER BY FECHA ASC
                                        ''')
            tipos_presa = df_ventas['Tipo Presa'].unique()
            val_min = df_ventas['Total'].min()
            val_max = df_ventas['Total'].max()
            return df_ventas, tipos_presa, val_min, val_max
        
        df_ventas, tipos_presa, val_min, val_max = consultarVentas()
        #fecha_venta = df_ventas['Fecha Venta'].min()
        
        #Se aplica mensaje si aún no hay ventas.
        if df_ventas.shape[0] == 0:
            st.info('Aún no haz registrado ventas de tus camadas', icon=':material/notifications:')
        else:
            #Aplica filtros a las ventas
            col_fecha, col_presa, col_valor = st.columns(3)
            
            with col_fecha:
                cliente = st.text_input('Buscar por cliente', )
            
            with col_presa:
                presa = st.multiselect('Seleccione presas', tipos_presa)
            
            with col_valor:
                rango_venta = st.slider('Rango de venta',val_min, val_max, (val_min, val_max))
            
            # Se aplica los filtros aplicados a las ventas
            df_ventas_filtered = df_ventas[
                (df_ventas['Cliente'].str.contains(cliente, case=False)) &
                (df_ventas['Tipo Presa'].isin(presa)) & 
                (df_ventas['Total']>= rango_venta[0]) &
                (df_ventas['Total']<= rango_venta[1])]
            
            #Muestra los las ventas que cumplen con las condiciones
            st.dataframe(df_ventas_filtered, column_order=['Fecha Venta',"N. Identificación", 'Cliente','Tipo Presa', 'Cantidad', 'Vlr. Unitario', 'Total'], hide_index=True, use_container_width=True)
            
            # df_ventas_filtered_agg = df_ventas_filtered.groupby('Fecha Venta')['Total'].sum().reset_index()
            # #df_ventas_filtered_agg
            # st.line_chart(df_ventas_filtered_agg, x='Fecha Venta', y='Total')
