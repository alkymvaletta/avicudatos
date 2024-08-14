import streamlit as st
import utilidades as util
import pandas as pd
from psycopg2 import sql

#Configuración de Pagina

# Se agrega logo
HORIZONTAL = 'src\images\horizontal_logo.png'

st.set_page_config(
    page_title= 'Avicudatos - Granjas y galpones', 
    page_icon='🐔')

st.header('Avicudatos 🐔', divider='rainbow')

st.logo(HORIZONTAL)

#Si no hay usuario registrado se va a Home
if 'usuario' not in st.session_state:
    st.switch_page('Home.py')

# Se generan menús
util.generarMenu(st.session_state['usuario'])

st.title("Proveedores")

# Se agrega el id del usuario
user_id = st.session_state['id_usuario']

# Se define el listado de proveedores
df_proveedores = util.consultarProveedores(user_id)

if df_proveedores.shape[0] == 0:
    st.info('Aún no haz registrado proveedores, puedes hacerlo en **gestionar**', icon=':material/notifications:')
else:
    st.dataframe(df_proveedores[['Nombre', 'Nit', 'Contacto', 'Teléfono']], hide_index=True)

st.subheader('Agrega o elimina proveedores')
with st.container(border=True):
    if st.toggle('Gestionar proveedores'):
        agg_prov, del_prov = st.tabs(['Agregar', 'Eliminar'])
        with agg_prov:
            agg_nombre_proveedor = st.text_input('Nombre del proveedor')
            agg_nit_proveedor = st.number_input('Nit del proveedor', step=1, min_value=0)
            agg_contacto_proveedor = st.text_input('Contacto del proveedor')
            agg_tel_proveedor = st.number_input('Teléfono de contacto', step=1, min_value=0)
            act_enviar_proveedor = False
            if (len(agg_nombre_proveedor) != 0) and (agg_nit_proveedor != 0):
                act_enviar_proveedor = True
            if st.button('Agregar proveedor', disabled= not(act_enviar_proveedor)):
                resultado_proveedor = util.agregarPropveedor(agg_nombre_proveedor, agg_nit_proveedor, agg_contacto_proveedor, agg_tel_proveedor, user_id)
                if resultado_proveedor == True:
                    st.success('Se agregó el proveedor exitosamente', icon=':material/done_all:')
                    st.rerun()
        
        with del_prov:
            if df_proveedores.shape[0] == 0:
                st.info('Aún no haz registrado proveedores, puedes hacerlo en la otra pestaña', icon=':material/notifications:')
            else:
                del_nombre = st.selectbox('Selecciona proveedor a eliminar', options=df_proveedores['Nombre'])
                aceptar_eliminar = st.checkbox('Acepto que el proceso no se púede deshacer')
                if st.button('Eliminar proveedor', disabled=not(aceptar_eliminar), type='primary')
                    resultado_proveedor = util.agregarPropveedor(agg_nombre_proveedor, agg_nit_proveedor, agg_contacto_proveedor, agg_tel_proveedor, user_id)
                    if resultado_proveedor == True:
                        st.success('El proveedor se eliminó con exito', icon=':material/done_all:')
                        st.rerun()