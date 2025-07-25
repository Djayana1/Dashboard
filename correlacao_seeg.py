import streamlit as st
import pandas as pd

def mostrar_pagina_correlacao():
    st.title("Correlação entre Emissões da Alcoa e o SEEG Nacional")

    # Carregar os dados
    df_seeg = pd.read_csv("E:/Area de Trabalho/Dashboard/SEEG - Nacional.csv", sep=";", decimal=",")
    df_resumo = pd.read_csv("E:/Area de Trabalho/Dashboard/Resumo.csv", sep=";", decimal=",")
    
    # Padronizar colunas
    df_resumo.columns = df_resumo.columns.str.strip()
    df_seeg.columns = df_seeg.columns.str.strip()

    # Conversão de dados
    anos_validos = [str(ano) for ano in range(2019, 2024)]
    df_seeg[anos_validos] = df_seeg[anos_validos].apply(pd.to_numeric, errors="coerce")
    df_resumo["ANO"] = pd.to_numeric(df_resumo["ANO"], errors="coerce")

    for col in ["EQ Escopo 1", "EQ Escopo 2 - Baseada na localização", "EQ Escopo 2 - Baseada na escolha de compra"]:
        if col in df_resumo.columns:
            df_resumo[col] = df_resumo[col].astype(str).str.replace(",", ".").str.replace(" ", "")
            df_resumo[col] = pd.to_numeric(df_resumo[col], errors="coerce")

    # Sidebar - filtros
    st.sidebar.header("Filtros")
    ano = st.sidebar.selectbox("Ano", sorted(df_resumo["ANO"].dropna().unique(), reverse=True))
    setor_seeg = st.sidebar.selectbox("Setor de emissão (SEEG)", sorted(df_seeg["Setor de emissão"].dropna().unique()))
    empresa = st.sidebar.selectbox("Organização Alcoa", sorted(df_resumo["NOME"].dropna().unique()))

    # Filtro de dados da empresa
    df_emp = df_resumo[(df_resumo["ANO"] == ano) & (df_resumo["NOME"] == empresa)]

    # Filtro de dados SEEG
    seeg_valor = df_seeg[df_seeg["Setor de emissão"] == setor_seeg][str(ano)].sum()

    # Tabela de comparação
    def comparar_escopo(label, col_resumo):
        valor_emp = df_emp[col_resumo].sum() if col_resumo in df_emp.columns else 0
        participacao = (valor_emp / seeg_valor * 100) if seeg_valor > 0 else 0

        st.markdown(f"""
        #### 🔍 {label}
        - Emissões Alcoa: **{valor_emp:,.2f}** tCO₂e  
        - Emissões SEEG ({setor_seeg}): **{seeg_valor:,.2f}** tCO₂e  
        - Participação relativa: **{participacao:.2f}%**
        """)

        df_grafico = pd.DataFrame({
            "Origem": ["Alcoa", "Outros"],
            "Emissões (tCO₂e)": [valor_emp, max(seeg_valor - valor_emp, 0)]
        })
        st.bar_chart(df_grafico.set_index("Origem"))

    st.subheader("Comparação de EQ Escopo 1")
    comparar_escopo("Escopo 1: Combustão, Fugitivas, Processos Industriais", "EQ Escopo 1")

    st.subheader("Comparação de EQ Escopo 2 - Localização")
    comparar_escopo("Escopo 2 - Localização: Energia elétrica adquirida", "EQ Escopo 2 - Baseada na localização")

    st.subheader("EQ Escopo 2 - Escolha de Compra (sem correspondência no SEEG)")
    comparar_escopo("Escopo 2 - Escolha de compra (comparativo interno)", "EQ Escopo 2 - Baseada na escolha de compra")
