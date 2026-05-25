# Importando bibliotecas

from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import folium
import streamlit as st
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Marketplace - Visão Empresa', page_icon='📈', layout='wide')

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

def pedidos_dia(df):
  cols = ['Order_Date', 'ID']
  df_aux = df.loc[ : , cols].groupby('Order_Date').count().reset_index()
  fig = px.bar(df_aux, x='Order_Date', y='ID')

  return fig


# 
def pedidos_semana(df):
  df['semana_ano'] = df['Order_Date'].dt.strftime('%U')
  cols = ['semana_ano', 'ID']
  df_aux = df.loc[ : , cols].groupby('semana_ano').count().rename(columns={'ID':'quantidade_vendas'}).reset_index()
  fig = px.line(df_aux, x='semana_ano', y='quantidade_vendas')

  return fig

# 

def pedidos_trafego(df):

  cols = ['Road_traffic_density', 'ID']
  df_aux = df.loc[ : , cols].groupby( 'Road_traffic_density' ).count().rename(columns={'ID':'quantidade_vendas'}).sort_values(by='quantidade_vendas', ascending=False).reset_index()
  df_aux['percentual'] = 100 * (df_aux['quantidade_vendas'] / df_aux['quantidade_vendas'].sum())
  fig = px.pie(df_aux, values='percentual', names='Road_traffic_density')
  
  return fig


# 

def volume_cidade_trafego(df):

  cols = ['City', 'Road_traffic_density' ,'ID']
  df_aux = df.loc[: , cols].groupby( ['City', 'Road_traffic_density'] ).count().rename(columns={'ID':'quantidade_vendas'}).sort_values(by='quantidade_vendas', ascending=False ).reset_index()
  df_aux['percentual'] = 100 * (df_aux['quantidade_vendas'] / df_aux['quantidade_vendas'].sum())
  fig = px.bar( df_aux, x='City', y='quantidade_vendas', color='Road_traffic_density', barmode='group' )

  return fig

# 

def entregador_semana(df):

  # Quantidade de pedidos por entregador por Semana

  cols = ['semana_ano', 'ID']
  df_aux1 = df.loc[ : , cols ].groupby('semana_ano').count().reset_index()

  # Quantas entregas na semana / Quantos entregadores únicos por semana

  cols2 = ['semana_ano', 'Delivery_person_ID']
  df_aux2 = df.loc[ : , cols2 ].groupby('semana_ano').nunique().reset_index()

  # Juntar as duas tabelas e fazer o gráfico

  df_aux = pd.merge(df_aux1, df_aux2, on='semana_ano', how='inner')
  df_aux['pedido_por_entregador'] = df_aux['ID'] / df_aux['Delivery_person_ID']
  fig = px.line(df_aux, x='semana_ano', y='pedido_por_entregador')

  return fig

#

def mapa_cidade_trafego(df):

  cols =[
      'City',
      'Road_traffic_density',
      'Delivery_location_longitude',
      'Delivery_location_latitude'
  ]

  cols_agrupada = ['City', 'Road_traffic_density']
  df_prin = df.loc[ : , cols].groupby( cols_agrupada ).median().reset_index()

  # desenhar mapa

  map_ = folium.Map( zoom_start= 21 )
  for i, local in df_prin.iterrows():
    folium.Marker ( [
                    local['Delivery_location_latitude'],
                    local['Delivery_location_longitude']
                    ],
                    popup=local[[ 'City', 'Road_traffic_density' ]]
                  ).add_to( map_ )
  return map_




#=========================
# Barra Lateral Streamlit
#=========================

st.header('Marketplace - Visão Empresa')


# st.dataframe(df1)
with st.sidebar:
    image = Image.open('img/curry_company.png')
    st.image(image, width=120)

    st.markdown('# Curry Company')
    st.markdown('## O Delivery mais Rápido da Cidade')
    st.markdown('''---''')

    st.markdown('## Selecione uma data limite')
    
    data_slider = st.slider( 
            'Até qual data?',
            value=datetime(2022, 4, 13),
            min_value=datetime(2022, 2, 11),
            max_value=datetime(2022, 4, 13),
            format='DD-MM-YYYY')
    st.markdown('''---''')

    trafego_opcoes = st.multiselect(
        'Escolha as condições do trânsito',
        ['Low', 'Medium', 'High', 'Jam'],
        default=['Low', 'Medium', 'High', 'Jam'])
    st.markdown('''---''')
    st.markdown('### Powered by Alifer Rabelo')

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

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container():
         # Pedido por Dia
        st.markdown('# Quantidade de Pedidos por Dia')
        fig= pedidos_dia(df)
        st.plotly_chart(fig, use_container_width=True)
   
    

    with st.container():
        col1, col2 = st.columns(2)
        # Distribuição dos pedidos por tipo de tráfego
        with col1:
            st.markdown('## Distribuição dos Pedidos por Tráfego')
            fig = pedidos_trafego(df)
            st.plotly_chart(fig, use_container_width=True)
        
        # Volume de Pedidos por Cidade e Tráfego

        with col2:
            st.markdown('## Volume de Pedidos por Cidade e Tráfego')
            fig = volume_cidade_trafego(df)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        # Quantidade de Pedidos por Semana
        fig = pedidos_semana(df)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        # Quantidade de pedidos por entregador por Semana
        fig = entregador_semana(df)
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    with st.container():
        st.markdown('# Mapa do País')
        mapa = mapa_cidade_trafego(df)
        folium_static(mapa, width=1024, height=600)