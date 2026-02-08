import streamlit as st
import pandas as pd
import io
from utils import hide_streamlit_style

hide_streamlit_style()

st.title("DC Capacity and Power File Processor (.xlsx)")
st.write("Add DC capacity column")

# Cached function to read Excel files
@st.cache_data
def load_excel(file):
    return pd.read_excel(file)

# Step 1: Upload DC Capacity File
st.header("Step 1: Upload DC Capacity Excel File")
dc_file = st.file_uploader("Upload DC Capacity Excel file", type=["xlsx"])
if dc_file:
    dc_df = load_excel(dc_file)
    st.subheader("Preview of DC Capacity File")
    st.dataframe(dc_df)

    # Step 2: Select Columns
    st.subheader("Select Columns from DC Capacity File")
    inverter_col_dc = st.selectbox("Select the column with inverter names", dc_df.columns)
    capacity_col_dc = st.selectbox("Select the column with DC capacity values", dc_df.columns)

    # Step 3: Upload Power File
    st.header("Step 2: Upload Power Excel File")
    power_file = st.file_uploader("Upload Power Excel file", type=["xlsx"])
    if power_file:
        power_df = load_excel(power_file)
        st.subheader("Preview of Power File")
        st.dataframe(power_df)

        # Step 4: Select Inverter Name Columns in Power File
        st.subheader("Select Columns from Power File")
        inverter_cols_power = st.multiselect("Select columns that contain inverter names", power_df.columns)

        # Step 5: Match and Add DC Capacity Columns
        st.header("Step 3: Process and Merge DC Capacity")
        for _, row in dc_df.iterrows():
            inverter_name = str(row[inverter_col_dc])
            dc_capacity = row[capacity_col_dc]
            for col in inverter_cols_power:
                if inverter_name in col:
                    new_col_name = f"{col}_DC_capacity"
                    power_df[new_col_name] = dc_capacity

        # Step 6: Final Preview
        st.subheader("Final Preview of Modified Power File")
        st.dataframe(power_df)

        # Step 7: Download Option
        st.header("Step 4: Download Modified File")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            power_df.to_excel(writer, index=False, sheet_name='ModifiedPower')
        output.seek(0)
        st.download_button(
            label="Download Modified Power File as Excel",
            data=output,
            file_name="modified_power_file.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )