import streamlit as st
#import sqlalchemy
#import psycopg2
#from psycopg2 import sql
from PIL import Image
import os
import secrets

#Configuración de Pagina
st.set_page_config(page_title="Alimento", page_icon="🌽", layout='centered')
st.title("Datos de Alimentación")
st.sidebar.header("Alimentación")

st.write(
    """En este módulo se ingresarán los datos de los alimentos que se le estan suministrando 
       a nuestros pollos """)

conn = st.connection('postgresql', type='sql')

#st.cache()

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


# Definiciones de campos para cada tabla
tables = {
    "razas": {
        "nombre": "text"
    },

    "grit": {
        "suministrado": "integer"
    },
    "alimento": {
        "peso": "decimal",
        "fecha": "date",
        "hora": "time"
    },
    "tipo_alimento": {
        "etapa_alimento": "text"
    },
    "agua": {
        "cantidad": "decimal",
        "fecha": "date",
        "hora": "time"
    },
    
    "proveedor": {
        "nombre": "text"
    }}

# Crear formulario si decide el usuario realizarlo
# for table_name, fields in tables.items():
#     create_form(table_name, fields)
st.button("Terminar Alimento")