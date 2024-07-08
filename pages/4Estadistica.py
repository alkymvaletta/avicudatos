import streamlit as st
#import psycopg2
import pandas as pd

conn = st.connection('postgresql', type='sql')

df = conn.query('SELECT * FROM public.objetivos_desempeno')


st.write(df)
# Configurar la conexión a la base de datos
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
#         return cur.fetchall()

# # Obtener datos de la tabla 'usuario'
# def get_user_data():
#     query = "SELECT nombre, apellido, email FROM usuario LIMIT 1"
#     result = run_query(query)
#     if result:
#         return result[0]
#     return None

# # Obtener datos de la tabla 'camada'
# def get_camada_data():
#     query = "SELECT COUNT(*) FROM camada WHERE activa = TRUE"
#     result = run_query(query)
#     if result:
#         return result[0][0]
#     return 0

# # Obtener datos combinados de todas las tablas relevantes
# def get_combined_data():
#     query = """
#     SELECT
#         u.nombre,
#         u.apellido,
#         u.email,
#         g.nombre_granja,
#         l.municipio,
#         d.nombre AS departamento,
#         COUNT(c.id) AS camadas_activas
#     FROM usuario u
#     LEFT JOIN granja g ON g.usuario_id = u.id
#     LEFT JOIN ubicacion l ON g.ubicacion_id = l.cod_municipio
#     LEFT JOIN ubicacion_departamento d ON l.departamento_id = d.cod_departamento
#     LEFT JOIN camada c ON c.granja_id = g.id AND c.activa = TRUE
#     GROUP BY u.nombre, u.apellido, u.email, g.nombre_granja, l.municipio, d.nombre
#     """
#     result = run_query(query)
#     columns = ["Nombre", "Apellido", "Email", "Nombre Granja", "Municipio", "Departamento", "Camadas Activas"]
#     return pd.DataFrame(result, columns=columns)

# # Interfaz de usuario
# def main():
#     st.title("Estadísticas de Avicuidatos")

#     # Obtener datos del usuario
#     user_data = get_user_data()
#     if user_data:
#         nombre, apellido, email = user_data
#         st.write(f"Hola {nombre} {apellido}, tienes {get_camada_data()} camadas activas.")
#     else:
#         st.write("No se encontraron datos del usuario.")

#     # Obtener y mostrar datos combinados en una tabla
#     combined_data = get_combined_data()
#     if not combined_data.empty:
#         st.write("Aquí tienes un resumen de tus datos:")
#         st.dataframe(combined_data)
#     else:
#         st.write("No se encontraron datos para mostrar.")

# if __name__ == "__main__":
#     main()
