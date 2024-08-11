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

#Si no hay usuario registrado se va a Home
if 'usuario' not in st.session_state:
    st.switch_page('Home.py')

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

df_granjas, df_galpones = util.listaGranjaGalpones(user_id)

df_granjas_merged = pd.merge(df_granjas, df_municipios, how='left', left_on='ubicacion', right_on='cod_municipio')
df_granjas_show = df_granjas_merged[['nombre_granja', 'nombre', 'municipio', 'fecha']]
df_granjas_show = df_granjas_show.sort_values(by=['nombre_granja'])
df_granjas_show.rename(columns={'nombre_granja':'Granja','nombre':'Departamento' ,'fecha':'Fecha de creación', 'municipio':'Municipio'}, inplace=True)

st.session_state['granjas'] = df_granjas
st.session_state['galpones'] = df_galpones

# Muestra los galpones según la granja seleccionada
if df_granjas.shape[0] == 0:
        st.warning('Aún no haz registrado granjas. Puedes agregarlas en **gestionar**', icon=':material/notifications:')
else:
    st.write(f'Actualmente tienes :red[**{df_granjas_show.shape[0]}**] granjas activas:')
    
    st.dataframe(df_granjas_show, hide_index=True, use_container_width=True)
    
    st.subheader('Visualiza los galpones según la granja')
    
    listado_granjas = list(df_granjas_show['Granja'])
    listado_granjas.append('Ninguno')
    index_=len(listado_granjas)
    
    ver_galpones = st.selectbox('Selecciona la granja para ver sus galpones',listado_granjas, index=index_-1)
    
    if ver_galpones != 'Ninguno':
        mostrar_galpones = df_galpones[df_galpones['Granja'] == ver_galpones]
        if mostrar_galpones.shape[0] == 0:
            st.warning('Aún no haz registrado galpones en esta granja. Puedes agregarlos en **gestionar**', icon=':material/notifications:')
        else:
            st.dataframe(mostrar_galpones[['Galpón', 'Granja', 'Capacidad']],use_container_width=True ,hide_index=True)

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
                                st.rerun()
            
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

        # La opción parra eliminar granja o galpones
        if st.checkbox(':red[**Eliminar granja o galpón**]'):
            
            #La opción para eliminar una granja
            with st.container():
                if st.checkbox(':red[Eliminar granja]'):
                    if df_granjas.shape[0] == 0:
                        st.warning('Aún no haz registrado granjas. Puedes agregarlas en **gestionar**', icon=':material/notifications:')
                    else:
                        eliminar_granja = st.selectbox('Selecciona la granja a eliminar', options=listado_granjas, index=index_-1)
                        if eliminar_granja == 'Ninguno':
                            st.warning('Aún no haz seleccionado la granja **eliminar**. Recuerda que **EL PROCESO NO SE PUEDE DESHACER**', icon=':material/notifications:')
                        else:
                            # Se agrega doble verificación de eliminación para activar boton de eliminar.
                            aceptar_eliminar_granja = st.checkbox('Comprendo que al **Eliminar** el proceso no se puede deshacer', key='granja01')
                            aceptar_eliminar_todo_granja = st.checkbox('Comprendo que al **Eliminar** la granja tambien se :red[eliminaran los galpones asociados]', key='granja02')
                            aceptar_def = False
                            if (aceptar_eliminar_granja == True) and (aceptar_eliminar_todo_granja == True):
                                aceptar_def = True
                                # Se extrae el id de la granja a eliminar
                                eliminar_granja_id  = int(df_granjas['id'][df_granjas['nombre_granja'] == eliminar_granja].values[0])
                            if st.button('Eliminar granja', type='primary', disabled=not(aceptar_def),key='del_granja'):
                                resultado_eliminar_granja = util.quitarGranja(eliminar_granja_id)
                                if resultado_eliminar_granja == True:
                                    st.success('Se eliminó la granja exitosamente')
                                    st.rerun()
                                else:
                                    resultado_eliminar_granja
                                    

            # La opción para eliminar un galpón
            if st.checkbox(':red[Eliminar galpon]'):
                if df_galpones.shape[0] == 0:
                    st.warning('Aún no haz registrado galpones. Puedes agregarlas en **gestionar**', icon=':material/notifications:')
                else:
                    seleccion_granja_galpon = st.selectbox('Selecciona la granja', options=listado_granjas, index=index_-1)
                    listado_galpones = df_galpones[df_galpones['Granja'] == seleccion_granja_galpon]
                    
                    if seleccion_granja_galpon == 'Ninguno':
                        st.warning('Selecciona una granja para eliminar un galpón')
                    elif listado_galpones.shape[0] == 0:
                        st.warning('La granja seleccionada NO cuenta con galpones.', icon=':material/notifications:')
                    else:
                        eliminar_galpon = st.selectbox('Selecciona el galpón a eliminar', options=listado_galpones['Galpón'])
                        # el id del galpón que se va a eliminar
                        eliminar_galpon_id = int((listado_galpones['galpon_id'][listado_galpones['Galpón'] == eliminar_galpon]).values[0])
                        aceptar_eliminar_galpon= st.checkbox('Comprendo que al **Eliminar** el proceso no se puede deshacer', key='galpon01')
                        if st.button('Eliminar granja', type='primary', disabled=not(aceptar_eliminar_galpon), key='del_galpon'):
                            resultado_eliminar_galpon = util.quitarGalpon(eliminar_galpon_id)
                            if resultado_eliminar_galpon == True:
                                st.success('Se eliminó el galpón exitosamente')
                                st.rerun()
                            else:
                                resultado_eliminar_galpon