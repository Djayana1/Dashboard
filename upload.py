import streamlit as st
import pandas as pd
import os

def mostrar_pagina_upload_etl():
    st.title("📤 Upload e Integração de Dados")

    # Inputs manuais do usuário
    nome = st.text_input("Nome da Organização")
    cnpj = st.text_input("CNPJ")
    estado = st.text_input("Estado (sigla)")
    ano = st.number_input("Ano do Inventário", min_value=2000, max_value=2100, step=1, value=2023)
    relatorio = st.selectbox("Tipo de Relatório", ["Controle Operacional", "Equivalência"])

    # Upload do arquivo
    arquivo = st.file_uploader("Envie o arquivo Excel (GHG Protocol)", type=["xlsx"])

    if arquivo and nome and cnpj and estado and relatorio:
        try:
            df_ghg = pd.read_excel(arquivo, sheet_name="Registro Público de Emissões", skiprows=17, nrows=7)
            df_ghg = df_ghg.rename(columns={
                "GEE": "GEE",
                "Escopo 1.1": "Escopo 1",
                "Escopo 1.5": "EQ Escopo 1"
            })

            gases = ["CO2", "CH4", "N2O", "HFC", "PFC", "SF6", "NF3"]
            df_ghg = df_ghg[df_ghg["GEE"].isin(gases)]

            # Adiciona colunas fixas
            df_ghg["NOME"] = nome
            df_ghg["CNPJ"] = cnpj
            df_ghg["ESTADO"] = estado
            df_ghg["ANO"] = ano
            df_ghg["Relatório"] = relatorio

            # Preenche as colunas que faltam com None
            colunas_finais = [
                "NOME", "CNPJ", "ESTADO", "ANO", "Relatório", "GEE",
                "Escopo 1", "Escopo 2 - Baseada na localização", "Escopo 2 - Baseada na escolha de compra", "Escopo 3",
                "EQ Escopo 1", "EQ Escopo 2 - Baseada na localização", "EQ Escopo 2 - Baseada na escolha de compra", "EQ Escopo 3"
            ]
            for col in colunas_finais:
                if col not in df_ghg.columns:
                    df_ghg[col] = None

            df_formatado = df_ghg[colunas_finais]

            st.success("✅ Dados extraídos com sucesso. Pronto para salvar.")
            st.dataframe(df_formatado)

            # Botão para salvar no Resumo.csv
            if st.button("➕ Adicionar ao Resumo.csv"):
                salvar_em_resumo(df_formatado)

        except Exception as e:
            st.error(f"❌ Erro ao processar o arquivo: {e}")

def salvar_em_resumo(novos_dados):
    caminho_resumo = r"E:\Area de Trabalho\Dashboard\Resumo.csv"

    if not os.path.exists(caminho_resumo):
        st.error("Arquivo 'Resumo.csv' não encontrado.")
        return

    try:
        resumo_atual = pd.read_csv(caminho_resumo, sep=";", decimal=",", encoding="latin1")
        df_unido = pd.concat([resumo_atual, novos_dados], ignore_index=True)
        df_unido.to_csv(caminho_resumo, sep=";", decimal=",", index=False, encoding="latin1")
        st.success("✅ Dados adicionados ao arquivo Resumo.csv com sucesso!")
    except Exception as e:
        st.error(f"Erro ao salvar no Resumo.csv: {e}")
