import streamlit as st
import pandas as pd
import json
from io import BytesIO, StringIO

st.set_page_config(
    page_title="Data Converter",
    page_icon="",
    layout="wide"
)

st.title("Data Converter")
st.markdown("Conversor de arquivos: **CSV, Excel, JSON, Parquet, TSV** e mais.")

st.sidebar.header("Configurações de Leitura")

uploaded_file = st.sidebar.file_uploader(
    "Escolha um arquivo para upload",
    type=["csv", "xlsx", "xls", "json", "parquet", "tsv", "txt", "feather", "dict py"]
)

# Opções específicas por tipo
sep = st.sidebar.selectbox("Separador (CSV/TSV/TXT)", [",", ";", "\t", "|", "auto"], index=0)
encoding = st.sidebar.selectbox("Encoding", ["utf-8", "latin1", "iso-8859-1", "cp1252"], index=0)
sheet_name = st.sidebar.text_input("Nome da aba (Excel)", value="0")  # 0 = primeira aba
json_orient = st.sidebar.selectbox(
    "Orientação do JSON",
    ["records", "columns", "index", "split", "table", "values"],
    index=0
)

df = None
file_type = None

if uploaded_file is not None:
    file_type = uploaded_file.name.split(".")[-1].lower()
    st.sidebar.success(f"Arquivo detectado: **.{file_type}**")

    try:
        if file_type in ["csv", "txt"]:
            # Detecta separador automaticamente se escolhido "auto"
            if sep == "auto":
                df = pd.read_csv(uploaded_file, sep=None, engine="python", encoding=encoding)
            else:
                real_sep = "\t" if sep == "\\t" else sep
                df = pd.read_csv(uploaded_file, sep=real_sep, encoding=encoding)

        elif file_type == "tsv":
            df = pd.read_csv(uploaded_file, sep="\t", encoding=encoding)

        elif file_type in ["xlsx", "xls"]:
            # Tenta converter sheet_name para int se for número
            try:
                sheet = int(sheet_name)
            except ValueError:
                sheet = sheet_name
            df = pd.read_excel(uploaded_file, sheet_name=sheet, engine="openpyxl")

        elif file_type == "json":
            content = uploaded_file.read().decode(encoding)
            data = json.loads(content)

            # Tenta as orientações mais comuns
            try:
                df = pd.read_json(StringIO(content), orient=json_orient)
            except:
                # Fallback para json_normalize (bom para JSON aninhado)
                df = pd.json_normalize(data)

        elif file_type == "parquet":
            df = pd.read_parquet(uploaded_file)

        elif file_type == "feather":
            df = pd.read_feather(uploaded_file)

        else:
            st.error("Formato não suportado.")

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        st.info("Tente alterar o separador, encoding ou orientação do JSON na barra lateral.")

if df is not None and not df.empty:
    st.subheader("Pré-visualização dos Dados")
    st.dataframe(df, use_container_width=True)

    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Linhas", f"{len(df):,}")
    col2.metric("Colunas", len(df.columns))
    col3.metric("Valores nulos", f"{df.isnull().sum().sum():,}")
    col4.metric("Tamanho em memória", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    with st.expander("Tipos de dados das colunas"):
        st.write(df.dtypes.astype(str))
    st.divider()


    st.subheader("Converter e Baixar")

    formato_saida = st.selectbox(
        "Escolha o formato de saída:",
        ["CSV", "Excel (.xlsx)", "JSON", "Parquet", "TSV", "HTML", "Markdown", "Feather"]
    )

    # Opções extras de exportação
    col_a, col_b = st.columns(2)

    with col_a:
        incluir_index = st.checkbox("Incluir índice no arquivo", value=False)
    
    with col_b:
        if formato_saida == "JSON":
            orient_export = st.selectbox(
                "Orientação do JSON de saída",
                ["records", "columns", "index", "split", "table", "values"]
            )
        elif formato_saida == "CSV":
            sep_export = st.selectbox("Separador do CSV", [",", ";", "\t", "|"])
        elif formato_saida == "Dict (Python)":
            dict_orient = st.selectbox(
                "Orientação do Dict",
                ["records", "dict", "list", "series", "split", "index"],
                index=0
            )

    # Botões de download
    try:
        if formato_saida == "CSV":
            sep_final = "\t" if sep_export == "\\t" else sep_export
            data = df.to_csv(index=incluir_index, sep=sep_final).encode("utf-8")
            st.download_button(
                "Baixar CSV",
                data=data,
                file_name="dados_convertidos.csv",
                mime="text/csv"
            )
        elif formato_saida == "Dict (Python)":
            dict_orient = st.selectbox(
                "Orientação do Dict",
                ["records", "dict", "list", "series", "split", "index"],
                index=0
            )

        elif formato_saida == "Excel (.xlsx)":
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=incluir_index, sheet_name="Dados")
            st.download_button(
                "Baixar Excel",
                data=buffer.getvalue(),
                file_name="dados_convertidos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        elif formato_saida == "JSON":
            json_str = df.to_json(orient=orient_export, force_ascii=False, indent=2)
            st.download_button(
                "Baixar JSON",
                data=json_str,
                file_name="dados_convertidos.json",
                mime="application/json"
            )

        elif formato_saida == "Parquet":
            buffer = BytesIO()
            df.to_parquet(buffer, index=incluir_index)
            st.download_button(
                "Baixar Parquet",
                data=buffer.getvalue(),
                file_name="dados_convertidos.parquet",
                mime="application/octet-stream"
            )

        elif formato_saida == "TSV":
            data = df.to_csv(index=incluir_index, sep="\t").encode("utf-8")
            st.download_button(
                "Baixar TSV",
                data=data,
                file_name="dados_convertidos.tsv",
                mime="text/tab-separated-values"
            )

        elif formato_saida == "HTML":
            html = df.to_html(index=incluir_index)
            st.download_button(
                "Baixar HTML",
                data=html,
                file_name="dados_convertidos.html",
                mime="text/html"
            )

        elif formato_saida == "Markdown":
            try:
                md = df.to_markdown(index=incluir_index)
                st.download_button(
                    "Baixar Markdown",
                    data=md.encode("utf-8"),
                    file_name="dados_convertidos.md",
                    mime="text/markdown"
                )
            except ImportError:
                st.error("Biblioteca 'tabulate' não encontrada. Rode: pip install tabulate")
            except Exception as e:
                st.error(f"Erro ao gerar Markdown: {e}")

        elif formato_saida == "Feather":
            buffer = BytesIO()
            df.to_feather(buffer)
            st.download_button(
                "Baixar Feather",
                data=buffer.getvalue(),
                file_name="dados_convertidos.feather",
                mime="application/octet-stream"
            )
        elif formato_saida == "Dict (Python)":
            dados_dict = df.to_dict(orient=dict_orient)
            # Transforma em texto formatado para download
            dict_str = json.dumps(dados_dict, ensure_ascii=False, indent=2, default=str)
            st.download_button(
                "Baixar Dict (Python)",
                data=dict_str.encode("utf-8"),
                file_name="dados_convertidos_dict.json",
                mime="application/json"
            )

    except Exception as e:
        st.error(f"Erro ao gerar o arquivo: {e}")

else:
    st.info("Faça o upload de um arquivo na barra lateral para começar.")

# Rodapé
st.sidebar.markdown("---")
st.sidebar.caption("Formatos suportados na entrada: CSV, TSV, Excel, JSON, Parquet, Feather")