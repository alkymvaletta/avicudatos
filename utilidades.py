import streamlit as st

def generarMenu(usuario = 'Alkin'):
    with st.sidebar:
        st.write(f'Bienvenido, **{usuario}**')
        st.page_link('Home.py', label= 'Inicio', icon= ':material/home:')
        st.subheader('Gestiona tu granja')
        st.page_link('pages/granja.py', label='Tu granja', icon=':material/agriculture:')
        st.page_link('pages/camada.py', label='Tus camadas', icon=':material/gite:')
        st.page_link('pages/faenas.py', label='Faenas', icon=':material/food_bank:')
        st.subheader('Vende tu producto')
        st.page_link('pages/ventas.py', label='Ventas', icon=':material/payments:')
        st.subheader('Evalúa tu desempeño')
        st.page_link('pages/estadistica.py', label='Analíticas', icon=':material/analytics:')
        
        