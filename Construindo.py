import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Dashboard GEE - ALCOA",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

pagina = st.sidebar.radio("Selecione a Página:", ["Resumo Geral EQ", "Desagregados por Categoria"])

if pagina == "Resumo Geral EQ":
    df = pd.read_csv(
    r"E:\MEUS DOCUMENTOS\1 UFRPE\3. MESTRADO ENG AMBIENTAL\INVENTÁRIO DE GEE\ALCOA\COMPILADOS\Resumo.csv",
    sep=';'
)
    df.columns = df.columns.str.strip()

    colunas_numericas = [
        'Escopo 1', 'Escopo 2 - Baseada na localização', 'Escopo 2 - Baseada na escolha de compra', 'Escopo 3',
        'EQ Escopo 1', 'EQ Escopo 2 - Baseada na localização', 'EQ Escopo 2 - Baseada na escolha de compra', 'EQ Escopo 3'
    ]
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", ".").str.replace(" ", "").str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df['ANO'] = pd.to_numeric(df['ANO'], errors='coerce').astype('Int64')

    with st.sidebar:
        st.title("🏢 Filtros")
        ano = st.selectbox("Ano:", sorted(df['ANO'].dropna().unique(), reverse=True))
        df = df[df['ANO'] == ano]
        rel = st.selectbox("Relatório:", sorted(df['Relatório'].dropna().unique()))
        df = df[df['Relatório'] == rel]
        nome = st.selectbox("Organização:", sorted(df['NOME'].dropna().unique()))
        df = df[df['NOME'] == nome]

        indicador = st.selectbox("🔍 Indicador EQ:", [
            'EQ Escopo 1', 'EQ Escopo 2 - Baseada na localização', 'EQ Escopo 2 - Baseada na escolha de compra', 'EQ Escopo 3'
        ])

    st.subheader("📊 Emissões de GEE (Indicadores EQ)")
    st.dataframe(df[['GEE'] + colunas_numericas], use_container_width=True)

    st.subheader("📄 Emissões de GEE (Escopos Diretos)")
    st.dataframe(df[['GEE', 'Escopo 1', 'Escopo 2 - Baseada na localização', 'Escopo 2 - Baseada na escolha de compra', 'Escopo 3']], use_container_width=True)

    ordem_gee = ['CO2', 'CH4', 'N2O', 'HFC', 'PFC', 'SF6', 'NF3']
    df_plot = df[['GEE', indicador]].dropna()
    df_plot = df_plot[df_plot['GEE'].isin(ordem_gee)]

    chart = alt.Chart(df_plot).mark_bar().encode(
        y=alt.Y('GEE:N', title='Tipo de GEE', sort=ordem_gee),
        x=alt.X(indicador, title=f'{indicador} (tCO2e)'),
        color=alt.value('#1f77b4'),
        tooltip=['GEE', indicador]
    ).properties(width=700, height=400, title=f"Emissões por GEE - {indicador}")

    st.subheader("📈 Gráfico de Emissão por Indicador EQ")
    st.altair_chart(chart, use_container_width=True)

elif pagina == "Desagregados por Categoria":
    df_cat = pd.read_csv(
    r"E:\MEUS DOCUMENTOS\1 UFRPE\3. MESTRADO ENG AMBIENTAL\INVENTÁRIO DE GEE\ALCOA\COMPILADOS\Desagregados por categoria.csv",
    sep=';'
)
    df_cat.columns = df_cat.columns.str.strip()

    for col in ['Emissões (tCO2e)', 'Emissões de CO2 biogênico (t)', 'Remoções de CO2 biogênico (t)']:
        df_cat[col] = df_cat[col].astype(str).str.replace(",", ".").str.strip()
        df_cat[col] = pd.to_numeric(df_cat[col], errors='coerce')

    with st.sidebar:
        st.title("📌 Filtros - Desagregados")
        ano = st.selectbox("Ano:", sorted(df_cat['ANO'].dropna().unique(), reverse=True))
        nome = st.selectbox("Organização:", sorted(df_cat['NOME'].dropna().unique()))
        escopo = st.selectbox("Escopo:", sorted(df_cat['ESCOPO'].dropna().unique()))
        rel = st.selectbox("Relatório:", sorted(df_cat['Relatório'].dropna().unique()))

    df_cat = df_cat[
        (df_cat['ANO'] == ano) &
        (df_cat['NOME'] == nome) &
        (df_cat['ESCOPO'] == escopo) &
        (df_cat['Relatório'] == rel)
    ]

    st.subheader("📄 Tabela Agregada por Categoria")
    tabela_agregada = df_cat.groupby(['NOME', 'ANO', 'Relatório', 'ESCOPO'], as_index=False)[
        ['Emissões (tCO2e)', 'Emissões de CO2 biogênico (t)', 'Remoções de CO2 biogênico (t)']
    ].sum()
    st.dataframe(tabela_agregada, use_container_width=True)

    st.subheader("📊 Gráfico 1: Emissões por Categoria")
    g1 = df_cat.groupby('Categoria', as_index=False)['Emissões (tCO2e)'].sum()
    chart1 = alt.Chart(g1).mark_bar().encode(
        x=alt.X('Categoria:N', sort='-y'),
        y=alt.Y('Emissões (tCO2e):Q'),
        tooltip=['Categoria', 'Emissões (tCO2e)']
    ).properties(width=800, height=400)
    st.altair_chart(chart1, use_container_width=True)

    st.subheader("📊 Gráfico 2: Todos Indicadores por Categoria")
    g2 = df_cat.groupby('Categoria', as_index=False)[
        ['Emissões (tCO2e)', 'Emissões de CO2 biogênico (t)', 'Remoções de CO2 biogênico (t)']
    ].sum()
    g2_melt = g2.melt(id_vars='Categoria', var_name='Indicador', value_name='Valor')

    chart2 = alt.Chart(g2_melt).mark_bar().encode(
        x=alt.X('Categoria:N', sort='-y'),
        y=alt.Y('Valor:Q'),
        color='Indicador:N',
        tooltip=['Categoria', 'Indicador', 'Valor']
    ).properties(width=800, height=400)
    st.altair_chart(chart2, use_container_width=True)
