import streamlit as st
import pandas as pd
import numpy as np   # ✅ for safe division
from utils import hide_streamlit_style

hide_streamlit_style()

st.title("Data Normalisation")
st.write("Normalise Power generation data with DC Capacity, GHI AND POA in few clicks.")
@st.cache_data
def load_file(uploaded_file):
    """Read CSV or Excel file with caching."""
    if uploaded_file.name.lower().endswith(".csv"):
        try:
            return pd.read_csv(uploaded_file, encoding="utf-8")
        except UnicodeDecodeError:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding="latin1")
    else:
        uploaded_file.seek(0)
        return pd.read_excel(uploaded_file)

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    df = load_file(uploaded_file)

    st.subheader("Preview of Uploaded File")
    st.dataframe(df.head())

    num_inverters = st.number_input("Enter number of inverters (blocks)", min_value=1, step=1)
    cols_to_normalise = st.multiselect("Select columns to be normalised", df.columns)
    st.warning("⚠️ Choose normalising columns in the SAME order as the columns to be normalised")
    normalising_cols = st.multiselect("Select normalising columns (DC capacity)", df.columns)

    if cols_to_normalise and normalising_cols and len(cols_to_normalise) == num_inverters and len(normalising_cols) == num_inverters:
        normalised_cols = []
        for col_norm, col_base in zip(cols_to_normalise, normalising_cols):
            norm_col_name = f"{col_norm}_norm"
            # ✅ safe division
            df[norm_col_name] = np.where(df[col_base] == 0, 0, df[col_norm] / df[col_base])
            normalised_cols.append(norm_col_name)

        # Step 7: Let user create multiple summed columns
        sum_cols_list = []
        add_more = True
        counter = 1
        while add_more:
            st.subheader(f"Sum Selection {counter}")
            selected_sum_cols = st.multiselect(f"Select columns to sum for group {counter}", normalised_cols, key=f"sum_{counter}")
            if selected_sum_cols:
                sum_col_name = f"sum_group_{counter}"
                df[sum_col_name] = df[selected_sum_cols].sum(axis=1)
                sum_cols_list.append(sum_col_name)

            add_more = st.radio("Do you want to create another sum column?", ["No", "Yes"], key=f"radio_{counter}") == "Yes"
            counter += 1

        # Step 8: GHI selection (average or single)
        use_avg_ghi = st.radio("Do you want to average multiple GHI columns?", ["No", "Yes"])
        if use_avg_ghi == "Yes":
            ghi_cols = st.multiselect("Select GHI columns to average", df.columns, key="ghi_avg")
            if ghi_cols:
                df["average_ghi"] = df[ghi_cols].mean(axis=1)
                ghi_col = "average_ghi"
            else:
                ghi_col = None
        else:
            ghi_col = st.selectbox("Select single GHI column", df.columns, key="ghi_single")

        # Step 9: POA selection (average or single)
        use_avg_poa = st.radio("Do you want to average multiple POA columns?", ["No", "Yes"])
        if use_avg_poa == "Yes":
            poa_cols = st.multiselect("Select POA columns to average", df.columns, key="poa_avg")
            if poa_cols:
                df["average_poa"] = df[poa_cols].mean(axis=1)
                poa_col = "average_poa"
            else:
                poa_col = None
        else:
            poa_col = st.selectbox("Select single POA column", df.columns, key="poa_single")

        # Step 10: Normalise sums by GHI and POA
        if ghi_col and poa_col and sum_cols_list:
            ghi_norm_cols, poa_norm_cols = [], []
            for sum_col in sum_cols_list:
                ghi_norm_name = f"{sum_col}_norm_by_GHI"
                poa_norm_name = f"{sum_col}_norm_by_POA"
                df[ghi_norm_name] = np.where(df[ghi_col] == 0, 0, df[sum_col] / df[ghi_col])
                df[poa_norm_name] = np.where(df[poa_col] == 0, 0, df[sum_col] / df[poa_col])
                ghi_norm_cols.append(ghi_norm_name)
                poa_norm_cols.append(poa_norm_name)

            st.subheader("Preview of Normalised Results")
            st.dataframe(df.head())

            file_name = st.text_input("Enter file name for download:", "normalised_output.csv")
            enhanced_csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Normalised File as CSV",
                data=enhanced_csv,
                file_name=file_name if file_name else "normalised_output.csv",
                mime="text/csv",
            )