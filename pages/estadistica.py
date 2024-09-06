import streamlit as st
import utilidades as util
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

@st.cache_data(ttl='1d')
def datos_desempeno():
    # Conectamos con la database
    conn, c  = util.conectarDB()
    # Extraemos los datos de DB con base al query
    c.execute('''SELECT EDAD_EN_DIAS,
                    PESO,
                    CONSUMO_ALIMENTOS_ACUMULADO,
                    GANANCIA,
                    CONVERSION_ALIMENTICIA_ACUMULADA AS "CA",
                    raza_id,
                    RAZAS.NOMBRE AS "Raza",
                    SEXOS_AVES.SEXO
                FROM PUBLIC.OBJETIVOS_DESEMPENO
                LEFT JOIN PUBLIC.RAZAS ON RAZAS.ID = OBJETIVOS_DESEMPENO.RAZA_ID
                LEFT JOIN PUBLIC.SEXOS_AVES ON SEXOS_AVES.ID = OBJETIVOS_DESEMPENO.ID_SEXO''')
    resultados = c.fetchall()
    columnas = [desc[0] for desc in c.description]
    df_desempeno = pd.DataFrame(resultados, columns=columnas)
    df_desempeno.rename(columns={'edad_en_dias':'Edad en días', 'peso':'Peso', 'consumo_alimentos_acumulado':'Consumo alimento acumulado'}, inplace=True)
    return df_desempeno

