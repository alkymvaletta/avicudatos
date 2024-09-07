import streamlit as st
import utilidades as util
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import analisisCamada as anaca
from datetime import datetime

# Se agrega logo
HORIZONTAL = 'src\images\horizontal_logo.png'

st.set_page_config(page_title='Avicudatos - Estadisticas de desempeño',page_icon='🐔')

st.logo(HORIZONTAL)

st.header('Avicudatos 🐔', divider='rainbow')

#Si no hay usuario registrado se va a Home
if 'usuario' not in st.session_state:
    st.switch_page('Home.py')

util.generarMenu(st.session_state['usuario'])

#Asignamos id del usuario a user_id
user_id = st.session_state['id_usuario']

if 'granjas' and 'galpon' in st.session_state:
    st.write('No hay sesion state en granja')
else:
    df_granjas, df_galpones = util.listaGranjaGalpones(user_id)

st.title('Estadistica de desempeño')



df_desempeno = util.datos_desempeno()

st.write('Vigila el desempeño de tus aves de acuerdo a los datos de referencia suministrados por cada una de las razas')


# Se crea visualización con filtros de razas y sexo de los pollos
with st.container(border=True):

    if st.toggle('Datos de referencia por razas'):
    
        # Creamos 3 columnas para establecer filtros
        col1, col2, col3 = st.columns(3)

        ## Creamos filtro para seleccionar rango de días
        with col1:
            dias = st.slider('Cuantos días deseas visualizar',
                        value=42,
                        min_value=df_desempeno['Edad en días'].min(), 
                        max_value=df_desempeno['Edad en días'].max())

        ## Creamos filtro para seleccionar Raza
        with col2:
            raza = st.selectbox('Seleccione las raza', df_desempeno['Raza'].unique())

        ## Creamos filtro para seleccionar Sexo
        with col3:
            sexo = st.selectbox('Seleccione el sexo', df_desempeno['sexo'].unique())
        
        # Se crea df de acuerdo a los filtros seleccionados
        df_filtrado = df_desempeno[
                    ((df_desempeno['Edad en días']).isin(range(0, dias + 1))) &
                    (df_desempeno['Raza'] == raza) &
                    (df_desempeno['sexo'] == sexo)
                    ]
        
        ### Gráfica de consumo de alimento y el peso
        
        fig_consumo_peso = go.Figure()
        
        #Se agrega trazo de los datps de referencia Consumo alimento acumulado
        fig_consumo_peso.add_trace(go.Line(x=df_filtrado['Edad en días'], 
                                        y=df_filtrado['Consumo alimento acumulado'],
                                        name = 'Alimento',
                                        line =(dict(color='firebrick', width=2))))
        
        #Se agrega trazo de los datps de referencia de Peso
        fig_consumo_peso.add_trace(go.Line(x=df_filtrado['Edad en días'], 
                                        y=df_filtrado['Peso'],
                                        name = 'Peso',
                                        line =(dict(color='green', width=2, dash = 'dot'))))
        
        fig_consumo_peso.update_layout(title= 'Evolución Consumo de Alimento y Ganancia de Peso Acumulado',
                                    xaxis_title='Dias del ave',
                                    yaxis_title= 'Gramos')
        
        st.plotly_chart(fig_consumo_peso)
        #st.plotly_chart(fig_cosumo)
        
        if st.checkbox('Tabla datos de referencia'):
            st.dataframe(df_filtrado[['Edad en días', 'Peso', 'Consumo alimento acumulado', 'Raza', 'CA']], hide_index=True, use_container_width=True)

# Se crea función para mergear camada y galpon en el mismo DF
def unirCamadaGalpon(user_id):
    df_camadas = util.consultarCamadasActiva(user_id)
    df_camadas_merged = pd.merge(df_camadas, df_galpones, how='left', left_on='galpon_id', right_on='galpon_id')
    df_camadas_merged = df_camadas_merged.rename(columns={'cantidad':'Ingresados', 'fecha_inicio':'Fecha ingreso', 'fecha_estimada_sacrificio':'Sacrificio estimado', 'muertes':'Muertes', 'descartes':'Descartes', 'faenados':'Sacrificados'})
    df_camadas_merged['Fecha ingreso'] = pd.to_datetime(df_camadas_merged['Fecha ingreso']).dt.date
    df_camadas_merged['Dias'] = (datetime.now().date() - df_camadas_merged['Fecha ingreso']).apply(lambda x: x.days)
    df_camadas_merged['Disponibles'] =df_camadas_merged['Ingresados'] - df_camadas_merged['Muertes'] - df_camadas_merged['Descartes'] - df_camadas_merged['Sacrificados']
    df_camadas_merged['galponEingreso'] = ' Ingresado el ' + df_camadas_merged['Fecha ingreso'].map(str) + ' en el galpón '+ df_camadas_merged['Galpón'].map(str)
    return df_camadas_merged

