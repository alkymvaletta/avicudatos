import streamlit as st
import pandas as pd
import utilidades as util
from psycopg2 import sql
from datetime import datetime

# Se agrega logo
HORIZONTAL = 'src\images\horizontal_logo.png'

st.set_page_config(page_title="Avicudatos - Camadas", page_icon='🐔')

st.logo(HORIZONTAL)

st.header('Avicudatos 🐔', divider='rainbow')

#Si no hay usuario registrado se va a Home
if 'usuario' not in st.session_state:
    st.switch_page('Home.py')

util.generarMenu(st.session_state['usuario'])

user_id = st.session_state['id_usuario']
# Configuración de la página

st.title("Camadas")

if 'granjas' and 'galpon' in st.session_state:
    st.write('No hay sesion state en granja')
else:
    df_granjas, df_galpones = util.listaGranjaGalpones(user_id)

# Se configura el sidebar 
st.sidebar.header("Camadas")

# Se configura el texto de la página principal
st.write(
    """Gestiona tus camadas, registra sus consumos, medicaciones, los pesajes, la mortalidad, 
        los descartes que se presenten y los costos asociados a la camada""")

st.subheader('Tus camadas activas')

lista_granjas = sorted(df_galpones['Granja'].unique())

#Consultamos las camadas
df_camadas = util.consultarCamadas(user_id)
df_camadas_merged = pd.merge(df_camadas, df_galpones, how='left', left_on='galpon_id', right_on='galpon_id')
df_camadas_merged = df_camadas_merged.rename(columns={'cantidad':'Ingresados', 'fecha_inicio':'Fecha ingreso', 'fecha_estimada_sacrificio':'Sacrificio estimado', 'muertes':'Muertes', 'descartes':'Descartes', 'faenados':'Sacrificados'})
df_camadas_merged['Fecha ingreso'] = pd.to_datetime(df_camadas_merged['Fecha ingreso']).dt.date
df_camadas_merged['Dias'] = (datetime.now().date() - df_camadas_merged['Fecha ingreso']).apply(lambda x: x.days)
df_camadas_merged['Disponibles'] =df_camadas_merged['Ingresados'] - df_camadas_merged['Muertes'] - df_camadas_merged['Descartes'] - df_camadas_merged['Sacrificados']

#df_camadas_merged

# Muestras las camadas activas o mensaje si no hay ninguna
if (df_granjas.shape[0] == 0):
    #link = st.page_link('pages/granja.py',label='ir a **Tu granja**')
    st.info('No tienes granjas registradas. Puedes crearlas en **Tu granja**', icon=':material/notifications:')
    st.stop()
elif df_galpones.shape[0] == 0:
    st.info('No tienes galpones registrados. Puedes crearlas en el apartado gestionar de **Tu granja**', icon=':material/notifications:')
    st.stop()
elif df_camadas.shape[0] == 0:
    st.info('Aún no haz registrado camadas. Puedes agregarlas en **gestionar**', icon=':material/notifications:')
    st.sidebar.write(f'Actualmente **NO** tienes camadas activas, pero aquí las puedes agregar:point_right:')
else:
    st.dataframe(df_camadas_merged[['Granja','Galpón','Fecha ingreso','Ingresados', 'Disponibles', 'Muertes','Descartes' ,'Sacrificados','Dias', 'Sacrificio estimado']], hide_index=True, use_container_width=True)
    st.sidebar.write(f'Actualmente tienes {df_camadas.shape[0]} camadas activas y aquí las puedes gestionar :point_right:')

df_razas = util.listaRazas()

#df_camadas_merged

