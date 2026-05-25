# Importando bibliotecas


import pandas as pd
import streamlit as st
import plotly.express as px
import folium
import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

# Setando página

st.set_page_config(page_title='Marketplace - Visão Entregadores', page_icon='🚚', layout='wide')

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

        Input: Dataframe
        Output: Dataframe 

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
# Barra Lateral Streamlit
#=========================

st.header('Marketplace - Visão Entregadores')

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
    st.markdown(''' --- ''')

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

linhas_selecionadas = df['Order_Date'] <= data_slider
df = df.loc[ linhas_selecionadas , : ]

# Filtro de trafego

linhas_selecionadas = df['Road_traffic_density'].isin( trafego_opcoes )
df = df.loc[ linhas_selecionadas , : ]

# Filtro de condicoes climáticas

linhas_selecionadas = df['Weatherconditions'].isin(condicoes_opcoes)
df = df.loc[ linhas_selecionadas , : ]

#=========================
# Layout Streamlit
#=========================

tab1, = st.tabs(['Visão Gerencial'])

with tab1:
    with st.container():
        st.title('Métricas Gerais')

        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # A maior idade dos entregadores
            maior_idade = df['Delivery_person_Age'].max()
            col1.metric('Maior Idade', maior_idade)

        with col2:
            # A menor idade dos entregadores
            menor_idade = df['Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)

        with col3:
            # A melhor condição dos veículos
            melhor_condicao = df['Vehicle_condition'].max()
            col3.metric('Melhor Condição', melhor_condicao)

        with col4:
            # Pior condição dos veículos
            pior_condicao = df['Vehicle_condition'].min()
            col4.metric('Pior Condição', pior_condicao)

    with st.container():
        st.markdown('''---''')
        st.title('Avaliações')

        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.markdown('## Avaliação Média por Clima')
            df_aval_condicoes = (df.groupby('Weatherconditions', as_index=False)
                    .agg(
                        avaliacao_media=('Delivery_person_Ratings', 'mean'),
                        avaliacao_desvio_padrao=('Delivery_person_Ratings', 'std') ) )
            st.dataframe(df_aval_condicoes, use_container_width=True)

            st.markdown('## Avaliação Média por Trânsito')
            cols = [ 'Road_traffic_density', 'Delivery_person_Ratings' ]

            df_std_trafego = (df.loc[ : , cols].groupby('Road_traffic_density', as_index=False)
                  .agg(
                      avaliacao_media=('Delivery_person_Ratings','mean'),
                      avaliacao_desvio_padrao=('Delivery_person_Ratings', 'std')))
            st.dataframe(df_std_trafego, use_container_width=True)

            

        with col2:
            st.markdown('## Avaliação Média por Entregador')
            cols = [ 'Delivery_person_Ratings', 'Delivery_person_ID' ]
            df_aval_entregador = df.loc[ : , cols ].groupby( 'Delivery_person_ID' ).mean().reset_index()
            st.dataframe(df_aval_entregador, use_container_width=True)

    with st.container():
        st.markdown('''---''')
        st.markdown('# Velocidade de Entrega')

        col1, col2 = st.columns(2, gap='large')

        with col1:
            st.markdown('## Entregadores mais Rápidos')
            cols = [ 'City', 'Delivery_person_ID', 'Time_taken(min)' ]
            df_mais_rapido = df.loc[ : , cols]
            df_mais_rapido = df_mais_rapido.sort_values(['City','Time_taken(min)'], ascending=True).groupby('City' ).head(10)
            st.dataframe(df_mais_rapido)

        with col2:
            st.markdown('## Entregadores mais Lentos')
            cols = [ 'City', 'Delivery_person_ID', 'Time_taken(min)' ]
            df_mais_lento = df.loc[ : , cols]
            df_mais_lento = df_mais_lento.sort_values(['City', 'Time_taken(min)'], ascending=False).groupby('City').head(10)
            st.dataframe(df_mais_lento)


