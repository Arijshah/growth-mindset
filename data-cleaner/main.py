import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Simple File Cleaner", layout="centered")

st.title("🗃️Simple File Cleaner & Converter")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a file", type=["csv", "xlsx", "json", "tsv", "txt"])

# --- Options ---
remove_duplicates = st.checkbox("Remove duplicate rows", value=True)
handle_missing = st.checkbox("Handle missing values", value=True)

missing_strategy = None
fill_value = None

if handle_missing:
    missing_strategy = st.selectbox(
        "How to handle missing values?",
        ["Drop rows with missing values", "Fill with median", "Fill with zeros", "Fill with custom value"]
    )
    if missing_strategy == "Fill with custom value":
        fill_value = st.text_input("Enter custom fill value", "N/A")

rename_columns = st.checkbox("Rename columns to lowercase and underscores")
drop_column = st.checkbox("Drop specific columns")

# --- Processing ---
if uploaded_file:
    # Load data
    ext = uploaded_file.name.split(".")[-1].lower()
    if ext == "csv":
        df = pd.read_csv(uploaded_file)
    elif ext in ["xlsx", "xls"]:
        df = pd.read_excel(uploaded_file)
    elif ext == "json":
        df = pd.read_json(uploaded_file)
    elif ext == "tsv":
        df = pd.read_csv(uploaded_file, sep="\t")
    elif ext == "txt":
        sep = st.text_input("Enter separator for TXT file:", ",")
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
    else:
        st.error("Unsupported file type.")
        st.stop()

    st.subheader("Original Data")
    st.dataframe(df.head())

    # Clean data
    if remove_duplicates:
        df = df.drop_duplicates()

    if handle_missing:
        if missing_strategy == "Drop rows with missing values":
            df = df.dropna()
        elif missing_strategy == "Fill with median":
            for col in df.select_dtypes(include=np.number):
                df[col] = df[col].fillna(df[col].median())
            for col in df.select_dtypes(exclude=np.number):
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "")
        elif missing_strategy == "Fill with zeros":
            df = df.fillna(0)
        elif missing_strategy == "Fill with custom value":
            df = df.fillna(fill_value)

    if rename_columns:
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    if drop_column:
        columns_to_drop = st.multiselect("Select columns to drop", df.columns)
        df = df.drop(columns=columns_to_drop)

    st.subheader("Cleaned Data")
    st.dataframe(df.head())

    # --- Downloads ---
    st.subheader("Download")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="cleaned_data.csv", mime="text/csv")

    json = df.to_json(orient="records", indent=2).encode('utf-8')
    st.download_button("Download JSON", data=json, file_name="cleaned_data.json", mime="application/json")

    # Excel
    excel_io = BytesIO()
    with pd.ExcelWriter(excel_io, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    excel_io.seek(0)
    st.download_button("Download Excel", data=excel_io, file_name="cleaned_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.info("Please upload a file to begin.")