## Agergar o eliminar camadas
st.subheader('Agrega o elimina camadas')
with st.container(border=True):
    if st.toggle('**Gestionar camadas**'):
        tab1, tab2, tab3 = st.tabs(['Agregar camada','Finalizar camada' ,'Eliminar camada'])
        # Opción para agregar una camada
        with tab1:
            granja_camada = st.selectbox('Selecciona la granja', options=lista_granjas)
            granja_camada_id = int(df_galpones['granja_id'][df_galpones['Granja'] == granja_camada].values[0])
            galpon_camada = st.selectbox('Selecciona el galpón', options=df_galpones['Galpón'][df_galpones['Granja'] == granja_camada])
            galpon_camada_id = int(df_galpones['galpon_id'][df_galpones['Galpón'] == galpon_camada].values[0])
            cant_camada = st.number_input('Ingresa el número de pollos recibidos', step=1, min_value=1)
            raza_camada = st.selectbox('Selecciona la raza', options=df_razas['nombre'].values)
            raza_camada_id = int(df_razas['id'][df_razas['nombre'] == raza_camada].values[0])
            df_proveedores = util.consultarProveedores(user_id)
            proveedor_camada = st.selectbox('Seleccione el proveedor de la camada', options=df_proveedores['Nombre'])
            proveedor_camada_id = int(df_proveedores['id'][df_proveedores['Nombre'] == proveedor_camada].values[0])
            fecha_ent_camada = st.date_input('Ingresa fecha de inicio de camada')
            fecha_faena_camada = util.sumaDias(fecha_ent_camada)
            if cant_camada > df_galpones['Capacidad'][df_galpones['galpon_id'] == galpon_camada_id].values[0]:
                st.warning('El tamaño de la camada excede la capacidad del galpón')
                continuar = st.checkbox('Estas seguro que deseas continuar')
                if st.button('Agregar camada', disabled=not continuar):
                    resultado_agg_camada = util.agregarCamada(granja_camada_id, 
                                                        galpon_camada_id, 
                                                        cant_camada, 
                                                        raza_camada_id,
                                                        proveedor_camada_id,
                                                        fecha_ent_camada,
                                                        fecha_faena_camada,
                                                        user_id)
                    if resultado_agg_camada == True:
                        st.success('Se agregó la camada exitosamente', icon=':material/done_all:')
                        st.rerun()
            else:
                if st.button('Agregar camada'):
                    resultado_agg_camada = util.agregarCamada(granja_camada_id, 
                                                        galpon_camada_id, 
                                                        cant_camada, 
                                                        raza_camada_id,
                                                        proveedor_camada_id,
                                                        fecha_ent_camada,
                                                        fecha_faena_camada,
                                                        user_id)
                    if resultado_agg_camada == True:
                        st.success('Se agregó la camada exitosamente', icon=':material/done_all:')
                        st.sle
                        st.rerun()
        
        if df_camadas_merged.shape[0] > 0:
            with tab2:
                granja_finalizar_camada = st.selectbox('Selecciona la camada a eliminar', options=df_camadas_merged['Granja'], key='granjafinal')
                galpon_finalizar_camada = st.selectbox('Selecciona la camada a eliminar', options=df_camadas_merged['Galpón'][df_camadas_merged['Granja'] == granja_finalizar_camada], key='galponfinal')
                finalizar_camada_id = int(df_camadas_merged['id'][df_camadas_merged['Galpón'] == galpon_finalizar_camada].values[0])
                st.write(f'La camada a :red[finalizar] inició con {df_camadas_merged["Ingresados"].values[0]} aves y se han sacrificado {df_camadas_merged["Sacrificados"].values[0]}')
                aceptar_finalizar = st.checkbox('Confirmo que deseo finalizar la camada')
                if st.button('Finalizar camada', disabled=not(aceptar_finalizar), type='primary'):
                    resultado_finalizar_camada = util.finalizarCamada(finalizar_camada_id)
                    resultado_finalizar_camada
                    if resultado_finalizar_camada:
                        st.success('Se finalizó la camada exitosamente', icon=':material/done_all:')
                        #st.rerun()
                    else:
                        resultado_finalizar_camada
            
            
            with tab3: #st.checkbox(':red[**Eliminar una camada**]', key='del_camada', value=False):
                granja_eliminar_camada = st.selectbox('Selecciona la camada a eliminar', options=df_camadas_merged['Granja'])
                galpon_eliminar_camada = st.selectbox('Selecciona la camada a eliminar', options=df_camadas_merged['Galpón'][df_camadas_merged['Granja'] == granja_eliminar_camada])
                galpon_eliminar_camada_id = int(df_camadas_merged['id'][df_camadas_merged['Galpón'] == galpon_eliminar_camada].values[0])
                #df_camadas_merged
                st.write(f'El galpón seleccionado tiene un total de **{df_camadas_merged["Ingresados"].values[0]}** aves')
                aceptar_eliminar = st.checkbox('Comprendo que al **Eliminar** el proceso no se puede deshacer', key='camada_eliminar')
                if st.button('Eliminar camada', disabled=not(aceptar_eliminar), type='primary'):
                    resultado_eliminar_camada = util.quitarCamada(galpon_eliminar_camada_id)
                    if resultado_eliminar_camada:
                        st.success('Se eliminó la camada exitosamente', icon=':material/done_all:')
                        st.rerun()
                    else:
                        resultado_eliminar_camada
        else:
            with tab2:
                st.info('Aún no haz registrado camadas que puedas finalizar', icon=':material/notifications:')
            with tab3:
                st.info('Aún no haz registrado camadas que puedas eliminar', icon=':material/notifications:')