df_desempeno = datos_desempeno()

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
    df_camadas = util.consultarCamadas(user_id)
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
            
            # Datos de camada de comparación
            camada_ingreso = df_camadas_merged['Fecha ingreso'].iloc[0]
            camada_granja = df_camadas_merged['Granja'].iloc[0]
            camada_galpon = df_camadas_merged['Galpón'].iloc[0]
            camada_capacidad = df_camadas_merged['Capacidad'].iloc[0]
            camada_ingresados = df_camadas_merged['Ingresados'].iloc[0]
            camada_dias = df_camadas_merged['Dias'].iloc[0]
            camada_muerte = df_camadas_merged['Muertes'].iloc[0]
            camada_descarte = df_camadas_merged['Descartes'].iloc[0]
            camada_sacrificio = df_camadas_merged['Sacrificados'].iloc[0]
            camada_raza = df_camadas_merged['raza'].iloc[0]
            
            st.write(f'''La camada se ingresó el **{camada_ingreso}** encuentra en la granja **{camada_granja}** en el galpón **{camada_galpon}** 
                    que tiene una capacidad de **{camada_capacidad}** aves. Se ingresaron un total de **{camada_ingresados}** y llevan 
                    **{camada_dias}** dias, en los cuales han muerto **{camada_muerte}** y se han descartado **{camada_descarte}** aves. 
                    Hasta la fecha se han sacrificado **{camada_sacrificio}**''')
        
            
            # Se establecen columnas para las métricas.
            st.divider()
            
            st.subheader('Análisis Zootécnicos')
            metr1, metr2, metr3, metr4 = st.columns(4)
            
            # Mortalidad
            with metr1:
                mortalidad = round((df_camadas_merged['Muertes'][df_camadas_merged['id'] == camada_evualuar_id] )/ (df_camadas_merged['Ingresados'][df_camadas_merged['id'] == camada_evualuar_id]),4)*100
                st.metric('Mortalidad', value= f'{float(mortalidad)} %')
            
            #Conversión Alimenticia - CA = Consumo Alimento Promedio / Peso Prom
            with metr2: 
                df_consumo_alimento = util.cosnultaQuery(f'''SELECT SUM(PESO) AS TOTAL_ALIMENTO
                                                            FROM PUBLIC.ALIMENTO
                                                            WHERE (CAMADA_ID = {camada_evualuar_id})
                                                            ''')
                df_promedio_pesos = util.cosnultaQuery(f'''SELECT PROMEDIO
                                                            FROM PUBLIC.PROMEDIO_MEDICIONES_PESOS
                                                            WHERE FECHA =
                                                                    (SELECT MAX(FECHA)
                                                                        FROM PUBLIC.PROMEDIO_MEDICIONES_PESOS
                                                                        WHERE CAMADA_ID = {camada_evualuar_id})''')
                
                #Traemos la referencia de CA de acuerdo a los días transcurridos
                CA_referencia = df_desempeno['CA'][(df_desempeno['Edad en días'] == camada_dias) & 
                                                    (df_desempeno['raza_id'] == camada_raza) &
                                                    (df_desempeno['sexo'] == 'mixto')].iloc[0]
                
                if (df_consumo_alimento.shape[0] == 0) or (df_promedio_pesos.shape[0] == 0):
                    st.metric('Conv. Alimenticia - CA', 'NaN')
                    CA = None
                else:
                    #Peso promedio de las aves
                    peso_promedio = float(df_promedio_pesos.values[0])/1000
                    
                    # Consumo promedio de aves ingresadas
                    consumo_promedio = float(round(df_consumo_alimento['total_alimento'].values[0]/df_camadas_merged['Ingresados'].values[0], 4))
                    
                    # Calculo de la conversión alimenticia
                    CA = round(consumo_promedio / peso_promedio, 4)
                    CA_diferencia = round(CA-CA_referencia, 4)
                    st.metric('Conv. Alimenticia - CA', CA, CA_diferencia, delta_color='inverse')
                    
            
        
            # Eficiencia Alimenticia - EA = Peso Prom / Conversión Alimenticia 
            with metr3:
                if (CA == None) or (df_promedio_pesos.shape[0] == 0) :
                    st.metric('Ef. Alimenticia - EA', 'NaN')
                    EA = None
                else:
                    EA = round(peso_promedio / CA, 4)
                    st.metric('Ef. Alimenticia - EA', EA)
            
            # Indice de Productividad - IP = Eficiencia Alimenticia / Conversión Alimenticia
            with metr4:
                if (CA == None) or (EA == None):
                    st.metric('Indice Productividad - IP', 'NaN')
                else:
                    IP = round(EA / CA, 4)
                    st.metric('Indice Productividad - IP', IP)
            st.divider()
            
            st.subheader('Análisis Económico')
            metr5, metr6, metr7, metr8 = st.columns(4)
            
            # Total costos
            with metr5:
                df_costo_total = util.cosnultaQuery(f'''SELECT SUM(COSTO_TOTAL)
                                            FROM PUBLIC.COSTOS
                                            WHERE CAMADA_ID = {camada_evualuar_id}
                                        ''')
                if df_costo_total.values[0] == None:
                    st.metric('Total costos', value = 0)
                    costo_total = 0
                else:
                    costo_total = int(df_costo_total.values[0])
                    st.metric('Total costos', value = f'${format(round(costo_total/1000000, 3), ",")} M')
            
            # total ventas
            with metr6:
                df_valor_venta = util.cosnultaQuery(f'''
                                                SELECT SUM(PRECIO_TOTAL) AS TOTAL
                                                FROM PUBLIC.VENTAS
                                                WHERE CAMADA_ID = {camada_evualuar_id}
                                                ''')
                
                if df_valor_venta.values[0] == None:
                    st.metric('Total Ventas',value= 0)
                    valor_venta = 0
                else:
                    valor_venta = int(df_valor_venta.values[0])
                    st.metric('Total Ventas',value= f'${format(round(valor_venta/1000000, 3) , ",")} M')
            
            #Utilidades
            with metr7:
                st.metric('Utilidad Total', value= f'${format(round((valor_venta-costo_total)/1000000, 3), ",")} M')
            
            #Porcentaje de utilidades
            with metr8:
                if valor_venta == 0:
                    
                    st.metric('Porcentaje Utilidad', value= f'{0} %')
                else:
                    utilidad = (valor_venta-costo_total)/valor_venta
                    utilidad = round(utilidad * 100, 3)
                    st.metric('Porcentaje Utilidad', value= f'{utilidad} %')
            
            st.divider()
            
            st.subheader('Mortalidad y Descarte')
            
            ### Se hace grafico st.scatter_chart donde muestre las muertes en un color y los descartes en otro
            ### donde se vea las muertes de las aves
            
            df_mortalidad, df_descarte, df_mortalidad_descarte = util.buscarMortalidad_descarte(camada_evualuar_id)
            
            # Se aplica mensaje en caso de que no se haya presentado mortalidad o descarte
            if (df_mortalidad.shape[0] == 0 ) and (df_descarte.shape[0] == 0):
                st.info('Aún no haz registrado mortalidad o descartes en tu camada')

            else:
                
                df_mortalidad_agg = df_mortalidad.groupby('Causa')['Mortalidad'].sum().reset_index().sort_values(by='Mortalidad', ascending=False)
                
                suma_mortalidad= df_mortalidad_descarte['Mortalidad'].values.sum()
                suma_descarte= df_mortalidad_descarte['Descarte'].values.sum()
                
                # Si hay eventos en mortalidad y descarte
                if (suma_mortalidad > 0) and (suma_descarte > 0):
                    fig_mortalidad_descarte = px.scatter(df_mortalidad_descarte, 
                                                        x = 'fecha', 
                                                        y=['Mortalidad', 'Descarte'],
                                                        )
                    
                    #Se grafica scatter de mortalidad y descarte
                    st.plotly_chart(fig_mortalidad_descarte, use_container_width=True)

                # Si solo se ha presentado mortalidad
                elif suma_mortalidad > 0:
                    fig_mortalidad_descarte = px.scatter(df_mortalidad_descarte, 
                                                        x = 'fecha', 
                                                        y='Mortalidad',
                                                        )
                    
                    #Se grafica scatter de mortalidad y descarte
                    st.plotly_chart(fig_mortalidad_descarte, use_container_width=True)
                
                # Si solo se ha presentado descarte
                elif suma_descarte > 0:
                    fig_mortalidad_descarte = px.scatter(df_mortalidad_descarte, 
                                                        x = 'fecha', 
                                                        y='Descarte',
                                                        )
                    
                    #Se grafica scatter de mortalidad y descarte
                    st.plotly_chart(fig_mortalidad_descarte, use_container_width=True)
                
                #Se hace la gráfica de barras de mortalidad
                fig_mortalidad = px.bar(df_mortalidad_agg,
                                x='Causa',
                                y='Mortalidad',
                                color = 'Causa',
                                text_auto=True, #Muestra el valor de la columna
                                color_discrete_sequence= px.colors.qualitative.D3,
                                title='Causas de Mortalidad'
                            )
                st.plotly_chart(fig_mortalidad, use_container_width=True)

                #Se hace grafica de pie de distribución de mortalidad
                fig_distribucion_mortalidad = px.pie(df_mortalidad_agg,
                                values='Mortalidad',
                                names='Causa',
                                color_discrete_sequence= px.colors.qualitative.D3,
                                title='Distribución de Causas de Mortalidad'
                            )
                st.plotly_chart(fig_distribucion_mortalidad, use_container_width=True)
                
            st.divider()
            
            # Se hace Análisis de los Costos
            st.subheader('Análisis de Costos')
            
            @st.cache_data(ttl=180)
            
            def consultarCostosCamada():
                df_costosCamada = util.cosnultaQuery(f'''
                                                    SELECT CAMADA_ID,
                                                        TIPO_ID,
                                                        TIPO as "Tipo",
                                                        PROVEEDOR_ID,
                                                        COSTO_UNITARIO,
                                                        CANTIDAD,
                                                        COSTO_TOTAL as "Costo Total",
                                                        FECHA
                                                    FROM PUBLIC.COSTOS
                                                    JOIN PUBLIC.TIPOS_COSTOS ON TIPOS_COSTOS.ID = COSTOS.TIPO_ID
                                                    WHERE CAMADA_ID = {camada_evualuar_id}
                                                    ''')
                
                df_costoCamada_agg = df_costosCamada.groupby('Tipo')['Costo Total'].sum().reset_index().sort_values(by='Costo Total', ascending=False)
                
                return df_costosCamada, df_costoCamada_agg
            
            df_costosCamada, df_costoCamada_agg = consultarCostosCamada()
            
            # Se aplica mensaje si NO hay costos registrados
            if df_costosCamada.shape[0] == 0:
                st.info('Aún no haz registrado costos asociados a tu camada', icon=':material/notifications:')
            
            else:
                fig_costos = px.bar(df_costoCamada_agg,
                                    x= 'Tipo',
                                    y= 'Costo Total',
                                    color = 'Tipo',
                                    color_discrete_sequence= px.colors.qualitative.D3,
                                    text_auto=True,
                                    title='Constos de producción de camada')
                
                st.plotly_chart(fig_costos, use_container_width=True)
                
                fig_pie_costos = px.pie(df_costoCamada_agg,
                                    names= 'Tipo',
                                    values= 'Costo Total',
                                    color = 'Tipo',
                                    color_discrete_sequence= px.colors.qualitative.D3,
                                    title= 'Distribución de los costos de producción')
                
                st.plotly_chart(fig_pie_costos, use_container_width=True)
        
            st.divider()
                
            st.subheader('Análisis de Ventas')
                
            df_ventas_camadas = util.cosnultaQuery(f'''
                                                SELECT VENTAS.CAMADA_ID,
                                                    TIPO_PRESAS.NOMBRE,
                                                    SUM(PRECIO_TOTAL) AS "Total Ventas"
                                                FROM PUBLIC.VENTAS
                                                JOIN PUBLIC.TIPO_PRESAS ON TIPO_PRESAS.ID = VENTAS.PRESA
                                                WHERE CAMADA_ID = {camada_evualuar_id}
                                                GROUP BY VENTAS.CAMADA_ID, TIPO_PRESAS.NOMBRE
                                                ''')
            if df_ventas_camadas.shape[0] == 0:
                st.info('Aún no haz registrado ventas en tu camada', icon=':material/notifications:')
            
            else:
                st.write('sss')
        
        else:
            st.info('Aún no haz registrado mortalidad o descartes en tu camada', icon=':material/notifications:')

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
            df_mortalidad_his, df_descarte_his, df_mortalidad_descarte_his = util.buscarMortalidad_descarte(camada_historial_id)
            #df_mortalidad_his, df_descarte_his, df_mortalidad_descarte_his
            
            def unirCamadaGalpon(user_id):
                df_camadas = util.consultarCamadas(user_id)
                df_camadas_merged = pd.merge(df_camadas, df_galpones, how='left', left_on='galpon_id', right_on='galpon_id')
                df_camadas_merged = df_camadas_merged.rename(columns={'cantidad':'Ingresados', 'fecha_inicio':'Fecha ingreso', 'fecha_estimada_sacrificio':'Sacrificio estimado', 'muertes':'Muertes', 'descartes':'Descartes', 'faenados':'Sacrificados'})
                df_camadas_merged['Fecha ingreso'] = pd.to_datetime(df_camadas_merged['Fecha ingreso']).dt.date
                df_camadas_merged['Dias'] = (datetime.now().date() - df_camadas_merged['Fecha ingreso']).apply(lambda x: x.days)
                df_camadas_merged['Disponibles'] =df_camadas_merged['Ingresados'] - df_camadas_merged['Muertes'] - df_camadas_merged['Descartes'] - df_camadas_merged['Sacrificados']
                df_camadas_merged['galponEingreso'] = ' Ingresado el ' + df_camadas_merged['Fecha ingreso'].map(str) + ' en el galpón '+ df_camadas_merged['Galpón'].map(str)
                return df_camadas_merged
            
            
            def analisisCamadas(camada_id, df_camadas, df_desempeno):
    
                df_costos_camadas, df_ventas_camadas, df_ventas_dias_camadas = util.costos_ventas_Camadas(camada_id)

                st.divider()

                st.subheader('Análisis Zootécnicos')

                df_camadas_merged = unirCamadaGalpon(user_id)

                camada_ingreso = df_camadas_merged['Fecha ingreso'].iloc[0]
                camada_granja = df_camadas_merged['Granja'].iloc[0]
                camada_galpon = df_camadas_merged['Galpón'].iloc[0]
                camada_capacidad = df_camadas_merged['Capacidad'].iloc[0]
                camada_ingresados = df_camadas_merged['Ingresados'].iloc[0]
                camada_dias = df_camadas_merged['Dias'].iloc[0]
                camada_muerte = df_camadas_merged['Muertes'].iloc[0]
                camada_descarte = df_camadas_merged['Descartes'].iloc[0]
                camada_sacrificio = df_camadas_merged['Sacrificados'].iloc[0]
                camada_raza = df_camadas_merged['raza'].iloc[0]

                st.write(f'''La camada se ingresó el **{camada_ingreso}** encuentra en la granja **{camada_granja}** en el galpón **{camada_galpon}** 
                    que tiene una capacidad de **{camada_capacidad}** aves. Se ingresaron un total de **{camada_ingresados}** y llevan 
                    **{camada_dias}** dias, en los cuales han muerto **{camada_muerte}** y se han descartado **{camada_descarte}** aves. 
                    Hasta la fecha se han sacrificado **{camada_sacrificio}**''')

                metr1, metr2, metr3, metr4 = st.columns(4)

                # Mortalidad
                with metr1:
                    mortalidad = round((df_camadas['Muertes'][df_camadas['camada_id'] == camada_id] )/ (df_camadas['Ingresados'][df_camadas['camada_id'] == camada_id]),4)*100
                    st.metric('Mortalidad', value= f'{float(mortalidad)} %')

                #Conversión Alimenticia - CA = Consumo Alimento Promedio / Peso Prom
                with metr2: 
                    df_consumo_alimento = util.cosnultaQuery(f'''SELECT SUM(PESO) AS TOTAL_ALIMENTO
                                                                FROM PUBLIC.ALIMENTO
                                                                WHERE (CAMADA_ID = {camada_id})
                                                                ''')
                    
                    df_promedio_pesos = util.cosnultaQuery(f'''SELECT PROMEDIO
                                                                FROM PUBLIC.PROMEDIO_MEDICIONES_PESOS
                                                                WHERE FECHA =
                                                                        (SELECT MAX(FECHA)
                                                                            FROM PUBLIC.PROMEDIO_MEDICIONES_PESOS
                                                                            WHERE CAMADA_ID = {camada_id})''')
                    
                    #Traemos la referencia de CA de acuerdo a los días transcurridos
                    CA_referencia = df_desempeno['CA'][(df_desempeno['Edad en días'] == camada_dias) & 
                                                        (df_desempeno['raza_id'] == camada_raza) &
                                                        (df_desempeno['sexo'] == 'mixto')].iloc[0]
                    
                    if (df_consumo_alimento.shape[0] == 0) or (df_promedio_pesos.shape[0] == 0):
                        st.metric('Conv. Alimenticia - CA', 'NaN')
                        CA = None
                    else:
                        #Peso promedio de las aves
                        peso_promedio = float(df_promedio_pesos.values[0])/1000
                        # Consumo promedio de aves ingresadas
                        consumo_promedio = float(round(df_consumo_alimento['total_alimento'].values[0]/df_camadas['Ingresados'].values[0], 4))
                        
                        # Calculo de la conversión alimenticia
                        CA = round(consumo_promedio / peso_promedio, 4)
                        CA_diferencia = round(CA-CA_referencia, 4)
                        st.metric('Conv. Alimenticia - CA', CA, CA_diferencia, delta_color='inverse')

                # Eficiencia Alimenticia - EA = Peso Prom / Conversión Alimenticia 
                with metr3:
                    if (CA == None) or (df_promedio_pesos.shape[0] == 0) :
                        st.metric('Ef. Alimenticia - EA', 'NaN')
                        EA = None
                    else:
                        EA = round(peso_promedio / CA, 4)
                        st.metric('Ef. Alimenticia - EA', EA)

                # Indice de Productividad - IP = Eficiencia Alimenticia / Conversión Alimenticia
                with metr4:
                    if (CA == None) or (EA == None):
                        st.metric('Indice Productividad - IP', 'NaN')
                    else:
                        IP = round(EA / CA, 4)
                        st.metric('Indice Productividad - IP', IP)
                st.divider()

                st.subheader('Análisis Económico')
                metr5, metr6, metr7, metr8 = st.columns(4)

                # Total costos
                with metr5:
                    df_costo_total = util.cosnultaQuery(f'''SELECT SUM(COSTO_TOTAL)
                                                FROM PUBLIC.COSTOS
                                                WHERE CAMADA_ID = {camada_id}
                                            ''')
                    if df_costo_total.values[0] == None:
                        st.metric('Total costos', value = 0)
                        costo_total = 0
                    else:
                        costo_total = int(df_costo_total.values[0])
                        st.metric('Total costos', value = f'${format(round(costo_total/1000000, 3), ",")} M')

                # total ventas
                with metr6:
                    df_valor_venta = util.cosnultaQuery(f'''
                                                    SELECT SUM(PRECIO_TOTAL) AS TOTAL
                                                    FROM PUBLIC.VENTAS
                                                    WHERE CAMADA_ID = {camada_id}
                                                    ''')
                    
                    if df_valor_venta.values[0] == None:
                        st.metric('Total Ventas',value= 0)
                        valor_venta = 0
                    else:
                        valor_venta = int(df_valor_venta.values[0])
                        st.metric('Total Ventas',value= f'${format(round(valor_venta/1000000, 3) , ",")} M')

                #Utilidades
                with metr7:
                    st.metric('Utilidad Total', value= f'${format(round((valor_venta-costo_total)/1000000, 3), ",")} M')

                #Porcentaje de utilidades
                with metr8:
                    if valor_venta == 0:
                        
                        st.metric('Porcentaje Utilidad', value= f'{0} %')
                    else:
                        utilidad = (valor_venta-costo_total)/valor_venta
                        utilidad = round(utilidad * 100, 3)
                        st.metric('Porcentaje Utilidad', value= f'{utilidad} %')

                st.divider()

                st.subheader('Mortalidad y Descarte')

                df_mortalidad, df_descarte, df_mortalidad_descarte = util.buscarMortalidad_descarte(camada_id)

                # Se aplica mensaje en caso de que no se haya presentado mortalidad o descarte
                if (df_mortalidad.shape[0] == 0 ) and (df_descarte.shape[0] == 0):
                    st.info('Aún no haz registrado mortalidad o descartes en tu camada')

                else:
                    
                    df_mortalidad_agg = df_mortalidad.groupby('Causa')['Mortalidad'].sum().reset_index().sort_values(by='Mortalidad', ascending=False)
                    
                    suma_mortalidad= df_mortalidad['Mortalidad'].values.sum()
                    suma_descarte= df_descarte['Descarte'].values.sum()
                    
                    # Si hay eventos en mortalidad y descarte
                    if (suma_mortalidad > 0) and (suma_descarte > 0):
                        
                        fig_mortalidad_descarte = px.scatter(df_mortalidad_descarte, 
                                                            x = 'fecha', 
                                                            y=['Mortalidad', 'Descarte'],
                                                            title= 'Eventos de mortalidad y descarte'
                                                            )
                        
                        #Se grafica scatter de mortalidad y descarte
                        st.plotly_chart(fig_mortalidad_descarte, use_container_width=True)

                    # Si solo se ha presentado mortalidad
                    elif suma_mortalidad > 0:
                        fig_mortalidad_descarte = px.scatter(df_mortalidad_descarte, 
                                                            x = 'fecha', 
                                                            y='Mortalidad',
                                                            title= 'Eventos de mortalidad y descarte'
                                                            )
                        
                        #Se grafica scatter de mortalidad y descarte
                        st.plotly_chart(fig_mortalidad_descarte, use_container_width=True)
                    
                    # Si solo se ha presentado descarte
                    elif suma_descarte > 0:
                        fig_mortalidad_descarte = px.scatter(df_mortalidad_descarte, 
                                                            x = 'fecha', 
                                                            y='Descarte',
                                                            title= 'Eventos de mortalidad y descarte'
                                                            )
                        
                        #Se grafica scatter de mortalidad y descarte
                        st.plotly_chart(fig_mortalidad_descarte, use_container_width=True)
                    
                    #Se hace la gráfica de barras de mortalidad
                    fig_mortalidad = px.bar(df_mortalidad_agg,
                                    x='Causa',
                                    y='Mortalidad',
                                    color = 'Causa',
                                    text_auto=True, #Muestra el valor de la columna
                                    color_discrete_sequence= px.colors.qualitative.D3,
                                    title='Causas de Mortalidad'
                                )
                    st.plotly_chart(fig_mortalidad, use_container_width=True)

                    #Se hace grafica de pie de distribución de mortalidad
                    fig_distribucion_mortalidad = px.pie(df_mortalidad_agg,
                                    values='Mortalidad',
                                    names='Causa',
                                    color_discrete_sequence= px.colors.qualitative.D3,
                                    title='Distribución de Causas de Mortalidad'
                                )
                    st.plotly_chart(fig_distribucion_mortalidad, use_container_width=True)

                st.divider()

                st.subheader('Análisis de Costos')

                if df_costos_camadas.shape[0] == 0:
                    st.info('Aún no haz registrado costos asociados a tu camada', icon=':material/notifications:')

                else:
                    fig_costos = px.bar(df_costos_camadas,
                                        x= 'Tipo',
                                        y= 'Costo Total',
                                        color = 'Tipo',
                                        color_discrete_sequence= px.colors.qualitative.D3,
                                        text_auto=True,
                                        title='Costos de producción de camada')
                    
                    st.plotly_chart(fig_costos, use_container_width=True)
                    
                    fig_pie_costos = px.pie(df_costos_camadas,
                                        names= 'Tipo',
                                        values= 'Costo Total',
                                        color = 'Tipo',
                                        color_discrete_sequence= px.colors.qualitative.D3,
                                        title= 'Distribución de los costos de producción')
                    
                    st.plotly_chart(fig_pie_costos, use_container_width=True)
                
                st.divider()
                
                st.subheader('Análisis de Ventas')
                
                if df_ventas_camadas.shape[0] == 0:
                    st.info('Aún no haz registrado mortalidad o descartes en tu camada', icon=':material/notifications:')
                
                else:
                    # Se hacen gráficas de ventas
                    fig_ventas = px.bar(df_ventas_camadas,
                                        x = 'nombre',
                                        y= 'Total Ventas',
                                        color = 'nombre',
                                        color_discrete_sequence= px.colors.qualitative.D3,
                                        title= 'Ventas por presas')
                    
                    st.plotly_chart(fig_ventas, use_container_width=True)
                    
                    fig_pie_ventas = px.pie(df_ventas_camadas,
                                        names = 'nombre',
                                        values= 'Total Ventas',
                                        color = 'nombre',
                                        color_discrete_sequence= px.colors.qualitative.D3,
                                        title= 'Distribución de ventas por presas')
                    
                    st.plotly_chart(fig_pie_ventas, use_container_width=True)
                    
                    fig_ventas_dias = px.bar(df_ventas_dias_camadas,
                                            x = 'fecha',
                                            y= 'Total',
                                            color = 'fecha',
                                            color_discrete_sequence= px.colors.qualitative.D3,
                                            title= 'Ventas por dias')
                    
                    st.plotly_chart(fig_ventas_dias, use_container_width=True)
            
            analisisCamadas(camada_historial_id, df_camadas_finalizadas, df_desempeno)



######### agrega hora de faena. para arreglar la cuenta del tiempo de las históricas
# SELECT CAMADA.ID AS "camada_id",
# 	GALPON_ID,
# 	CANTIDAD,
# 	FECHA_INICIO,
# 	RAZA,
# 	PROVEEDOR,
# 	USER_ID,
# 	CAMADA_ACTIVA,
# 	GRANJA_ID,
# 	MUERTES,
# 	DESCARTES,
# 	FAENADOS,
# 	MAX(FAENA.FECHA) AS "Fecha Final",
# 	FINALIZADA
# FROM PUBLIC.CAMADA
# JOIN PUBLIC.FAENA ON FAENA.CAMADA_ID = CAMADA.ID
# WHERE CAMADA.ID = 1
# GROUP BY CAMADA.ID,
# 	GALPON_ID,
# 	CANTIDAD,
# 	FECHA_INICIO,
# 	RAZA,
# 	PROVEEDOR,
# 	USER_ID,
# 	CAMADA_ACTIVA,
# 	GRANJA_ID,
# 	MUERTES,
# 	DESCARTES,
# 	FAENADOS,
# 	FINALIZADA
 ######