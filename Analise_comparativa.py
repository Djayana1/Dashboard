import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

def mostrar_pagina_comparacao():
    st.title("Correlação entre Emissões da Alcoa e o SEEG Nacional")

    # Carregar os dados
    df_seeg = pd.read_csv("SEEG - Nacional.csv", sep=";", decimal=",")
    df_alcoa = pd.read_csv("Desagregados por categoria.csv", sep=";", decimal=",")

    # Conversão de tipos
    anos_validos = [str(ano) for ano in range(2019, 2024)]
    df_seeg[anos_validos] = df_seeg[anos_validos].apply(pd.to_numeric, errors="coerce")
    df_alcoa["ANO"] = pd.to_numeric(df_alcoa["ANO"], errors="coerce")
    df_alcoa["Emissões (tCO2e)"] = pd.to_numeric(df_alcoa["Emissões (tCO2e)"], errors="coerce")

    # Filtros
    st.sidebar.header("Filtros de comparação")
    ano = st.sidebar.selectbox("Ano", list(range(2019, 2024)))
    setores_seeg = sorted(df_seeg["Setor de emissão"].dropna().unique())
    setor_seeg = st.sidebar.selectbox("Categoria de emissão (SEEG)", ["Todos"] + setores_seeg)
    categorias_opcoes = sorted(df_alcoa["Categoria"].dropna().unique())
    categorias_alcoa = st.sidebar.multiselect(
        "Categorias da empresa Alcoa",
        options=["Todas"] + categorias_opcoes,
        default=["Todas"]
    )

    # Filtrar SEEG
    seeg_filtrado = df_seeg.copy()
    if setor_seeg != "Todos":
        seeg_filtrado = seeg_filtrado[seeg_filtrado["Setor de emissão"] == setor_seeg]
    seeg_filtrado = seeg_filtrado[
        (seeg_filtrado["Emissão/Remoção/Bunker"] == "Emissão") &
        (seeg_filtrado["Gás"] == "CO2e (t) GWP-AR6")
    ]
    seeg_total = seeg_filtrado[str(ano)].sum()

    # Filtrar Alcoa
    if "Todas" not in categorias_alcoa:
        alcoa_filtrado = df_alcoa[(df_alcoa["Categoria"].isin(categorias_alcoa)) & (df_alcoa["ANO"] == ano)]
    else:
        alcoa_filtrado = df_alcoa[df_alcoa["ANO"] == ano]
    alcoa_total = alcoa_filtrado["Emissões (tCO2e)"].sum()

    percentual = (alcoa_total / seeg_total * 100) if seeg_total else 0

    # Texto resumo
    st.markdown(f"""
    ### Comparação entre Alcoa e SEEG ({ano})
    - **Setor Nacional (SEEG):** `{setor_seeg}`
    - **Categorias Selecionadas:** `{', '.join(categorias_alcoa) if categorias_alcoa else 'Nenhuma'}`
    - **Emissões da Alcoa:** `{alcoa_total:,.2f}` tCO₂e  
    - **Total Nacional no SEEG:** `{seeg_total:,.2f}` tCO₂e  
    - **Participação da Alcoa:** **{percentual:.2f}%**
    """)

    if seeg_total > 0:
        # Gráfico de linha com variação por ano (Alcoa vs SEEG)
        st.subheader("Tendência das Emissões por Ano – Alcoa vs SEEG")

        # Série temporal SEEG
        seeg_series = df_seeg[
            (df_seeg["Emissão/Remoção/Bunker"] == "Emissão") &
            (df_seeg["Gás"] == "CO2e (t) GWP-AR6")
        ]
        if setor_seeg != "Todos":
            seeg_series = seeg_series[seeg_series["Setor de emissão"] == setor_seeg]

        seeg_ano = seeg_series[anos_validos].sum().reset_index()
        seeg_ano.columns = ["ANO", "Emissões SEEG"]
        seeg_ano["ANO"] = seeg_ano["ANO"].astype(int)

        # Série temporal Alcoa
        if "Todas" not in categorias_alcoa:
            alcoa_series = df_alcoa[df_alcoa["Categoria"].isin(categorias_alcoa)]
        else:
            alcoa_series = df_alcoa.copy()

        alcoa_ano = alcoa_series.groupby("ANO")["Emissões (tCO2e)"].sum().reset_index()
        alcoa_ano.columns = ["ANO", "Emissões Alcoa"]

        # Combinar
        df_linha = pd.merge(seeg_ano, alcoa_ano, on="ANO", how="inner")
        df_linha = df_linha.melt(id_vars="ANO", var_name="Origem", value_name="Emissões (tCO₂e)")

        # Gráfico de linha
        fig_linha = px.line(
            df_linha,
            x="ANO",
            y="Emissões (tCO₂e)",
            color="Origem",
            markers=True,
            text=df_linha["Emissões (tCO₂e)"].apply(lambda x: f"{x:,.0f}"),
            title="Tendência das Emissões da Alcoa e SEEG (2019–2023)"
        )

        fig_linha.update_traces(
            textposition="top center",
            textfont=dict(size=14, color="black")
        )

        fig_linha.update_layout(
            height=400,
            font=dict(color="black", size=14),
            title_font=dict(size=18, color="black"),
            xaxis_title="Ano",
            yaxis_title="Emissões (tCO₂e)",
            yaxis=dict(tickfont=dict(color="black")),
            xaxis=dict(tickfont=dict(color="black")),
            plot_bgcolor="white"
        )

        st.plotly_chart(fig_linha, use_container_width=False)

        # Tabela comparativa de emissões por ano (Alcoa vs SEEG)
        st.subheader("Tabela – Emissões por Ano (Alcoa x SEEG)")

        # Juntar as séries em um único DataFrame
        tabela_comparativa = pd.merge(seeg_ano, alcoa_ano, on="ANO", how="inner")
        tabela_formatada = tabela_comparativa.copy()

        # Formatar os valores com separador de milhar
        tabela_formatada["Emissões SEEG"] = tabela_formatada["Emissões SEEG"].apply(lambda x: f"{x:,.0f}")
        tabela_formatada["Emissões Alcoa"] = tabela_formatada["Emissões Alcoa"].apply(lambda x: f"{x:,.0f}")

        # Exibir a tabela
        st.dataframe(tabela_formatada, use_container_width=True)



        # Gráfico de dispersão com regressão
        st.subheader("Dispersão entre Emissões da Alcoa e SEEG (2019–2023)")
        seeg_serie = df_seeg[
            (df_seeg["Emissão/Remoção/Bunker"] == "Emissão") &
            (df_seeg["Gás"] == "CO2e (t) GWP-AR6")
        ]
        if setor_seeg != "Todos":
            seeg_serie = seeg_serie[seeg_serie["Setor de emissão"] == setor_seeg]
        seeg_serie = seeg_serie[anos_validos].sum().reset_index()
        seeg_serie.columns = ["ANO", "SEEG_Emissoes"]
        seeg_serie["ANO"] = seeg_serie["ANO"].astype(int)

        alcoa_serie = df_alcoa.copy()
        if "Todas" not in categorias_alcoa:
            alcoa_serie = alcoa_serie[alcoa_serie["Categoria"].isin(categorias_alcoa)]
        alcoa_serie = alcoa_serie.groupby("ANO")["Emissões (tCO2e)"].sum().reset_index()

        df_disp = pd.merge(alcoa_serie, seeg_serie, on="ANO", how="inner")

        if not df_disp.empty:
            X = df_disp["SEEG_Emissoes"].values.reshape(-1, 1)
            y = df_disp["Emissões (tCO2e)"].values
            modelo = LinearRegression().fit(X, y)
            y_pred = modelo.predict(X)
            a = modelo.coef_[0]
            b = modelo.intercept_
            r2 = r2_score(y, y_pred)

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.scatter(df_disp["SEEG_Emissoes"], y, color="blue", label="Dados")
            ax.plot(df_disp["SEEG_Emissoes"], y_pred, color="red", label="Regressão Linear")
            for i, row in df_disp.iterrows():
                ax.annotate(str(row["ANO"]), (row["SEEG_Emissoes"], row["Emissões (tCO2e)"]), fontsize=6)
            ax.set_title("Dispersão - Emissões da Alcoa vs SEEG", fontsize=11)
            ax.set_xlabel("Emissões SEEG (tCO₂e)", fontsize=10)
            ax.set_ylabel("Emissões Alcoa (tCO₂e)", fontsize=10)
            ax.tick_params(axis='both', labelsize=8)
            ax.legend(fontsize=8)
            ax.grid(True)
            st.pyplot(fig)

            # Equação exibida abaixo do gráfico com fonte maior
            st.markdown(f"""
            <div style="font-size:18px; color:black;">
                <strong>Equação da Regressão Linear:</strong><br>
                y = {a:.2f}x + {b:,.0f} <br>
                <strong>R² = {r2:.4f}</strong>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.info("Nenhum dado encontrado para o setor SEEG selecionado nesse ano.")