########## Por terminar
with st.container(border=True):
    if st.toggle('Comparación de desempeño'):
        df_camadas_comparar = unirCamadaGalpon(user_id)
        
        if df_camadas_comparar.shape[0] == 0:
            st.info('Aún no haz registrado costos asociados a tu camada', icon=':material/notifications:')
        
        else:
            camada_comparar = st.selectbox('Selecciona la camada a comparar', options=df_camadas_comparar['galponEingreso'])
            camada_comparar_id = int(df_camadas_comparar['id'][df_camadas_comparar['galponEingreso'] == camada_comparar].values[0])
            df_promedio_pesos = util.cosnultaQuery(f'''
                                                    SELECT *
                                                    FROM PUBLIC.PROMEDIO_MEDICIONES_PESOS
                                                    WHERE CAMADA_ID = {camada_comparar_id}
                                                    ORDER BY FECHA ASC
                                                    ''')
            
            df_promedio_alimento = util.cosnultaQuery(f'''
                                                        SELECT ALIMENTO.CAMADA_ID,
                                                            ALIMENTO.PESO,
                                                            ALIMENTO.TIPO_ALIMENTO,
                                                            ALIMENTO.FECHA,
                                                            ALIMENTO.HORA,
                                                            CAMADA.FECHA_INICIO,
                                                            CAMADA.CANTIDAD,
                                                            SUM(ALIMENTO.PESO) OVER (PARTITION BY ALIMENTO.CAMADA_ID ORDER BY ALIMENTO.FECHA, ALIMENTO.HORA) AS PESO_ACUMULADO,
                                                            SUM(ALIMENTO.PESO) OVER (PARTITION BY ALIMENTO.CAMADA_ID ORDER BY ALIMENTO.FECHA, ALIMENTO.HORA) * 1000 / CAMADA.CANTIDAD AS CONSUMO_PROMEDIO,
                                                            (ALIMENTO.FECHA - CAMADA.FECHA_INICIO) AS DIAS
                                                        FROM PUBLIC.ALIMENTO
                                                        JOIN PUBLIC.CAMADA ON CAMADA.ID = ALIMENTO.CAMADA_ID
                                                        WHERE CAMADA_ID = {camada_comparar_id}
                                                        ORDER BY ALIMENTO.FECHA, ALIMENTO.HORA
                                                    ''')
            
            if (df_promedio_pesos.shape[0] == 0) and (df_promedio_alimento.shape[0]== 0):
                st.warning('Aún no registras datos para ofrecer una comparación de desempeño', icon=':material/error:')
            
            else:
                #Se agrega columna con fecha de ingreso de la camada seleccionada
                df_promedio_pesos['ingreso'] = df_camadas_comparar['Fecha ingreso'].values[0]
                
                df_promedio_pesos['dias'] = (df_promedio_pesos['fecha'] - df_promedio_pesos['ingreso']).apply(lambda x: x.days)
                dias_comparacion_peso = df_promedio_pesos['dias'].max()
                
                dias_comparacion_peso
                if dias_comparacion_peso != None:
                    
                    # Buscamos el máximo peso de comparación
                    peso_maximo = df_promedio_pesos['promedio'][df_promedio_pesos['dias'] == dias_comparacion_peso].values[0]
                    
                    #Dataframe de datos de referencia de de acuerdo a raza y días
                    df_desempeno_comp = df_desempeno[['Edad en días', 'Peso']][(df_desempeno['raza_id'] == (df_camadas_comparar['raza'][df_camadas_comparar['id'] == camada_comparar_id]).values[0]) &
                                                                                                            (df_desempeno['sexo'] == 'mixto') &
                                                                                                            (df_desempeno['Edad en días'] <= dias_comparacion_peso)]
                    
                    # Buscamos el peso de comparación de referencia
                    peso_referencia = df_desempeno['Peso'][df_desempeno['Edad en días'] == dias_comparacion_peso].values[0]
                    
                    #Creamos la figura a la cual se va a comparar el PESO
                    fig_comparacion_desempeno_peso = go.Figure()
                    
                    # Se agrega trazo de datos promedio
                    fig_comparacion_desempeno_peso.add_trace(go.Line(x=df_promedio_pesos['dias'],
                                                                y = df_promedio_pesos['promedio'],
                                                                name = 'Ganancia',
                                                                line = (dict(color='firebrick', width =2))))
                    
                    # Se agrega trazo de de datos de desempeño
                    fig_comparacion_desempeno_peso.add_trace(go.Line(x=df_desempeno_comp['Edad en días'],
                                                                y = df_desempeno_comp['Peso'],
                                                                name = 'Referencia',
                                                                line = (dict(color='green', width =2, dash='dot'))))
                    
                    # Se agrega nombre de ejes y nombres
                    fig_comparacion_desempeno_peso.update_layout( title='Ganancia de peso y datos de referencia',
                                                            xaxis_title = 'Días del ave',
                                                            yaxis_title = 'Gramos')
                    
                    st.plotly_chart(fig_comparacion_desempeno_peso)
                    
                    if peso_maximo < peso_referencia:
                        st.write(f'''
                                La ganancia de peso de repecto a los datos de refencia de la raza se encuentran 
                                    :red[**{peso_referencia -peso_maximo} gramos
                                    por debajo**] del peso de referencia, lo que equivale a **{round((peso_referencia - peso_maximo)/peso_referencia, 4) * 100}%**''')
                    else:
                        st.write(f'''La ganancia de peso de repecto a los datos de refencia de la raza se encuentran 
                                    :green[**{ peso_maximo - peso_referencia} gramos
                                    por encima**] del peso de referencia, lo que equivale a **{round((peso_maximo - peso_referencia)/peso_referencia, 4) * 100}%**''')
                    
                    #Creamos la figura a la cual se va a comparar el CONSUMO ALIMENTO
                    
                    dias_comparacion_alimento = df_promedio_alimento['dias'].max()

                    df_desempeno_comp_alimento = df_desempeno[['Edad en días', 'Consumo alimento acumulado']][(df_desempeno['raza_id'] == (df_camadas_comparar['raza'][df_camadas_comparar['id'] == camada_comparar_id]).values[0]) &
                                                                                                            (df_desempeno['sexo'] == 'mixto') &
                                                                                                            (df_desempeno['Edad en días'] <= dias_comparacion_alimento)]
                    
                    fig_comparacion_desempeno_alimento = go.Figure()
                    
                    # Se agrega trazo de datos promedio usuario
                    fig_comparacion_desempeno_alimento.add_trace(go.Line(x=df_promedio_alimento['dias'],
                                                                y = df_promedio_alimento['consumo_promedio'],
                                                                name = 'Consumo',
                                                                line = (dict(color='firebrick', width =2))))
                    
                    #df_desempeno_comp
                    
                    # Se agrega trazo de de datos de desempeño
                    fig_comparacion_desempeno_alimento.add_trace(go.Line(x=df_desempeno_comp_alimento['Edad en días'],
                                                                y = df_desempeno_comp_alimento['Consumo alimento acumulado'],
                                                                name = 'Referencia',
                                                                line = (dict(color='green', width =2, dash='dot'))))
                    
                    # Se agrega nombre de ejes y nombres
                    fig_comparacion_desempeno_alimento.update_layout( title='Consumo de alimento acumulado y datos de referencia',
                                                            xaxis_title = 'Días del ave',
                                                            yaxis_title = 'Gramos')
                    
                    st.plotly_chart(fig_comparacion_desempeno_alimento)
                    
                    alimento_referencia = df_desempeno_comp_alimento['Consumo alimento acumulado'].max()
                    alimento_maximo = float(df_promedio_alimento['consumo_promedio'].max())
                    

                    if alimento_maximo < alimento_referencia:
                        st.write(f'''
                                El consumo de alimento de las aves repecto a los datos de refencia de la raza se encuentran 
                                    :red[**{round(alimento_referencia -alimento_maximo, 2)} gramos
                                    por debajo**] del peso de referencia, lo que equivale a **{round((alimento_referencia - alimento_referencia)/alimento_referencia, 4) * 100}%**''')
                    else:
                        st.write(f'''La ganancia de peso de repecto a los datos de refencia de la raza se encuentran 
                                    :green[**{ round(alimento_maximo - alimento_referencia,2)} gramos
                                    por encima**] del peso de referencia, lo que equivale a **{round((alimento_maximo - peso_referencia)/alimento_referencia, 4) * 100}%**''')
                #st.write()

