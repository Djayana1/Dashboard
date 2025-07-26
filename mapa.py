import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json

def mostrar_pagina_mapa(mostrar_legenda=False):
    st.subheader("Estado Selecionado")

    # Carregar dados
    df = pd.read_csv(
        r"E:\Area de Trabalho\Dashboard\Desagregados por categoria.csv",
        sep=';',
        decimal=',',
        thousands='.',
        encoding='utf-8'
    )

    # Carregar GeoJSON
    with open(r"E:\Area de Trabalho\Dashboard\br_states.json", encoding='utf-8') as f:
        geojson = json.load(f)

    # Sidebar: estado para destaque
    estados_disponiveis = sorted(df["ESTADO"].dropna().unique())
    estado_destacado = st.sidebar.selectbox("Estado para destaque", estados_disponiveis)

    # Agrupar dados
    col_valor = "Emissões (tCO2e)"
    df_grouped = df.groupby("ESTADO")[col_valor].sum().reset_index()
    df_grouped[col_valor] = pd.to_numeric(df_grouped[col_valor], errors="coerce").fillna(0)

    # Criar df_full com todos os estados + merge
    estados_geojson = [f["properties"]["SIGLA"] for f in geojson["features"]]
    df_full = pd.DataFrame({"ESTADO": estados_geojson}).merge(df_grouped, on="ESTADO", how="left").fillna(0)
    df_full[col_valor] = pd.to_numeric(df_full[col_valor], errors="coerce").fillna(0)

    # Criar coluna de cor: 0=cinza, 1=azul, 2=amarelo (selecionado)
    def definir_cor(row):
        if row["ESTADO"] == estado_destacado:
            return 2
        elif row[col_valor] > 0:
            return 1
        else:
            return 0

    df_full["COR"] = df_full.apply(definir_cor, axis=1)

    # Criar mapa com cores fixas para cada categoria
    fig = go.Figure(go.Choropleth(
        geojson=geojson,
        locations=df_full["ESTADO"],
        z=df_full["COR"],
        featureidkey="properties.SIGLA",
        colorscale=[
            [0, "lightgrey"],       # sem dados
            [0.333, "lightgrey"],
            [0.334, "#09c6fc"],     # azul personalizado
            [0.666, "#09c6fc"],
            [0.667, "#f0f082"],     # amarelo fundo selecionado
            [1, "#C5AB19"]
        ],
        zmin=0,
        zmax=2,
        colorbar_title="",
        marker_line_color="black",
        marker_line_width=0.5,
        text=df_full.apply(lambda row: f"{row['ESTADO']}: {row[col_valor]:,.2f} tCO2e", axis=1),
        hoverinfo="text"
    ))

    # Overlay: destacar estado selecionado
    for feature in geojson["features"]:
        if feature["properties"]["SIGLA"] == estado_destacado:
            geometry = feature["geometry"]
            if geometry["type"] == "Polygon":
                for coords in geometry["coordinates"]:
                    lons, lats = zip(*coords)
                    fig.add_trace(go.Scattergeo(
                        lon=lons,
                        lat=lats,
                        mode="lines",
                        line=dict(width=2, color="#C5AB19"),
                        fill="toself",
                        fillcolor="#ffff98",
                        name=estado_destacado
                    ))
            elif geometry["type"] == "MultiPolygon":
                for polygon in geometry["coordinates"]:
                    for coords in polygon:
                        lons, lats = zip(*coords)
                        fig.add_trace(go.Scattergeo(
                            lon=lons,
                            lat=lats,
                            mode="lines",
                            line=dict(width=2, color="#C5AB19"),
                            fill="toself",
                            fillcolor="#ffff98",
                            name=estado_destacado
                        ))

    fig.update_geos(fitbounds="locations", visible=False)
    

    st.plotly_chart(fig, use_container_width=True)
