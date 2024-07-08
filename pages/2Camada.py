import streamlit as st
import sqlalchemy
import psycopg2
from psycopg2 import sql
from PIL import Image
import os
import secrets

# Configuration of the page
st.set_page_config(page_title="1. Camadas", page_icon="🐣")
st.title("Mis camadas")
st.sidebar.header("Mis Camadas")
cant_camadas_activas = 2
st.sidebar.write(f'Actualmente tienes {cant_camadas_activas} camadas activas y aquí las puedes gestionar :point_right:')
st.write(
    """Gestiona tus camadas, registra sus consumos, medicaciones, los pesajes, la mortalidad, 
        los descartes que se presenten y los costos asociados a la camada""")

conn = st.connection('postgresql', type='sql')

# # Configurar la conexión a la base de datos
# def init_connection():
#     return psycopg2.connect(
#         host="TU_HOST",
#         database="TU_DATABASE",
#         user="TU_USUARIO",
#         password="TU_CONTRASEÑA"
#     )

# # Ejecutar una consulta en la base de datos
# def run_query(query, params=None):
#     conn = init_connection()
#     with conn.cursor() as cur:
#         cur.execute(query, params)
#         if query.strip().lower().startswith("select"):
#             return cur.fetchall()
#         else:
#             conn.commit()

# # Crear una función para insertar datos
# def insert_data(table, data):
#     keys = data.keys()
#     values = [data[key] for key in keys]
#     query = sql.SQL("INSERT INTO {table} ({fields}) VALUES ({values})").format(
#         table=sql.Identifier(table),
#         fields=sql.SQL(', ').join(map(sql.Identifier, keys)),
#         values=sql.SQL(', ').join(sql.Placeholder() * len(values))
#     )
#     run_query(query, values)

# # Crear formularios para cada tabla
# st.title("Formulario de Entrada de Datos para Avicultura")

# # Función para crear formulario
# def create_form(table_name, fields):
#     st.header(f"Tabla: {table_name.capitalize()}")
#     with st.form(key=f'{table_name}_form'):
#         form_data = {}
#         for field, field_type in fields.items():
#             if field_type == 'integer':
#                 form_data[field] = st.number_input(field.capitalize(), min_value=1, step=1)
#             elif field_type == 'decimal':
#                 form_data[field] = st.number_input(field.capitalize(), format="%.2f")
#             elif field_type == 'text':
#                 form_data[field] = st.text_input(field.capitalize())
#             elif field_type == 'date':
#                 form_data[field] = st.date_input(field.capitalize())
#             elif field_type == 'time':
#                 form_data[field] = st.time_input(field.capitalize())
#             elif field_type == 'boolean':
#                 form_data[field] = st.checkbox(field.capitalize())
        
#         submit_button = st.form_submit_button(label='Guardar')

#         if submit_button:
#             insert_data(table_name, form_data)
#             st.success(f"Datos de la tabla {table_name} guardados con éxito.")

# # Definiciones de campos para cada tabla
# tables = {
#     "camada": {
#         "cantidad": "integer",
#         "fecha_inicio": "date",
#         "proveedor_id": "integer"
#     },
#     "mortalidad": {
#         "fecha": "date",
#         "cantidad": "integer",
#         "comentario": "text"
#     },
#     "causas_mortalidad": {
#         "causa_posible": "text"
#     },
#     "descarte": {
#         "razon": "text",
#         "fecha": "date"
#     },
#     "costos": {
#         "costo_unitario": "integer",
#         "cantidad": "decimal",
#         "costo_total": "integer",
#         "fecha": "date"
#     },
#     "tipo_costos": {
#         "tipo": "text",
#         "es_directo": "boolean"
#     }}

# # Crear formulario si decide el usuario realizarlo
# for table_name, fields in tables.items():
#     create_form(table_name, fields)
    
# st.button("Terminar Alimento")

st.subheader('Camadas activas')

st.write('Aqui va el DF con la lista de camadas activas')

st.subheader('Gestiona las necesidades de la camada')


### Se agregan la gestión de consumibles 
if st.checkbox('**Consumibles**'):
    
    st.write('Registra aquí el consumo de alimento, agua o grit que se le suministre a la camada')
    
    if st.checkbox('Alimento'):
        st.write('Aqui se gestiona el alimento')
    
    if st.checkbox('Agua'):
        st.write('Aqui se gestiona el agua')
    
    if st.checkbox('Grit'):
        st.write('Resgistra aquí el suministro de piedrecillas que el ave debe consumir para ayudar en la digestión del alimento')

if st.checkbox('**Medicamentos**'):
    st.write('Registra los medicamentos')

### Se agrega la gestión de la mortalidad
if st.checkbox('**Mortalidad y descarte**'):
    if st.checkbox('Mortalidad'):
        st.write('Aqui se registraría las muertes')
        
    if st.checkbox('Descartes'):
        st.write('Aqui se registraría las muertes')

if st.checkbox('**Pesajes**'):
    st.write('Aqui se gestiona el alimento')
    
if st.checkbox('**Costos**'):
    st.write('Aqui se gestiona el alimento')