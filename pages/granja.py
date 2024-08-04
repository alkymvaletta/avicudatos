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

st.logo(HORIZONTAL)

# Se generan menús
util.generarMenu(st.session_state['usuario'])

st.title("Granja y galpones")
st.sidebar.header("Mi Granja")

st.write(
    """Integramos los datos de para que gestiones tus granjas y los galpones que tengas para cada uno de estas""")

## Sección que muestra las granjas del Usuario y los galpones de cada uno

st.header('Tus granjas')

st.write('Agrega o elimina granjas y galpones de acuerdo a tus necesidades')

user_id = st.session_state['id_usuario']

conn, c  = util.conectarDB()
if conn is not None and c is not None:
    try:
        c.execute(''' SELECT nombre_granja, ubicacion, fecha
            FROM PUBLIC.GRANJA
            WHERE USUARIO_ID = %s
                ''', (user_id,))
        granjas = c.fetchall()
        columnas = [desc[0] for desc in c.description]
        df_granjas = pd.DataFrame(granjas, columns=columnas)
        c.close()
        conn.close()
        # st.write(df_granjas)
    except Exception as e:
        st.write(f'Error al ejecutar la consulta: {e}')
else:
    st.write('No se pudo conectar a la base de datos')


if df_granjas.shape[0] == 0:
    st.warning('Aún no haz registrado granjas. Puedes agregarlas en **gestionar**', icon=':material/notifications:')
else:
    df_granjas

## Se hace check box para gestionar las granjas
with st.container():
    if st.checkbox('**Gestionar**'):
        
        # Se abre la opción para agregar granjas 
        if st.checkbox('**Agregar granjas**'):
            
            conn, c = util.conectarDB()
            
            if conn is not None and c is not None:
                try:
                    # Consulto los departamentos
                    c.execute(''' SELECT UPPER(NOMBRE) as nombre,
                                    COD_DEPARTAMENTO
                                FROM PUBLIC.UBICACION_DEPARTAMENTO
                                ORDER BY NOMBRE ASC
                            ''')
                    departamentos = c.fetchall()
                    columnas_departamentos = [desc[0] for desc in c.description]
                    df_departamentos = pd.DataFrame(departamentos, columns=columnas_departamentos)
                    
                    c.execute('''SELECT DEPARTAMENTO,
                                UPPER(NOMBRE) as nombre,
                                MUNICIPIO,
                                COD_MUNICIPIO
                            FROM PUBLIC.UBICACION
                            JOIN PUBLIC.UBICACION_DEPARTAMENTO ON UBICACION_DEPARTAMENTO.COD_DEPARTAMENTO = UBICACION.DEPARTAMENTO
                            ''')
                    municipios = c.fetchall()
                    columnas_municipios = [desc[0] for desc in c.description]
                    df_municipios = pd.DataFrame(municipios, columns= columnas_municipios)
                    
                    c.close()
                    conn.close()
                    # st.write(df_granjas)
                except Exception as e:
                    st.write(f'Error al ejecutar la consulta: {e}')
                        
            with st.form('frmGrnj'):
                
                nombre_granja = st.text_input('Ingresa el nombre de la granja:')
                departamento_granja = st.selectbox('Seleccione Departamento:', options= df_departamentos['nombre'])
                
                municipios_departamento = df_municipios['municipio'][df_municipios['nombre'] == departamento_granja]
                
                municipio_granja = st.selectbox('Seleccione Municipio:', options=municipios_departamento)

                btnGranja = st.form_submit_button('Crear granja')
                
                if btnGranja:
                    errores = []
                    if len(nombre_granja) == 0:
                        errores.append('El nombre no puede estar vacío.')
                    if errores:
                        for error in errores:
                            st.error(error, icon=':material/gpp_maybe:')
                    else:
                        st.success('Se creó la granja con exito')
            
            
            st.write(departamento_granja)
            
            st.write(df_departamentos)
            
            st.write(df_municipios)
        # Se abre la opción para agregar galpones
        if st.checkbox('**Agregar galpones**'):
            st.write('Se muestran los galpones ')