import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def mostrar_pagina_tendencia():
    st.title("Tendência – Emissões (tCO2e) por Ano")


    # Carregar dados
    caminho = pd.read_csv("Resumo.csv", sep=';')
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
        "Selecione os escopos para análise", colunas_eq, default=colunas_eq
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
    title="Tendência das Emissões (tCO2e) (soma dos escopos selecionados)",
    labels={"ANO": "Ano", "Total EQ": "Emissões (tCO2e)"}
)

    fig.update_traces(
    line=dict(color="black", width=3),
    marker=dict(color="black"),
    textposition="top center",
    textfont=dict(size=14, color="black"),
    mode="lines+markers+text"
)

    fig.update_layout(
    font=dict(size=14, color="black"),  # fonte geral
    title_font=dict(size=18, color="black"),  # título
    xaxis=dict(
        title_font=dict(size=16, color="black"),
        tickfont=dict(size=12, color="black"),
        tickmode="linear",
        tickformat=".0f"
    ),
    yaxis=dict(
        title_font=dict(size=16, color="black"),
        tickfont=dict(size=12, color="black")
    )
)

    st.plotly_chart(fig, use_container_width=True)

# 🔽 Novo gráfico: Tendência individual por escopo ao longo dos anos
    st.subheader("Tendência por Escopo (tCO2e) ao longo dos Anos")

# Agrupar por ano e somar os escopos
    df_por_ano = df.groupby("ANO")[escopos_selecionados].sum().reset_index()

# Derreter para formato longo
    df_melt = df_por_ano.melt(id_vars="ANO", value_vars=escopos_selecionados, 
                          var_name="Escopo", value_name="Emissões")

# Gráfico de linha com uma linha para cada escopo
    
    fig_escopos = px.line(
    df_melt,
    x="ANO",
    y="Emissões",
    color="Escopo",
    markers=True,
    title="Tendência por Escopo (tCO2e)",
    labels={"ANO": "Ano", "Emissões": "Emissões (tCO2e)"}
)

    fig_escopos.update_traces(
    text=df_melt["Emissões"].apply(lambda x: f"{x:,.0f}"),
    textposition="top center",
    textfont=dict(size=12, color="black"),
    mode="lines+markers+text"
)

    fig_escopos.update_layout(
    font=dict(size=14, color="black"),
    title_font=dict(size=18, color="black"),
    xaxis=dict(
        title_font=dict(size=16, color="black"),
        tickfont=dict(size=12, color="black"),
        tickmode="linear"
    ),
    yaxis=dict(
        title_font=dict(size=16, color="black"),
        tickfont=dict(size=12, color="black")
    ),
    legend_title=dict(text="Escopo", font=dict(size=14, color="black")),
    legend=dict(font=dict(size=12, color="black"))
)

    st.plotly_chart(fig_escopos, use_container_width=True)

    
    # Exibir tabela formatada com separador de milhar
    # Formatar valores numéricos
    df_formatado = df_por_ano.copy()
    for col in escopos_selecionados:
        df_formatado[col] = df_formatado[col].apply(lambda x: f"{x:,.0f}")

    # Estilo: preto no corpo e no cabeçalho
    st.dataframe(
        df_formatado.style
            .set_properties(**{
                'color': 'black',
                'font-size': '14px',
                'font-family': 'Arial'
            })  # estilo para o corpo da tabela
            .set_table_styles([
                {
                    'selector': 'th',
                    'props': [('color', 'black'), ('font-size', '14px'), ('font-family', 'Arial')]
                }
            ]),  # estilo para o cabeçalho
        use_container_width=True
    )


    # Botão para download da tabela em CSV
    csv_eq_por_ano = df_por_ano.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="⬇️ Baixar CSV - Totais dos Escopos por Ano",
        data=csv_eq_por_ano,
        file_name="totais_escopos_por_ano.csv",
        mime="text/csv"
    )


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