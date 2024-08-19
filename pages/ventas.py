import streamlit as st
import sqlalchemy
import psycopg2
import utilidades as util
import time
from psycopg2 import sql
from PIL import Image

# Se agrega logo
HORIZONTAL = 'src\images\horizontal_logo.png'

st.set_page_config(page_title="Avicudatos - Ventas", page_icon='🐔')

st.logo(HORIZONTAL)

st.header('Avicudatos 🐔', divider='rainbow')

#Si no hay usuario registrado se va a Home
if 'usuario' not in st.session_state:
    st.switch_page('Home.py')

util.generarMenu(st.session_state['usuario'])

# Configuration of the page

st.title("Ventas de tus camadas")

## Establecemos conexion con la base de datos

#conn, c = util.conectarDB()
df_presas = util.cosnultaQuery('SELECT * FROM tipo_presas')
#df = c.execute('SELECT * FROM tipo_presas')

#st.write(df_presas['nombre'])

tipos = df_presas['nombre'].unique()

#st.write(tipos)


st.write(
    """En este módulo se ingresarán los datos de las ventas de los pollos de engorde 🐓""")

def formVentas(n):      
    with st.container(border=True):
        
        camada_venta = st.selectbox('Seleccione la camada a vender', options=['opt-1', 'opt0'], key=f'ca{n}')
        
        faena_venta = st.selectbox('Seleccione la faena a vender', options=['opt1', 'opt2'], key=f'fa{n}')
        
        cliente_venta = st.text_input('Cliente', key=f'{n+1}')
        
        c2, c3, c4, c5 = st.columns(4, vertical_alignment='bottom')
        with c2:
            presa_venta = st.selectbox('Seleccione el tipo de presa',tipos, key=f'a{n+2}')

        with c3:
            cantidad_venta = st.number_input('Ingrese la cantidad en Kg:', key=f'e{n+3}')
        
        with c4:
            valor_unitario_venta = st.number_input('Ingrese el valor unitario: ', step=1, key=f'i{n+4}')
        
        with c5:
            total_venta = round(cantidad_venta * valor_unitario_venta, 0)
            st.write('Total:')
            st.write(f'**{format(total_venta,",")}**')
        
        if st.button('Registrar ventas', key=f'b{n+5}'):
            st.success('Registrado con éxito')
            #st.rerun()

num_ventas = st.number_input('Ingrese la cantidad de ventas a registrar', step=1)
for i in range(num_ventas):
    formVentas(i)