# Análisis de las camadas
with st.container(border=True):
    if st.toggle('Análisis de tus camadas'):
        # Selecciona la camada que se va a analisar
        
        df_camadas_merged = unirCamadaGalpon(user_id)
        
        if df_camadas_merged.shape[0] != 0:
        
            camada_evualuar = st.selectbox('Selecciona la camada', options=df_camadas_merged['galponEingreso'])
            camada_evualuar_id = int(df_camadas_merged['id'][df_camadas_merged['galponEingreso'] == camada_evualuar])
            
            anaca.analisisCamadas(camada_evualuar_id, False)

# Histórico de las camadas
with st.container(border=True):
    if st.toggle('Histórico de tus camadas'):
        df_camadas_finalizadas = util.camadasFinalizadas(user_id)
        df_camadas_finalizadas['galponEingreso'] = ' Ingresado el ' + df_camadas_finalizadas['fecha_inicio'].map(str) +' en la granja '+df_camadas_finalizadas['Granja'].map(str) +' en el galpón '+ df_camadas_finalizadas['Galpón'].map(str)
        
        #Manejo de errores si no se han finalizado camadas
        if df_camadas_finalizadas.shape[0] == 0:
            st.info('Aún no haz fianlizado camadas. Vuelve más adelante', icon=':material/notifications:')
        
        else:
            camada_historial = st.selectbox('Seleccione la camada para ver su histórico', options=df_camadas_finalizadas['galponEingreso'])
            camada_historial_id = int(df_camadas_finalizadas['camada_id'][df_camadas_finalizadas['galponEingreso'] == camada_historial])           
            
            anaca.analisisCamadas(camada_historial_id, True)