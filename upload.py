import streamlit as st
import pandas as pd

# Título da página
st.title("📥 Upload e Integração de Dados do GHG Protocol")

# Formulário para preenchimento de metadados
with st.form("formulario_ghg"):
    st.subheader("Preencha os dados da organização")
    nome = st.text_input("Nome da empresa")
    cnpj = st.text_input("CNPJ")
    estado = st.selectbox("Estado", ["SP", "MG", "PA", "MA"])
    ano = st.number_input("Ano do inventário", min_value=2000, max_value=2050, step=1, value=2023)
    relatorio = st.selectbox("Tipo de Relatório", ["Controle Operacional", "Participação Acionária"])
    arquivo = st.file_uploader("Selecione o arquivo do GHG Protocol (.xlsx)", type="xlsx")
    enviar = st.form_submit_button("Executar ETL e Integrar")

if enviar and arquivo:
    try:
        # Leitura das abas com Escopo 1 e 2
        df1 = pd.read_excel(arquivo, sheet_name="Registro Público de Emissões", skiprows=45, nrows=20, usecols="A:D", engine="openpyxl")
        df2 = pd.read_excel(arquivo, sheet_name="Registro Público de Emissões", skiprows=69, nrows=20, usecols="A:D", engine="openpyxl")

        df1.columns = ["Categoria", "Emissões (tCO2e)", "Emissões de CO2 biogênico (t)", "Remoções de CO2 biogênico (t)"]
        df1["ESCOPO"] = "Escopo 1"
        df2.columns = df1.columns[:-1] + ["ESCOPO"]
        df2["ESCOPO"] = "Escopo 2"

        df_final = pd.concat([df1, df2], ignore_index=True)
        df_final = df_final[df_final["Categoria"].notna() & ~df_final["Categoria"].astype(str).str.lower().str.contains("total")]

        # Adiciona os metadados
        df_final["NOME"] = nome
        df_final["CNPJ"] = cnpj
        df_final["ANO"] = ano
        df_final["Relatório"] = relatorio
        df_final["ESTADO"] = estado

        df_final = df_final[[
            "NOME", "CNPJ", "ESTADO", "ANO", "Relatório", "ESCOPO",
            "Categoria", "Emissões (tCO2e)", "Emissões de CO2 biogênico (t)", "Remoções de CO2 biogênico (t)"
        ]]

        # Leitura do arquivo existente local
        caminho = r"E:\\Area de Trabalho\\Dashboard\\Desagregados por categoria.csv"
        df_existente = pd.read_csv(caminho, sep=";", decimal=",", encoding="utf-8")

        # Conversão dos números
        for col in ["Emissões (tCO2e)", "Emissões de CO2 biogênico (t)", "Remoções de CO2 biogênico (t)"]:
            df_final[col] = pd.to_numeric(df_final[col], errors="coerce").fillna(0)

        # Juntar e salvar
        df_novo = pd.concat([df_existente, df_final], ignore_index=True)
        df_novo.to_csv(caminho, sep=";", index=False, encoding="utf-8", decimal=",")

        st.success("✅ Dados integrados com sucesso ao arquivo de desagregados!")
        st.dataframe(df_final)

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
