import streamlit as st
import utilidades as util
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def analisisCamadas(camada_id, finalizada):
    
    #df_costos_camadas, df_ventas_camadas, df_ventas_dias_camadas = util.costos_ventas_Camadas(camada_id)

    st.divider()
    
    st.subheader('Análisis Zootécnicos')

    df_datosCamada = util.datosCamada(camada_id, finalizada)
    camada_ingreso = df_datosCamada['Fecha ingreso'].iloc[0]
    camada_granja = df_datosCamada['Granja'].iloc[0]
    camada_galpon = df_datosCamada['Galpón'].iloc[0]
    camada_capacidad = df_datosCamada['capacidad'].iloc[0]
    camada_ingresados = df_datosCamada['Ingresados'].iloc[0]
    camada_dias = df_datosCamada['Dias'].iloc[0]
    camada_muerte = df_datosCamada['Muertes'].iloc[0]
    camada_descarte = df_datosCamada['Descartes'].iloc[0]
    camada_sacrificio = df_datosCamada['Sacrificados'].iloc[0]
    camada_raza = df_datosCamada['Raza'].iloc[0]
    camada_razaid = df_datosCamada['raza_id'].iloc[0]
    camada_dias_final = df_datosCamada['Dias_Faena'].iloc[0]

    if finalizada == True:
        st.write(f'''La camada se ingresó el **{camada_ingreso}** encuentra en la granja **{camada_granja}** en el galpón **{camada_galpon}** 
            que tiene una capacidad de **{camada_capacidad}** aves. Se ingresaron un total de **{camada_ingresados}**  de raza **{camada_raza}** y llevan 
            **{camada_dias_final} dias**, en los cuales han muerto **{camada_muerte}** y se han descartado **{camada_descarte}** aves. 
            Hasta la fecha se han sacrificado **{camada_sacrificio}**''')
        camada_dias = camada_dias_final
    
    else:
        st.write(f'''La camada se ingresó el **{camada_ingreso}** encuentra en la granja **{camada_granja}** en el galpón **{camada_galpon}** 
            que tiene una capacidad de **{camada_capacidad}** aves. Se ingresaron un total de **{camada_ingresados}**  de raza **{camada_raza}** y llevan 
            **{camada_dias} dias**, en los cuales han muerto **{camada_muerte}** y se han descartado **{camada_descarte}** aves. 
            Hasta la fecha se han sacrificado **{camada_sacrificio}**''')

    df_desempeno = util.datos_desempeno()
    
    metr1, metr2, metr3, metr4 = st.columns(4)

    # Mortalidad
    with metr1:
        mortalidad = round(camada_muerte / camada_ingresados,4)*100
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
        
        df_desempeno = util.datos_desempeno()
        # st.write(df_desempeno)
        #Traemos la referencia de CA de acuerdo a los días transcurridos
        CA_referencia = df_desempeno['CA'][(df_desempeno['Edad en días'] == camada_dias) & 
                                            (df_desempeno['raza_id'] == camada_razaid) &
                                            (df_desempeno['sexo'] == 'mixto')].values[0]
        
        #st.dataframe(CA_referencia)
        
        if (df_consumo_alimento.shape[0] == 0) or (df_promedio_pesos.shape[0] == 0):
            st.metric('Conv. Alimenticia - CA', 'NaN')
            CA = None
        else:
            #Peso promedio de las aves
            peso_promedio = float(df_promedio_pesos.values[0])/1000
            # Consumo promedio de aves ingresadas
            consumo_promedio = float(round(df_consumo_alimento['total_alimento'].values[0]/camada_ingresados, 4))
            
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
    
    df_costos_camadas, df_ventas_camadas, df_ventas_dias_camadas, df_ventas_diasWeek_camadas = util.costos_ventas_Camadas(camada_id)
    
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
        
        # Grafico Pie de distribución de gráfico por presas
        fig_pie_ventas = px.pie(df_ventas_camadas,
                            names = 'nombre',
                            values= 'Total Ventas',
                            color = 'nombre',
                            color_discrete_sequence= px.colors.qualitative.D3,
                            title= 'Distribución de ventas por presas')
        
        st.plotly_chart(fig_pie_ventas, use_container_width=True)
        
        #Grafico de barra de venta por días
        fig_ventas_dias = px.bar(df_ventas_dias_camadas,
                                x = 'fecha',
                                y= 'Total',
                                color = 'fecha',
                                color_discrete_sequence= px.colors.qualitative.D3,
                                title= 'Ventas por dias')
        
        st.plotly_chart(fig_ventas_dias, use_container_width=True)
        
        
        #Gráfico de barras de ventas por día de la semana.
        fig_ventas_diasWeek = px.bar(df_ventas_diasWeek_camadas,
                                x = 'Día',
                                y= 'Venta',
                                color = 'Día',
                                color_discrete_sequence= px.colors.qualitative.D3,
                                title= 'Ventas por dia de la semana')
        
        st.plotly_chart(fig_ventas_diasWeek, use_container_width=True)
    