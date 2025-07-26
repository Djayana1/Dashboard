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

        anos = sorted(df_cat['ANO'].dropna().unique())
        ano_cat = st.multiselect("Ano(s):", options=["Todos"] + list(anos), default=["Todos"])

        nomes_cat = sorted(df_cat['NOME'].dropna().unique())
        nome_cat = st.multiselect("Organização:", options=["Todas"] + nomes_cat, default=["Todas"])

        escopos = sorted(df_cat['ESCOPO'].dropna().unique())
        escopo_cat = st.selectbox("Escopo:", escopos)

        relatorios = sorted(df_cat['Relatório'].dropna().unique())
        relatorio_cat = st.selectbox("Relatório:", relatorios)

    # Aplicar filtros
    filtro_cat = (df_cat["Relatório"] == relatorio_cat)

    if "Todos" not in ano_cat:
        filtro_cat &= df_cat["ANO"].isin(ano_cat)

    if "Todas" not in nome_cat:
        filtro_cat &= df_cat["NOME"].isin(nome_cat)


    df_cat_filtrado = df_cat[filtro_cat].copy()

    # CSS para aumentar fonte das tabelas
    st.markdown("""
        <style>
        .dataframe tbody td, .dataframe thead th {
            font-size: 18px !important;
            color: black !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # -------------------------------
        # [Tabela] Emissões por categoria e escopo
    # -------------------------------
    st.subheader("Tabela – Emissões por Categoria e Escopo (Ano Selecionado)")
    tabela_escopo_categoria = df_cat_filtrado.groupby(
        ['Categoria', 'ESCOPO'], as_index=False
    )['Emissões (tCO2e)'].sum()

    with st.expander("Ver Tabela – Emissões por Categoria e Escopo (expandir)"):
        st.dataframe(tabela_escopo_categoria, use_container_width=True)


    # Formatar os valores de emissões com separador de milhar e sem casas decimais
    tabela_escopo_categoria['Emissões (tCO2e)'] = tabela_escopo_categoria['Emissões (tCO2e)'].apply(lambda x: f"{x:,.0f}")

    st.dataframe(tabela_escopo_categoria, use_container_width=True)

    # -------------------------------
    # [Tabela] Emissões por NOME, ANO, Relatório, ESCOPO
    # -------------------------------
    st.subheader("Emissões por Categoria - Tabela Agregada")
    tabela_agregada = df_cat_filtrado.groupby(
        ['NOME', 'ANO', 'Relatório', 'ESCOPO'], as_index=False
    )['Emissões (tCO2e)'].sum()

    # Aplicar a mesma formatação
    tabela_agregada['Emissões (tCO2e)'] = tabela_agregada['Emissões (tCO2e)'].apply(lambda x: f"{x:,.0f}")

    st.dataframe(tabela_agregada, use_container_width=True)
    # -------------------------------
    # [Gráfico 1] Emissões totais por categoria (barra simples)
    # -------------------------------
    st.subheader("Gráfico 1 – Emissões por Categoria (Total)")

    graf1 = df_cat_filtrado.groupby('Categoria', as_index=False)['Emissões (tCO2e)'].sum()

    barras1 = alt.Chart(graf1).mark_bar().encode(
        x=alt.X('Categoria:N', sort='-y', title="Categoria"),
        y=alt.Y('Emissões (tCO2e):Q', title="Emissões (tCO2e)"),
        tooltip=['Categoria', 'Emissões (tCO2e)'],
        color=alt.value('#1f77b4')
    )

    rotulos1 = alt.Chart(graf1).mark_text(
        align='center',
        baseline='bottom',
        dy=-5,
        fontSize=12
    ).encode(
        x='Categoria:N',
        y='Emissões (tCO2e):Q',
        text=alt.Text('Emissões (tCO2e):Q', format=',.0f')
    )

    st.altair_chart((barras1 + rotulos1).properties(width=700, height=400), use_container_width=True)

    # -------------------------------
    