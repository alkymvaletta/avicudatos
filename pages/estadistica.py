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

df = pd.DataFrame(resultados, columns=columnas)


st.write('Vigila el desempeño de tus aves de acuerdo a los datos de referencia suministrados por cada una de las razas')

# Creamos 3 columnas para establecer filtros

col1, col2, col3 = st.columns(3)

## Creamos filtro para seleccionar rango de días
with col1:
    dias = st.slider('Cuantos días deseas visualizar',
                value=42,
                min_value=df['edad_en_dias'].min(), 
                max_value=df['edad_en_dias'].max())

## Creamos filtro para seleccionar Raza
with col2:
    raza = st.selectbox('Seleccione las raza', df['Raza'].unique())

## Creamos filtro para seleccionar Sexo
with col3:
    sexo = st.selectbox('Seleccione el sexo', df['sexo'].unique())

# Se crea df de acuerdo a los filtros seleccionados
df_filtrado = df[
            ((df['edad_en_dias']).isin(range(0, dias + 1))) &
            (df['Raza'] == raza) &
            (df['sexo'] == sexo)
            ]

# Graficamos el consumo de alimentos acumulado
st.subheader('Consumo de alimento acumulado')
st.line_chart(df_filtrado, 
              x= 'edad_en_dias', 
              y='consumo_alimentos_acumulado', 
              x_label='Dias', 
              y_label='Consumo alimento acumulado [g]')

# Graficamos el peso
st.subheader('Ganancia de peso acumulada')
st.line_chart(df_filtrado, 
              x= 'edad_en_dias', 
              y='peso',
              x_label='Dias',
              y_label='Peso [g]')


if st.checkbox('Visualizar datos'):
    st.write(df_filtrado)