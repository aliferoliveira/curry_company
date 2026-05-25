import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎲',
    layout='centered'
)

with st.sidebar:
    image = Image.open('img/curry_company.png')
    st.image(image, width=120)
    st.markdown('# Curry Company')
    st.markdown('## O Delivery mais Rápido da Cidade')
    st.markdown(''' --- ''')
    st.markdown('### Powered by Alifer Rabelo')


st.markdown("""
# 📊 Growth Dashboard

Este dashboard foi construído para acompanhar as principais métricas de crescimento de entregadores e restaurantes.

## Como utilizar o Growth Dashboard?

### 🏢 Visão Empresa
- **Visão Gerencial:** métricas gerais de comportamento do negócio.
- **Visão Tática:** indicadores semanais de crescimento.
- **Visão Geográfica:** insights de geolocalização.

### 🛵 Visão Entregador
- Acompanhamento dos indicadores semanais de crescimento dos entregadores.

### 🍽️ Visão Restaurante
- Indicadores semanais de crescimento dos restaurantes.

💡 Selecione uma visão no menu ao lado para começar.
""")