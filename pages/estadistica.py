import streamlit as st
import psycopg2
import utilidades as util
import pandas as pd

# Se agrega logo
HORIZONTAL = 'src\images\horizontal_logo.png'

st.set_page_config(page_title='Avicudatos - Estadisticas de desempeño',page_icon='🐔')

st.logo(HORIZONTAL)

st.header('Avicudatos 🐔', divider='rainbow')

#Si no hay usuario registrado se va a Home
if 'usuario' not in st.session_state:
    st.switch_page('Home.py')

util.generarMenu(st.session_state['usuario'])


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

    if st.toggle('Ver datos de referencia por razas'):
    
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

with st.container(border=True):
    if st.toggle('Análisis de tus camadas'):
        # Selecciona la camada que se va a analisar
        camada_evualuar = st.selectbox('Selecciona la camada', options=['cam1', 'cam2', 'cam3'])
        # Se establecen columnas para las métricas.
        st.divider()
        st.subheader('Análisis zootécnicos')
        metr1, metr2, metr3, metr4 = st.columns(4)
        with metr1:
            st.metric('Mortalidad', '3 %', '0.3 %')
        with metr2:
            st.metric('Conv. Alimenticia - CA', '67 %', '-1.2 %')
        with metr3:
            st.metric('Ef. Alimenticia - EA', '45 %', '4.2 %')
        with metr4:
            st.metric('Indice Productividad - IP', '38 %', '09 %')
        st.divider()
        st.subheader('Análisis económico')
        metr5, metr6, metr7, metr8 = st.columns(4)
        with metr5:
            valor = 4237876
            st.metric('Total costos', format(valor, ","))
        with metr6:
            valor_venta= 7234650
            st.metric('Total ventas', format(valor_venta, ","))
        with metr7:
            st.metric('Utilidad total', value= f'${format(valor_venta-valor, ",")}')
        with metr8:
            utilidad = round((valor_venta-valor)/valor_venta, 2)
            st.metric('Porcentaje Utilidad', value= f'{utilidad} %')