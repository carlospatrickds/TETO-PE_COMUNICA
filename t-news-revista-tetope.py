import streamlit as st
import os
import base64
from streamlit.components.v1 import html
from config import SENHA_ACESSO, COR_FUNDO, NOME_PROJETO

st.set_page_config(layout="wide")

# =========================
# 🎨 ESTILO
# =========================
st.markdown(f"""
    <style>
    body {{
        background-color: {COR_FUNDO};
    }}
    .titulo {{
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        margin-bottom: 10px;
    }}
    </style>
""", unsafe_allow_html=True)

# =========================
# 🔐 AUTENTICAÇÃO
# =========================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.image("logo.png", width=200)
    senha = st.text_input("Digite a senha de acesso", type="password")
    if senha == SENHA_ACESSO:
        st.session_state.autenticado = True
        st.rerun()
    else:
        st.stop()

# =========================
# 🏷️ CABEÇALHO
# =========================
st.image("logo.png", width=180)
st.markdown(f"<div class='titulo'>{NOME_PROJETO}</div>", unsafe_allow_html=True)

# =========================
# 📚 HISTÓRICO AUTOMÁTICO
# =========================
pasta_edicoes = "edicoes"
edicoes = sorted(os.listdir(pasta_edicoes), reverse=True)

query_params = st.query_params
edicao_url = query_params.get("edicao", None)

if edicao_url and edicao_url in edicoes:
    edicao_escolhida = edicao_url
else:
    edicao_escolhida = st.selectbox("Selecione a edição", edicoes)

caminho_pdf = os.path.join(pasta_edicoes, edicao_escolhida)

# =========================
# 📥 BOTÃO DOWNLOAD
# =========================
with open(caminho_pdf, "rb") as f:
    st.download_button(
        label="⬇ Baixar PDF",
        data=f,
        file_name=edicao_escolhida,
        mime="application/pdf"
    )

# =========================
# 📖 FLIPBOOK
# =========================
with open(caminho_pdf, "rb") as f:
    base64_pdf = base64.b64encode(f.read()).decode("utf-8")

pdf_display = f"""
<!DOCTYPE html>
<html>
<head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.14.305/pdf.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/page-flip/2.0.7/js/page-flip.browser.min.js"></script>
<style>
body {{
    display: flex;
    justify-content: center;
}}
#flipbook {{
    width: 800px;
    height: 600px;
}}
</style>
</head>
<body>
<div id="flipbook"></div>
<script>
const pdfData = atob("{base64_pdf}");
const pdfjsLib = window['pdfjs-dist/build/pdf'];
pdfjsLib.GlobalWorkerOptions.workerSrc =
'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.14.305/pdf.worker.min.js';

const loadingTask = pdfjsLib.getDocument({{data: pdfData}});
loadingTask.promise.then(function(pdf) {{

const pageFlip = new St.PageFlip(
    document.getElementById("flipbook"),
    {{
        width: 400,
        height: 600,
        showCover: true
    }}
);

let pages = [];

for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {{
    pdf.getPage(pageNum).then(function(page) {{
        const viewport = page.getViewport({{scale: 1}});
        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");

        canvas.width = viewport.width;
        canvas.height = viewport.height;

        page.render({{
            canvasContext: context,
            viewport: viewport
        }}).promise.then(function() {{
            pages.push(canvas);
            if (pages.length === pdf.numPages) {{
                pageFlip.loadFromHTML(pages.map(p => {{
                    const div = document.createElement("div");
                    div.appendChild(p);
                    return div;
                }}));
            }}
        }});
    }});
}}
}});
</script>
</body>
</html>
"""

html(pdf_display, height=700)
