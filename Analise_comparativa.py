import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


def mostrar_pagina_comparacao():
    st.title("Correlação entre Emissões da Alcoa e o SEEG Nacional")

    # Carregar os dados
    df_seeg = pd.read_csv("E:/Area de Trabalho/Dashboard/SEEG - Nacional.csv", sep=";", decimal=",")
    df_alcoa = pd.read_csv("E:/Area de Trabalho/Dashboard/Desagregados por categoria.csv", sep=";", decimal=",")

    # Conversão de tipos
    anos_validos = [str(ano) for ano in range(2019, 2024)]
    df_seeg[anos_validos] = df_seeg[anos_validos].apply(pd.to_numeric, errors="coerce")
    df_alcoa["ANO"] = pd.to_numeric(df_alcoa["ANO"], errors="coerce")
    df_alcoa["Emissões (tCO2e)"] = pd.to_numeric(df_alcoa["Emissões (tCO2e)"], errors="coerce")

    # Filtros da sidebar
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

    # Filtro SEEG
    if setor_seeg != "Todos":
        seeg_filtrado = df_seeg[df_seeg["Setor de emissão"] == setor_seeg]
    else:
        seeg_filtrado = df_seeg.copy()

    seeg_filtrado = seeg_filtrado[
        (seeg_filtrado["Emissão/Remoção/Bunker"] == "Emissão") &
        (seeg_filtrado["Gás"] == "CO2e (t) GWP-AR6")
    ]
    seeg_total = seeg_filtrado[str(ano)].sum()

    # Filtro Alcoa
    if "Todas" not in categorias_alcoa:
        alcoa_filtrado = df_alcoa[(df_alcoa["Categoria"].isin(categorias_alcoa)) & (df_alcoa["ANO"] == ano)]
    else:
        alcoa_filtrado = df_alcoa[df_alcoa["ANO"] == ano]

    alcoa_total = alcoa_filtrado["Emissões (tCO2e)"].sum()

    percentual = (alcoa_total / seeg_total * 100) if seeg_total else 0

    # Exibição
    st.markdown(f"""
    ### Comparação entre Alcoa e SEEG ({ano})
    - **Setor Nacional (SEEG):** `{setor_seeg}`
    - **Categorias Selecionadas:** `{', '.join(categorias_alcoa) if categorias_alcoa else 'Nenhuma'}`
    - **Emissões da Alcoa:** `{alcoa_total:,.2f}` tCO₂e  
    - **Total Nacional no SEEG:** `{seeg_total:,.2f}` tCO₂e  
    - **Participação da Alcoa:** **{percentual:.2f}%**
    """)

    if seeg_total > 0:
        st.subheader("Proporção de emissões")
        df_grafico = pd.DataFrame({
            "Origem": ["Alcoa", "Outros"],
            "Emissões (tCO₂e)": [alcoa_total, max(seeg_total - alcoa_total, 0)]
        })
        st.bar_chart(df_grafico.set_index("Origem"))

        # --- Gráfico de Dispersão ---
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

        if "Todas" not in categorias_alcoa:
            alcoa_serie = df_alcoa[df_alcoa["Categoria"].isin(categorias_alcoa)]
        else:
            alcoa_serie = df_alcoa.copy()
        alcoa_serie = alcoa_serie.groupby("ANO")["Emissões (tCO2e)"].sum().reset_index()

        df_disp = pd.merge(alcoa_serie, seeg_serie, on="ANO", how="inner")

        if not df_disp.empty:
            X = df_disp["SEEG_Emissoes"].values.reshape(-1, 1)
            y = df_disp["Emissões (tCO2e)"].values
            modelo = LinearRegression().fit(X, y)
            y_pred = modelo.predict(X)

            fig, ax = plt.subplots(figsize=(8, 5))
            ax.scatter(df_disp["SEEG_Emissoes"], y, color="blue", label="Dados")
            ax.plot(df_disp["SEEG_Emissoes"], y_pred, color="red", label="Regressão Linear")
            for i, row in df_disp.iterrows():
                ax.annotate(str(row["ANO"]), (row["SEEG_Emissoes"], row["Emissões (tCO2e)"]), fontsize=9)
            ax.set_title("Dispersão - Emissões da Alcoa vs SEEG")
            ax.set_xlabel("Emissões SEEG (tCO₂e)")
            ax.set_ylabel("Emissões Alcoa (tCO₂e)")
            ax.legend()
            ax.grid(True)

            st.pyplot(fig)
    else:
        st.info("Nenhum dado encontrado para o setor SEEG selecionado nesse ano.")
