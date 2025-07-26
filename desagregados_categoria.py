import streamlit as st
import pandas as pd
import altair as alt
from Mapa import mostrar_pagina_mapa


def mostrar_pagina_categoria():
    mostrar_pagina_mapa(mostrar_legenda=False) 

    # Leitura dos dados
    df_cat = pd.read_csv(r"E:\Area de Trabalho\Dashboard\Desagregados por categoria.csv", sep=';')
    df_cat.columns = df_cat.columns.str.strip()

    # Conversão de colunas numéricas
    colunas_numericas = ['Emissões (tCO2e)']
    for col in colunas_numericas:
        df_cat[col] = df_cat[col].astype(str).str.replace(",", ".").str.replace(" ", "").str.strip()
        df_cat[col] = pd.to_numeric(df_cat[col], errors='coerce')

    # Filtros na sidebar
    with st.sidebar:
        st.title("Filtros - Desagregados")

        anos = sorted(df_cat['ANO'].dropna().unique(), reverse=True)
        ano_cat = st.selectbox("Ano:", anos)

        nomes_cat = sorted(df_cat['NOME'].dropna().unique())
        nome_cat = st.selectbox("Organização:", nomes_cat)

        escopos = sorted(df_cat['ESCOPO'].dropna().unique())
        escopo_cat = st.selectbox("Escopo:", escopos)

        relatorios = sorted(df_cat['Relatório'].dropna().unique())
        relatorio_cat = st.selectbox("Relatório:", relatorios)

    # Aplicar filtros
    filtro_cat = (
        (df_cat['ANO'] == ano_cat) &
        (df_cat['NOME'] == nome_cat) &
        (df_cat['ESCOPO'] == escopo_cat) &
        (df_cat['Relatório'] == relatorio_cat)
    )

    df_cat_filtrado = df_cat[filtro_cat].copy()

    # Tabela agregada por NOME, ANO, Relatório, ESCOPO
    st.subheader("Emissões por Categoria - Tabela Agregada")
    tabela_agregada = df_cat_filtrado.groupby(
        ['NOME', 'ANO', 'Relatório', 'ESCOPO'], as_index=False
    )[colunas_numericas].sum()

    st.dataframe(tabela_agregada, use_container_width=True)

    # Gráfico 1: Emissões por Categoria
    st.subheader("Gráfico 1: Emissões por Categoria")
    graf1 = df_cat_filtrado.groupby('Categoria', as_index=False)['Emissões (tCO2e)'].sum()

    barras1 = alt.Chart(graf1).mark_bar().encode(
        x=alt.X('Categoria:N', sort='-y'),
        y=alt.Y('Emissões (tCO2e):Q'),
        tooltip=['Categoria', 'Emissões (tCO2e)']
    )

    rotulos1 = alt.Chart(graf1).mark_text(
        align='center',
        baseline='bottom',
        dy=-5
    ).encode(
        x='Categoria:N',
        y='Emissões (tCO2e):Q',
        text=alt.Text('Emissões (tCO2e):Q', format=',.0f')
    )

    st.altair_chart((barras1 + rotulos1).properties(width=800, height=400), use_container_width=True)

 
