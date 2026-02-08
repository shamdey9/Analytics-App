import streamlit as st
import pandas as pd
import os
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

st.title("📊 Excel Date Extractor and Cell Replacer")
st.write("Get Date column added to your excel file")

@st.cache_data
def load_excel_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.endswith(('.xlsx', '.xls'))]

@st.cache_data
def read_excel_file(file_path):
    return pd.read_excel(file_path)

# Step 1: Get source folder path
source_folder = st.text_input("Enter the path to the folder containing Excel files")

if source_folder and os.path.isdir(source_folder):
    excel_files = load_excel_files(source_folder)

    if excel_files:
        # Step 2: Preview the first file
        first_file_path = os.path.join(source_folder, excel_files[0])
        df_preview = read_excel_file(first_file_path)
        st.subheader(f"Preview of: {excel_files[0]}")
        st.dataframe(df_preview)

        # Step 3: Select cell to extract date
        date_row = st.number_input("Enter row index to extract date", min_value=0, max_value=len(df_preview)-1, value=0)
        date_col = st.selectbox("Select column to extract date", df_preview.columns)

        # Step 4: Row index to insert new column
        #insert_row_index = st.number_input("Enter row index to insert new column", min_value=0, max_value=len(df_preview), value=0)
        new_column_name = f"unmade_0"

        # Step 5: Select row in new column to replace
        replace_row = st.number_input("Enter row index in new column to replace", min_value=0, max_value=len(df_preview)-1, value=0)

        # Step 6: Apply changes to preview
        date_value = df_preview.loc[date_row, date_col]
        df_preview.insert(loc=0, column=new_column_name, value=date_value)

        # Step 7: Replacement value
        original_value = df_preview.loc[replace_row, new_column_name]
        replacement_value = st.text_input(f"Enter a value to replace '{original_value}' in row {replace_row} of new column (leave blank to keep original)")
        df_preview.loc[replace_row, new_column_name] = replacement_value if replacement_value != "" else original_value

        st.subheader("Preview with new column and replaced value:")
        st.dataframe(df_preview)

        # Step 8: Destination folder
        destination_folder = st.text_input("Enter the destination folder path to save updated Excel files")

        # Step 9: Apply and save
        if st.button("Apply and Save"):
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)

            progress = st.progress(0)
            for i, file_name in enumerate(excel_files):
                file_path = os.path.join(source_folder, file_name)
                df = pd.read_excel(file_path)
                df.insert(loc=0, column=new_column_name, value=df.loc[date_row, date_col])
                df.loc[replace_row, new_column_name] = replacement_value if replacement_value != "" else df.loc[replace_row, new_column_name]
                save_path = os.path.join(destination_folder, file_name)
                df.to_excel(save_path, index=False)
                progress.progress((i + 1) / len(excel_files))

            st.success("✅ All files processed and saved successfully!")
    else:
        st.warning("No Excel files found in the specified folder.")
elif source_folder:
    st.error("The specified folder path does not exist.")