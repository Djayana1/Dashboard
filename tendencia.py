import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def mostrar_pagina_tendencia():
    st.title("Tendência – Emissões Equivalentes ao CO2 por Ano")


    # Carregar dados
    caminho = r"E:\Area de Trabalho\Dashboard\Resumo.csv"
    df = pd.read_csv(caminho, sep=";", decimal=",", encoding="latin1")

    # Corrigir nomes de colunas
    df.rename(columns={
        "EQ Escopo 2 - Baseada na localizaÃ§Ã£o": "EQ Escopo 2 - Baseada na localização",
        "EQ Escopo 2 - Baseada na escolha de compra": "EQ Escopo 2 - Baseada na escolha de compra"
    }, inplace=True)

    colunas_eq = [
        "EQ Escopo 1",
        "EQ Escopo 2 - Baseada na localização",
        "EQ Escopo 2 - Baseada na escolha de compra"
    ]

    # Conversões
    df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce").astype("Int64")
    for col in colunas_eq:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Sidebar: seleção de escopos
    st.sidebar.header("Filtros")
    escopos_selecionados = st.sidebar.multiselect(
        "Selecione os escopos EQ para análise", colunas_eq, default=colunas_eq
    )

    if not escopos_selecionados:
        st.warning("⚠️ Selecione pelo menos um escopo.")
        return

    # Soma por ano apenas dos escopos selecionados
    df["Total EQ"] = df[escopos_selecionados].sum(axis=1)
    df_agrupado = df.groupby("ANO")["Total EQ"].sum().reset_index()

    # Gráfico de linha interativo (Plotly)
    
    fig = px.line(
        df_agrupado,
        x="ANO",
        y="Total EQ",
        text=df_agrupado["Total EQ"].apply(lambda x: f"{x:,.0f}"),
        markers=True,
        title="Tendência das Emissões EQ (soma dos escopos selecionados)",
        labels={"ANO": "Ano", "Total EQ": "Emissões (tCO2e)"}
    )

    fig.update_traces(
        line=dict(color="#1f77b4", width=3),
        textposition="top center",
        mode="lines+markers+text"
    )
    fig.update_layout(
        xaxis=dict(tickmode="linear", tickformat=".0f")
    )
    st.plotly_chart(fig, use_container_width=True)


    # Gráfico de dispersão com regressão linear
    st.subheader("Dispersão com Regressão Linear")

    X = df_agrupado["ANO"].astype(int).values.reshape(-1, 1)
    y = df_agrupado["Total EQ"].astype(float).values

    modelo = LinearRegression()
    modelo.fit(X, y)
    y_pred = modelo.predict(X)

    coef = modelo.coef_[0]
    inter = modelo.intercept_
    r2 = r2_score(y, y_pred)
    tendencia = "aumentando" if coef > 0 else "diminuindo" if coef < 0 else "estável ⚖️"

    fig2, ax = plt.subplots(figsize=(6, 3))
    ax.scatter(X, y, color="blue", label="Dados")
    ax.plot(X, y_pred, color="red", label="Regressão Linear")

    # Adicionar rótulos com ano e valor
    for i in range(len(X)):
        ano = df_agrupado["ANO"].iloc[i]
        valor = df_agrupado["Total EQ"].iloc[i]
        ax.annotate(f"{ano}\n{valor:,.0f}", (X[i], y[i]), textcoords="offset points", xytext=(0, 6), ha='center', fontsize=5)

    ax.set_xlabel("Ano")
    ax.set_ylabel("Emissões EQ (tCO₂e)")
    ax.set_title("Dispersão - Emissões EQ ao longo do tempo")
    ax.legend()
    st.pyplot(fig2)

    # Resultados estatísticos
    st.markdown(f"""
    ### Resultados da Regressão Linear
    - **Tendência:** {tendencia}
    - **Equação:** `y = {coef:.2f}x + {inter:,.2f}`
    - **R² (Coeficiente de determinação):** `{r2:.4f}`
    """)
