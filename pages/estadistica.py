import streamlit as st
import utilidades as util
import pandas as pd
import plotly.express as px
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

@st.cache_data
def datos_desempeno():
    # Conectamos con la database
    conn, c  = util.conectarDB()
    # Extraemos los datos de DB con base al query
    c.execute('''SELECT EDAD_EN_DIAS,
                    PESO,
                    consumo_alimentos_acumulado,
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
        
        if st.checkbox('Comparar camada'):
            comparar_camada = st.selectbox('Seleccione la camada a comparar', options=['Camada1', 'Camada2'])
        
        # Se crea df de acuerdo a los filtros seleccionados
        df_filtrado = df_desempeno[
                    ((df_desempeno['Edad en días']).isin(range(0, dias + 1))) &
                    (df_desempeno['Raza'] == raza) &
                    (df_desempeno['sexo'] == sexo)
                    ]

        # Graficamos el consumo de alimentos acumulado
        with st.container(border=True):
            graph1, graph2 = st.columns(2)
            with graph1:
                st.write('**Consumo de alimento acumulado**')
                st.line_chart(df_filtrado,
                            color=(1,204,17),
                            x= 'Edad en días', 
                            y='Consumo alimento acumulado', 
                            x_label='Dias', 
                            y_label='Consumo alimento acumulado [g]')

        # Graficamos el peso
            with graph2:
                st.write('**Ganancia de peso acumulada**')
                st.line_chart(df_filtrado,
                            color=(246,64,19), 
                            x= 'Edad en días', 
                            y='Peso',
                            x_label='Dias',
                            y_label='Peso [g]')

        if st.checkbox('Tabla datos de referencia'):
            st.dataframe(df_filtrado, hide_index=True, use_container_width=True)

# Análisis de las camadas
with st.container(border=True):
    if st.toggle('Análisis de tus camadas'):
        # Selecciona la camada que se va a analisar
        
        df_camadas = util.consultarCamadas(user_id)
        df_camadas_merged = pd.merge(df_camadas, df_galpones, how='left', left_on='galpon_id', right_on='galpon_id')
        df_camadas_merged = df_camadas_merged.rename(columns={'cantidad':'Ingresados', 'fecha_inicio':'Fecha ingreso', 'fecha_estimada_sacrificio':'Sacrificio estimado', 'muertes':'Muertes', 'descartes':'Descartes', 'faenados':'Sacrificados'})
        df_camadas_merged['Fecha ingreso'] = pd.to_datetime(df_camadas_merged['Fecha ingreso']).dt.date
        df_camadas_merged['Dias'] = (datetime.now().date() - df_camadas_merged['Fecha ingreso']).apply(lambda x: x.days)
        df_camadas_merged['Disponibles'] =df_camadas_merged['Ingresados'] - df_camadas_merged['Muertes'] - df_camadas_merged['Descartes'] - df_camadas_merged['Sacrificados']
        df_camadas_merged['galponEingreso'] = df_camadas_merged['Galpón'].map(str) + ' ingresado ' + df_camadas_merged['Fecha ingreso'].map(str)
        
        camada_evualuar = st.selectbox('Selecciona la camada', options=df_camadas_merged['galponEingreso'])
        camada_evualuar_id = int(df_camadas_merged['id'][df_camadas_merged['galponEingreso'] == camada_evualuar])
        # Se establecen columnas para las métricas.
        st.divider()
        
        st.subheader('Análisis zootécnicos')
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
                
                st.metric('Conv. Alimenticia - CA', CA, '-1.2 %')
        
        # Eficiencia Alimenticia - EA = Peso Prom / Conversión Alimenticia 
        with metr3:
            if (CA == None) or (df_promedio_pesos.shape[0] == 0) :
                st.metric('Ef. Alimenticia - EA', 'NaN')
                EA = None
            else:
                EA = round(peso_promedio / CA, 4)
                st.metric('Ef. Alimenticia - EA', EA, '4.2 %')
        
        # Indice de Productividad - IP = Eficiencia Alimenticia / Conversión Alimenticia
        with metr4:
            if (CA == None) or (EA == None):
                st.metric('Indice Productividad - IP', 'NaN')
            else:
                IP = round(EA / CA, 4)
                st.metric('Indice Productividad - IP', IP, '09 %')
        st.divider()
        
        st.subheader('Análisis económico')
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
            #valor_venta= 7234650
            df_valor_venta = util.cosnultaQuery(f'''
                                            SELECT SUM(PRECIO_TOTAL) AS TOTAL
                                            FROM PUBLIC.VENTAS
                                            WHERE CAMADA_ID = {camada_evualuar_id}
                                            ''')
            if df_valor_venta.values[0] == None:
                st.metric('Total ventas',value= 0)
                valor_venta = 0
            else:
                valor_venta = int(df_valor_venta.values[0])
                st.metric('Total ventas',value= f'${format(round(valor_venta/1000000, 3) , ",")} M')
        
        #Utilidades
        with metr7:
            st.metric('Utilidad total', value= f'${format(round((valor_venta-costo_total)/1000000, 3), ",")} M')
        
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
        
        @st.cache_data()
        def buscarMortalidad_descarte():
            df_mortalidad = util.cosnultaQuery(f'''
                                                SELECT CAMADA_ID,
                                                    FECHA,
                                                    CANTIDAD AS "Mortalidad",
                                                    CAUSAS_MORTALIDAD.CAUSA_POSIBLE as "Causa"
                                                FROM PUBLIC.MORTALIDAD
                                                JOIN PUBLIC.CAUSAS_MORTALIDAD ON CAUSAS_MORTALIDAD.ID = MORTALIDAD.CAUSA_POSIBLE_ID
                                                WHERE CAMADA_ID = {camada_evualuar_id}
                                                ''')
            df_descarte = util.cosnultaQuery(f'''
                                            SELECT CAMADA_ID,
                                                RAZON,
                                                FECHA,
                                                CANTIDAD AS "Descarte"
                                            FROM PUBLIC.DESCARTE
                                            WHERE CAMADA_ID = {camada_evualuar_id}
                                            ''')
            
            # Hacemos grafico de barras por las causas de muerte
            df_descarte_ = df_descarte[['fecha', 'Descarte']]
            df_mortalidad_ = df_mortalidad[['fecha', 'Mortalidad']]
            df_mortalidad_descarte = pd.concat([df_mortalidad_, df_descarte_])
            return df_mortalidad, df_descarte, df_mortalidad_descarte
        
        df_mortalidad, df_descarte, df_mortalidad_descarte = buscarMortalidad_descarte()
        
        # Se aplica mensaje en caso de que no se haya presentado mortalidad o descarte
        if (df_mortalidad.shape[0] == 0 ) and (df_descarte.shape[0] == 0):
            st.info('Aún no haz registrado mortalidad o descartes en tu camada')
        
        else:
            df_mortalidad_agg = df_mortalidad.groupby('Causa')['Mortalidad'].sum().reset_index().sort_values(by='Mortalidad', ascending=False)
            
            fig_mortalidad_descarte = px.scatter(df_mortalidad_descarte, 
                                                x = 'fecha', 
                                                y=['Mortalidad', 'Descarte'],
                                                )
            
            st.plotly_chart(fig_mortalidad_descarte, use_container_width=True)
            
            #st.scatter_chart(df_mortalidad_descarte, x = 'fecha', y=['Mortalidad', 'Descarte'], x_label='Fecha', y_label='Cantidad', color=["#FF0000", "#0000FF"])
            
            #Se hace la gráfica
            fig = px.bar(df_mortalidad_agg,
                            x='Causa',
                            y='Mortalidad',
                            color = 'Causa',
                            text_auto=True, #Muestra el valor de la columna
                            color_discrete_sequence= px.colors.qualitative.D3,
                            title='Causas de Mortalidad'
                        )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Se hace Análisis de los Costos
        st.subheader('Análisis de Costos')
        
        @st.cache_data()
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
                                text_auto=True)
            
            st.plotly_chart(fig_costos, use_container_width=True)
        
# Histórico de las camadas
with st.container(border=True):
    if st.toggle('Histórico de tus camadas'):
        st.write('Ver el histórico de las camadas')