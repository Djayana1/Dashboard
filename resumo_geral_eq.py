import streamlit as st
import pandas as pd
import altair as alt

def mostrar_pagina_resumo():
    # Leitura da planilha
    df = pd.read_csv(r"E:\Area de Trabalho\Dashboard\Resumo.csv", sep=';')
    df.columns = df.columns.str.strip()

    # Conversão de colunas numéricas
    colunas_numericas = [
        'Escopo 1', 'Escopo 2 - Baseada na localização', 'Escopo 2 - Baseada na escolha de compra', 'Escopo 3',
        'EQ Escopo 1', 'EQ Escopo 2 - Baseada na localização', 'EQ Escopo 2 - Baseada na escolha de compra', 'EQ Escopo 3'
    ]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", ".").str.replace(" ", "").str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'ANO' in df.columns:
        df['ANO'] = pd.to_numeric(df['ANO'], errors='coerce').astype('Int64')

    # Sidebar com filtros
    with st.sidebar:
        st.title("Filtros")

        anos = sorted(df['ANO'].dropna().unique(), reverse=True)
        ano_selecionado = st.selectbox("Selecione o Ano:", anos)
        df = df[df['ANO'] == ano_selecionado]

        relatorios = sorted(df['Relatório'].dropna().unique())
        relatorio_selecionado = st.selectbox("Tipo de Relatório:", relatorios)
        df = df[df['Relatório'] == relatorio_selecionado]

        nomes = sorted(df['NOME'].dropna().unique())
        nome_selecionado = st.selectbox("Organização:", nomes)
        df = df[df['NOME'] == nome_selecionado]

        indicadores_disponiveis = [
            'EQ Escopo 1',
            'EQ Escopo 2 - Baseada na localização',
            'EQ Escopo 2 - Baseada na escolha de compra',
            'EQ Escopo 3'
        ]
        indicador_selecionado = st.selectbox("Indicador EQ para o gráfico:", indicadores_disponiveis)

    # Tabela de indicadores EQ
    colunas_eq = ['GEE'] + indicadores_disponiveis
    df_eq = df[[col for col in colunas_eq if col in df.columns]].copy()
    st.subheader("Emissões de GEE (Indicadores EQ)")
    st.dataframe(df_eq, use_container_width=True)

    # Tabela de escopos diretos
    colunas_escopos = [
        'GEE', 'Escopo 1', 'Escopo 2 - Baseada na localização', 'Escopo 2 - Baseada na escolha de compra', 'Escopo 3'
    ]
    df_escopos = df[[col for col in colunas_escopos if col in df.columns]].copy()
    st.subheader("Emissões de GEE (Escopos Diretos)")
    st.dataframe(df_escopos, use_container_width=True)

    # Gráfico de barras com rótulos
    ordem_gee = ['CO2', 'CH4', 'N2O', 'HFC', 'PFC', 'SF6', 'NF3']
    if 'GEE' in df.columns and indicador_selecionado in df.columns:
        df_plot = df[['GEE', indicador_selecionado]].copy()
        df_plot = df_plot[df_plot['GEE'].isin(ordem_gee)]
        df_plot[indicador_selecionado] = pd.to_numeric(df_plot[indicador_selecionado], errors='coerce')
        df_plot = df_plot.dropna()

        barras = alt.Chart(df_plot).mark_bar().encode(
            y=alt.Y('GEE:N', title='Tipo de GEE', sort=ordem_gee),
            x=alt.X(f'{indicador_selecionado}:Q', title=f'{indicador_selecionado} (toneladas CO2e)'),
            color=alt.value('#1f77b4'),
            tooltip=['GEE', indicador_selecionado]
        )

        rotulos = alt.Chart(df_plot).mark_text(
            align='left',
            baseline='middle',
            dx=3
        ).encode(
            y=alt.Y('GEE:N', sort=ordem_gee),
            x=alt.X(f'{indicador_selecionado}:Q'),
            text=alt.Text(f'{indicador_selecionado}:Q', format=',.0f')
        )

        chart = (barras + rotulos).properties(
            width=700,
            height=400,
            title=f"Emissões por GEE - {indicador_selecionado}"
        )

        st.subheader("Gráfico de Emissão por Indicador EQ")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Coluna 'GEE' ou indicador selecionado não encontrado.")