def verificarProveedor(df):
    if df.shape[0] == 0:
        st.info('Aún no haz registrado proveedores. Registralo en **Proveedores** para continuar', icon=':material/notifications:')
        return st.stop()

### Se agregan la gestión de consumibles
if df_camadas.shape[0] > 0:
    st.subheader('Registra la operación de la camada')
    camada_operar = st.selectbox('Selecciona la camada a operar' ,options=df_camadas_merged['Galpón'])
    camada_operar_id = int(df_camadas_merged['id'][df_camadas_merged['Galpón'] == camada_operar].values[0])
    
    with st.container(border=True):
        if st.toggle('**Consumibles**'):
            
            st.write('Registra aquí el consumo de alimento, agua o grit que se le suministre a la camada')
            tab_alimento, tab_agua, tab_grit = st.tabs(['Alimento', 'Agua', 'Grit'])
            # Se agrega la gestión de los alimentos de la camada
            with tab_alimento:
                st.write('Registra la cantidad y tipo de alimento suministrado')
                cantidad_alimento = st.number_input('Cantidad de alimento suministrado en **kilogramos**', min_value=0.1)
                df_etapas_alimento = util.cosnultaQuery('SELECT * FROM PUBLIC.TIPOS_ALIMENTOS')
                tipo_alimento = st.selectbox('Seleccione el tipo de alimento a suministrar', options=df_etapas_alimento['etapa_alimento'])
                tipo_alimento_id = int(df_etapas_alimento['id'][df_etapas_alimento['etapa_alimento'] == tipo_alimento].values[0])
                fecha_alimento = st.date_input('Ingrese la fecha de suministro', key='fechaAlimento')
                hora_alimento = st.time_input('Ingrese la hora de suministro', key='horaAlimento')
                st.write('Aqui se gestiona el alimento')
                if st.button('Ingresar datos de alimento', key='btnalimento'):
                    resultado_alimento = util.agregarAlimento(camada_operar_id, 
                                                            cantidad_alimento, 
                                                            tipo_alimento_id, 
                                                            fecha_alimento, 
                                                            hora_alimento)
                    if resultado_alimento == True:
                        st.success('Se agregó el suministro de alimento exitosamente', icon=':material/done_all:')
                        #st.rerun()
            
            # Se agrega la gestión del consumo de agua de la camada
            with tab_agua:
                st.write('Registra el consumo de agua de tu camada')
                cantidad_agua = st.number_input('Cantidad de agua suministrado en litros', min_value=0.1)
                fecha_agua = st.date_input('Ingrese la fecha de suministro', key='fechaAgua')
                hora_agua = st.time_input('Ingrese la hora de suministro', key='horaAgua')
                if st.button('Ingresar datos de consumo de agua', key='btnagua'):
                    resultado_agua = util.agregarAgua(camada_operar_id, 
                                                    cantidad_agua, 
                                                    fecha_agua, 
                                                    hora_agua)
                    if resultado_agua == True:
                        st.success('Se agregó el suministro de agua exitosamente', icon=':material/done_all:')

            # Se agrega la gestión de suministro del Grit a la camada
            with tab_grit:
                st.write('Resgistra aquí el suministro de piedrecillas que el ave debe consumir para ayudar en la digestión del alimento')
                suministro_grit = st.selectbox('Se suministró grit a las aves', options=['Si', 'No'])
                if suministro_grit == 'Si':
                    suministro_grit = True
                else:
                    suministro_grit = False
                fecha_grit = st.date_input('Ingrese la fecha de suministro', key='fechaGrit')
                if st.button('Ingresar datos del grit', key='btngrit'):
                    resultado_grit = util.agregarGrit(camada_operar_id, 
                                                    suministro_grit, 
                                                    fecha_grit)
                    if resultado_grit == True:
                        st.success('Se agregó el suministro de grit exitosamente', icon=':material/done_all:')

    #Se agrega la gestión medicamentos
    with st.container(border=True):
        if st.toggle('**Medicamentos**'):
            
            #Se crea pestaña para registrar medicamento suministrados a la camada
            #with tab_medicacion:
            st.write('Registra el suministro de medicamentos a tus aves')
            fecha_medicacion = st.date_input('Seleccione la fecha de suministro')
            df_tipos_mediacion = util.cosnultaQuery('SELECT * FROM PUBLIC.TIPO_MEDICAMENTO')
            tipo_medicamento = st.selectbox('Seleccione el tipo de medicamento suministrado', options=df_tipos_mediacion['tipo'].sort_values())
            tipo_medicamento_id = int(df_tipos_mediacion['id'][df_tipos_mediacion['tipo'] == tipo_medicamento].values[0])
            df_medicamentos = util.cosnultaQuery('SELECT * FROM PUBLIC.MEDICAMENTOS')
            df_medicamentos_aplicar = df_medicamentos[df_medicamentos['tipo'] == tipo_medicamento_id]
            medicamento_aplicado = st.selectbox('Seleccione el medicamento suministrado', options=df_medicamentos_aplicar['nombre'].sort_values())
            medicamento_aplicado_id = int(df_medicamentos_aplicar['id'][df_medicamentos_aplicar['nombre'] == medicamento_aplicado])
            dosis = int(df_medicamentos_aplicar['cant_dosis'][df_medicamentos_aplicar['nombre'] == medicamento_aplicado])
            dosis = range(1,dosis+1)
            dosis_medicamento = st.selectbox('Seleccione la dosis suministrada', options=dosis)
            cant_pollos_medicado = st.number_input('Ingrese el número de aves medicadas', min_value=1, step=1)
            if st.checkbox('Agregar información adicional'):
                lote_medicamento = st.text_input('Ingrese lote de la medicación')
                comentario_medicamento = st.text_area('Ingrese comentarios de la medicación')
                if st.button('Ingresar datos de medicación', key='btnMedicacion'):
                    resultado_medicacion = util.agregarMedicacion(camada_operar_id, 
                                                                medicamento_aplicado_id, 
                                                                dosis_medicamento, 
                                                                fecha_medicacion, 
                                                                cant_pollos_medicado, 
                                                                lote_medicamento, 
                                                                comentario_medicamento)
                    if resultado_medicacion == True:
                        st.success('Se agregó el suministro de medicación exitosamente', icon=':material/done_all:')
            else:    
                if st.button('Ingresar datos de medicación', key='btnMedicacion'):
                    resultado_medicacion = util.agregarMedicacion(camada_operar_id, tipo_medicamento_id, dosis_medicamento, fecha_medicacion, cant_pollos_medicado)
                    if resultado_medicacion == True:
                        st.success('Se agregó el suministro de medicación exitosamente', icon=':material/done_all:')

    ### Se agrega la gestión de la mortalidad
    with st.container(border=True):
        if st.toggle('**Mortalidad y descarte**'):
        
            # Se agrega la gestión de la mortalidad de los pollos en la camada
            tab_mortalidad, tab_descarte = st.tabs(['Mortalidad', 'Descarte'])
            with tab_mortalidad:
                cantidad_mortalidad = st.number_input('Ingrese la cantidad de aves muertas', min_value=1, step=1)
                df_causa_mortalidad = util.cosnultaQuery('SELECT * FROM public.causas_mortalidad ORDER BY causa_posible ASC ')
                causa_mortalidad = st.selectbox('Seleccione las posibles causas de muerte', options=df_causa_mortalidad['causa_posible'])
                causa_mortalidad_id = int(df_causa_mortalidad['id'][df_causa_mortalidad['causa_posible'] == causa_mortalidad].values[0])
                fecha_mortalidad = st.date_input('Ingrese fecha de la muerte', key='fechaMortalidad')
                if st.checkbox('Agregar comentario'):
                    comentario_mortalidad = st.text_area('Ingrese comentario:', max_chars=300)
                    if st.button('Ingresar datos de mortalidad', key='btnMortalidad'):
                        respuesta_mortalidad = util.agregarMuerte(camada_operar_id, 
                                                                fecha_mortalidad,
                                                                cantidad_mortalidad,
                                                                causa_mortalidad_id, 
                                                                comentario_mortalidad)
                        if respuesta_mortalidad == True:
                            st.success('Se registró los datos de mortalidad exitosamente', icon=':material/done_all:')
                else:
                    if st.button('Ingresar datos de mortalidad', key='btnMortalidad'):
                        respuesta_mortalidad = util.agregarMuerte(camada_operar_id, 
                                                                fecha_mortalidad,
                                                                cantidad_mortalidad,
                                                                causa_mortalidad_id)
                        if respuesta_mortalidad == True:
                            st.success('Se registró los datos de mortalidad exitosamente', icon=':material/done_all:')
                    

            # Se agrega la gestión de la descarte de los pollos en la camada
            with tab_descarte:
                cantidad_descarte = st.number_input('Ingrese la cantidad de aves descartadas', min_value=1, step=1)
                fecha_descarte = st.date_input('Ingrese fecha de la muerte', key='fechaDescarte')
                razon_descarte = st.text_area('Ingrese la razón de descarte')
                if st.button('Ingresar datos de descarte', key='btnDescarte'):
                    respuesta_descarte = util.agregarDescarte(camada_operar_id, 
                                                            razon_descarte, 
                                                            fecha_descarte, 
                                                            cantidad_descarte)
                    if respuesta_descarte == True:
                        st.success('Se registró los datos de descarte exitosamente', icon=':material/done_all:')
                

    ## Se agrega la gestión de los pesajes de los pollos de la camada
    with st.container(border=True):
        if st.toggle('**Pesajes**'):
            fecha_pesaje = st.date_input('Fecha del pesaje', key='fechaPesaje')
            tamano_muestra_pesaje = st.number_input('Indique la cantidad de pollos a pesar', min_value=1, step=1)
            pesos = []
            for i in range(tamano_muestra_pesaje):
                pesos.append( st.number_input(f'Ingrese el peso **en gramos** del pollo {i+1}', step=1, min_value=0, max_value=7000))
            promedio_pesaje= sum(pesos)/tamano_muestra_pesaje
            pesos_ =str(pesos)
            if st.button('Registrar pesaje', key='btnPesaje'):
                respuesta_pesaje = util.agregarPesaje(camada_operar_id, 
                                                    pesos_, 
                                                    fecha_pesaje, 
                                                    tamano_muestra_pesaje, 
                                                    promedio_pesaje)
                if respuesta_pesaje == True:
                    st.success('Se registró los datos de pesaje exitosamente', icon=':material/done_all:')



    ## Se agrega la gestión de los costos relacionados con la camada
    with st.container(border=True):
        if st.toggle('**Costos**'):
            df_proveedores = util.consultarProveedores(user_id)
            fecha_costo = st.date_input('Fecha de costo', key='fechaCosto')
            df_tipo_costo = util.cosnultaQuery('SELECT * FROM public.tipos_costos')
            tipo_costo = st.selectbox('Seleccione el tipo de costo', options=df_tipo_costo['tipo'].sort_values())
            tipo_costo_id = int(df_tipo_costo['id'][df_tipo_costo['tipo'] == tipo_costo].values[0])
            verificarProveedor(df_proveedores)
            proveedor_costo = st.selectbox('Seleccione el proveedor del servicio o producto', options=df_proveedores['Nombre'])
            proveedor_costo_id = int(df_proveedores['id'][df_proveedores['Nombre'] == proveedor_costo].values[0])
            valor_unitario_costo = st.number_input('Ingrese el valor unitario', min_value=0, step=1)
            cantidad_unidades_costo = st.number_input('Ingrese la cantidad', min_value=0, step=1)
            total_costo = valor_unitario_costo * cantidad_unidades_costo
            st.write(f'**TOTAL: ${format(total_costo,",")}**')
            if st.button('Registrar costos'):
                resultado_costo = util.agregarCosto(camada_operar_id, 
                                                    tipo_costo_id, 
                                                    proveedor_costo_id, 
                                                    valor_unitario_costo, 
                                                    cantidad_unidades_costo, 
                                                    total_costo, 
                                                    fecha_costo)
                if resultado_costo == True:
                    st.success('Se agregó el costo satisfactoriamente', icon=':material/done_all:')