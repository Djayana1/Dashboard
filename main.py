import streamlit as st
from resumo_geral_eq import mostrar_pagina_resumo
from desagregados_categoria import mostrar_pagina_categoria
from mapa import mostrar_pagina_mapa
from tendencia import mostrar_pagina_tendencia
from Analise_comparativa import mostrar_pagina_comparacao
from upload import mostrar_pagina_upload_etl

# Configuração da interface
st.set_page_config(page_title="Dashboard GEE - ALCOA", layout="wide")

# Sidebar de navegação
pagina = st.sidebar.radio(
    "Selecione a Página:",
    ["Carregue Seus Dados", "Resumo Geral EQ", "Desagregados por Categoria", "Tendência de Emissão", "Análise comparativa com SEEG"]
)

# Rotas para cada página
if pagina == "Carregue Seus Dados":
    mostrar_pagina_upload_etl()

elif pagina == "Resumo Geral EQ":
    mostrar_pagina_resumo()

elif pagina == "Desagregados por Categoria":
    mostrar_pagina_categoria()

elif pagina == "Mapa Interativo":
    mostrar_pagina_mapa()

elif pagina == "Tendência de Emissão":
    mostrar_pagina_tendencia()

elif pagina == "Análise comparativa com SEEG":
    mostrar_pagina_comparacao()


