import streamlit as st
import pandas as pd
from io import BytesIO
from utils import hide_streamlit_style

hide_streamlit_style()
hide_streamlit_style = """
    <style>
    /* Hide GitHub and Fork icons in Streamlit Cloud header */
    [data-testid="stToolbar"] {
        display: none !important;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("🔄 Unpivot Excel Columns Safely")

# Step 1: Upload Excel file
uploaded_file = st.file_uploader("Drop your Excel file here", type=["xlsx"])
st.write("Multiple Inverter values in a single column? You want to seperate them into individual column? Use this page for it.")

@st.cache_data
def load_excel(file):
    return pd.read_excel(file)

def convert_df_to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Unpivoted')
    output.seek(0)
    return output

if uploaded_file:
    df = load_excel(uploaded_file)
    st.subheader("📄 Preview of Uploaded File")
    st.dataframe(df)

    # Step 2: Select column to become new headers
    col_to_unpivot = st.selectbox("🧩 Select the column whose values will become new columns", df.columns)

    # Step 3: Select column that contains values
    value_column = st.selectbox("📦 Select the column that contains values for each new column", df.columns)

    if col_to_unpivot and value_column:
        unique_count = df[col_to_unpivot].nunique()
        st.write(f"🔢 Unique values in '{col_to_unpivot}': {unique_count}")

        if unique_count > 1000:
            st.warning("⚠️ Too many unique values to pivot safely. Consider filtering or aggregating your data.")
        else:
            # All other columns will be used as index
            index_cols = [col for col in df.columns if col not in [col_to_unpivot, value_column]]
            df_unpivoted = df.pivot_table(
                index=index_cols,
                columns=col_to_unpivot,
                values=value_column,
                aggfunc='first'  # safer than pivot
            ).reset_index()

            st.subheader("🔍 Preview of Unpivoted Data")
            st.dataframe(df_unpivoted)

            # Step 4: Download button
            excel_data = convert_df_to_excel(df_unpivoted)
            st.download_button(
                label="📥 Download Unpivoted Excel File",
                data=excel_data,
                file_name="unpivoted_output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )