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

#Conultamos lista de departamentos y municipios
df_departamentos, df_municipios = util.consultaMunicipios()

# Mostramos las granjas que tienes activas

conn, c  = util.conectarDB()

if conn is not None and c is not None:
    try:
        c.execute(''' SELECT
                id,
                nombre_granja, 
                ubicacion, 
                fecha
            FROM PUBLIC.GRANJA
            WHERE USUARIO_ID = %s
                ''', (user_id,))
        granjas = c.fetchall()
        columnas = [desc[0] for desc in c.description]
        df_granjas = pd.DataFrame(granjas, columns=columnas)
        
        #Se hacen transformaciones al df_granjas
        df_granjas_merged = pd.merge(df_granjas, df_municipios, how='left', left_on='ubicacion', right_on='cod_municipio')
        df_granjas_show = df_granjas_merged[['nombre_granja', 'nombre', 'municipio', 'fecha']]
        df_granjas_show.rename(columns={'nombre_granja':'Granja','nombre':'Departamento' ,'fecha':'Fecha de creación', 'municipio':'Municipio'}, inplace=True)
        
        c.execute('''
            SELECT 
                NOMBRE AS "Galpón",
                GRANJA.NOMBRE_GRANJA AS "Granja",
                CAPACIDAD AS "Capacidad",
                GALPON.ID AS "galpon_id",
                GRANJA_ID,
                UBICACION,
                DEPARTAMENTO,
                FECHA
            FROM PUBLIC.GALPON
            JOIN PUBLIC.GRANJA ON GRANJA.ID = GALPON.GRANJA_ID
            JOIN PUBLIC.UBICACION ON UBICACION.COD_MUNICIPIO = GRANJA.UBICACION
            WHERE USUARIO_ID = %s
        ''', (user_id,))
        galpones = c.fetchall()
        columnas = [desc[0] for desc in c.description]
        df_galpones = pd.DataFrame(galpones, columns=columnas)
        
        c.close()
        conn.close()
        # st.write(df_granjas)
    except Exception as e:
        st.write(f'Error al ejecutar la consulta: {e}')
else:
    st.write('No se pudo conectar a la base de datos')

# Muestra los galpones según la granja seleccionada
if df_granjas.shape[0] == 0:
        st.warning('Aún no haz registrado granjas. Puedes agregarlas en **gestionar**', icon=':material/notifications:')
else:
    st.write(f'Actualmente tienes :red[**{df_granjas_show.shape[0]}**] granjas activas:',df_granjas_show)
    
    st.write('Visualiza los galpones según la granja')
    
    listado_granjas = list(df_granjas_show['Granja'])
    listado_granjas.append('Ninguno')
    index_=len(listado_granjas)
    
    ver_galpones = st.selectbox('Selecciona la granja para ver sus galpones',listado_granjas, index=index_-1)
    
    if ver_galpones != 'Ninguno':
        mostrar_galpones = df_galpones[df_galpones['Granja'] == ver_galpones]
        if mostrar_galpones.shape[0] == 0:
            st.warning('Aún no haz registrado galpones en esta granja. Puedes agregarlos en **gestionar**', icon=':material/notifications:')
        else:
            mostrar_galpones[['Galpón', 'Granja', 'Capacidad']]
    

## Se hace check box para gestionar las granjas

with st.container():
    if st.toggle('**Gestionar**'):
        
        if st.checkbox(':green[**Agregar granja o galpon**]'):
        
            if st.checkbox(':green[Agregar granja]'):
                # Formulario para agregar granja
                with st.container(border=True):
                    nombre_granja = st.text_input('Ingresa el nombre de la granja:')
                    departamento_granja = st.selectbox('Seleccione Departamento:', options= df_departamentos['nombre'])
                    
                    municipios_departamento = df_municipios[df_municipios['nombre'] == departamento_granja]
                    municipio_granja = st.selectbox('Seleccione Municipio:', options=municipios_departamento['municipio'].sort_values())
                    cod_municipio_granja = int((df_municipios['cod_municipio'][df_municipios['municipio'] == municipio_granja]).values[0])
                    
                    btnAddGranja = st.button('Crear granja', type='primary')
                    if btnAddGranja:
                        errores = []
                        if len(nombre_granja) == 0:
                            errores.append('El nombre no puede estar vacío.')
                        if errores:
                            for error in errores:
                                st.error(error, icon=':material/gpp_maybe:')
                        else:
                            resultado = util.agregarGranja(user_id,nombre_granja,cod_municipio_granja)
                            if resultado == True:
                                st.success('Se creó la granja con exito')
            
            # Se abre la opción para agregar galpones
            if st.checkbox(':green[Agregar galpones]'):
                if df_granjas.shape[0] == 0:
                    st.warning('Aún no haz registrado granjas. Puedes agregarlas en **gestionar**', icon=':material/notifications:')
                
                else:
                    with st.container(border=True):
                        
                        granja_galpon= st.selectbox('Seleccione la granja', df_granjas_show['Granja'])
                        nombre_galpon = st.text_input('Ingrese nombre del galpón')
                        capacidad_galpon = st.number_input('Ingrese la capacidad del galpón', step=1,min_value=1, max_value=10_000)
                        
                        filtro_granja = df_granjas_merged['nombre_granja'] == granja_galpon
                        id_granja_galpon = int((df_granjas_merged[filtro_granja]['id']).values[0])
                        
                        btnAddGalpon = st.button('Crear galpón', type='primary')
                        if btnAddGalpon:
                            errores_galpon = []
                            if len(nombre_galpon) == 0:
                                errores_galpon.append('El nombre no puede estar vacío.')
                            if capacidad_galpon <= 1:
                                errores_galpon.append('La capacidad del galpón NO puede ser cero')
                            if errores_galpon:
                                for error in errores_galpon:
                                    st.error(error, icon=':material/gpp_maybe:')
                            else:
                                resultado_galpon = util.agregarGalpon(id_granja_galpon, capacidad_galpon, nombre_galpon)
                                if resultado_galpon == True:
                                    st.success('Se creó el galpón exitosamente')

        
        if st.checkbox(':red[**Eliminar granja o galpón**]'):
        
            if st.checkbox(':red[Eliminar granja]'):
                if df_granjas.shape[0] == 0:
                    st.warning('Aún no haz registrado granjas. Puedes agregarlas en **gestionar**', icon=':material/notifications:')
                else:
                    eliminar_granja = st.selectbox('Selecciona la granja a eliminar', options=listado_granjas, index=index_-1)
                    aceptar_eliminar_granja = st.checkbox('Comprendo que al **Eliminar** el proceso no se puede deshacer')
                    if st.button('Eliminar granja', type='primary', disabled=not(aceptar_eliminar_granja)):
                        st.write('Se elimina')
            
            if st.checkbox(':red[Eliminar galpon]'):
                if mostrar_galpones.shape[0] == 0:
                    st.warning('Aún no haz registrado galpones. Puedes agregarlas en **gestionar**', icon=':material/notifications:')
                else:
                    seleccion_granja = st.selectbox('Selecciona la granja', options=listado_granjas, index=index_-1)
                    eliminar_galpon = st.selectbox('Selecciona el galpón a eliminar', options=listado_granjas, index=index_-1)
                    aceptar_eliminar_granja = st.checkbox('Comprendo que al **Eliminar** el proceso no se puede deshacer')
                    if st.button('Eliminar granja', type='primary', disabled=not(aceptar_eliminar_granja)):
                        st.write('Se elimina')