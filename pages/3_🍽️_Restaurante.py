# Importando bibliotecas


import pandas as pd
import streamlit as st
import plotly.express as px
import folium
import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static
from haversine import haversine

# Setando página

st.set_page_config(page_title='Marketplace - Visão Restaurante', page_icon='🍽️', layout='wide')

# Lendo o dataset

df_raw = pd.read_csv('dataset/train.csv')
df = df_raw.copy()

# Limpeza dos dados



def limpeza_codigo(df1):
    '''''
        Essa função tem como objetivo limpar o código, sendo dividido em três partes:

        1. Remoção dos espaços;
        2. Remoção dos NaN
        3. Conversão dos tipos

    '''''
    colunas_texto = [
        'Delivery_person_Age',
        'multiple_deliveries',
        'Festival',
        'Road_traffic_density',
        'City',
        'ID',
        'Delivery_person_ID',
        'Type_of_vehicle',
        'Type_of_order'
    ]

    # 1. Remoção dos espaços;

    for col in colunas_texto:
        df1[col] = df1[col].astype(str).str.strip()

    # 2. Remoção dos NaN


    df1 = df1[df1['Delivery_person_Age'] != 'NaN']
    df1 = df1[df1['multiple_deliveries'] != 'NaN']
    df1 = df1[df1['Festival'] != 'NaN']
    df1 = df1[df1['Road_traffic_density'] != 'NaN']
    df1 = df1[df1['City'] != 'NaN']


    # 3. Conversão dos tipos


    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.replace('(min) ', '', regex=False).astype( int )

    return df1

df = limpeza_codigo(df)

#=========================
# Funções
#=========================


# 

def distancia_media(df):
    cols = ['Restaurant_latitude',
            'Restaurant_longitude',
            'Delivery_location_latitude',
            'Delivery_location_longitude']

    df_aux = df.loc[:, cols].copy()

    df_aux['distancia'] = df_aux.apply(
        lambda x: haversine(
            (x['Restaurant_latitude'], x['Restaurant_longitude']),
            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
        ),
        axis=1
    )

    return df_aux['distancia'].mean().round(2)

#

def boxplot_tempo_por_cidade(df):
    fig = px.box(df, x='City', y='Time_taken(min)', title='Distribuição do Tempo de Entrega por Cidade')
    return fig

#=========================
# Barra Lateral Streamlit
#=========================

st.header('Marketplace - Visão Restaurante')

with st.sidebar:
    image = Image.open('img/curry_company.png')
    st.image(image, width=120)
    st.markdown('# Curry Company')
    st.markdown('## O Delivery mais Rápido da Cidade')
    st.markdown(''' --- ''')

    st.markdown('## Selecione uma data limite ')
    data_slider = st.slider(
        'Até qual data?',
        value=datetime(2022, 4, 13),
        min_value=datetime(2022, 2, 11),
        max_value=datetime(2022, 4, 13),
        format='DD-MM-YYYY')
    st.markdown('''---''')

    trafego_opcoes = st.multiselect(
        'Escolha as condições de trânsito',
        ['Low', 'Medium', 'High', 'Jam'],
        default=['Low', 'Medium', 'High', 'Jam'])
    
    condicoes_opcoes = st.multiselect(
        'Escolha as condições climáticas',
        ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
        default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'])
    st.markdown(''' --- ''')
    st.markdown('### Powered by Alifer Rabelo')


# Filtro de data

linhas_selecionadas = df['Order_Date'] < data_slider
df = df.loc[linhas_selecionadas , :]

# Filtro de trafego

linhas_selecionadas = df['Road_traffic_density'].isin(trafego_opcoes)
df = df.loc[linhas_selecionadas , :]

# Filtro de condições climáticas

linhas_selecionadas = df['Weatherconditions'].isin(condicoes_opcoes)
df = df.loc[linhas_selecionadas , :]

#=========================
# Layout Streamlit
#=========================

tab1, = st.tabs(['Visão Gerencial'])

with tab1:
    with st.container():
        st.markdown('# Métricas Gerais')
        col1, col2, col3, col4, col5, col6 = st.columns(6, gap='large')

        with col1:
            quantidade_entregadores = df['Delivery_person_ID'].nunique()
            st.metric('Quantidade de Entregadores',quantidade_entregadores)
        with col2:
            st.metric('Distância Média', distancia_media(df))
        with col3:
            tempo_medio_festival = df.loc[df['Festival'] == 'Yes','Time_taken(min)'].mean().round(2)
            st.metric('Tempo Médio Festival', tempo_medio_festival)
        with col4:
            std_medio_festival = round(df.loc[df['Festival'] == 'Yes','Time_taken(min)'].std(), 2)
            st.metric('STD Médio Festival', std_medio_festival)
        with col5:
            tempo_medio_sfestival = df.loc[df['Festival'] == 'No','Time_taken(min)'].mean().round(2)
            st.metric('Tempo Médio S/ Festival', tempo_medio_sfestival)
        with col6:
            std_medio_sfestival = round(df.loc[df['Festival'] == 'No','Time_taken(min)'].std(), 2)
            st.metric('STD Médio S/ Festival', std_medio_sfestival)

    with st.container():
        st.markdown('''---''')
        st.plotly_chart(boxplot_tempo_por_cidade(df))

