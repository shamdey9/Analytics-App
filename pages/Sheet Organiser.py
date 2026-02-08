import streamlit as st
import os
import pandas as pd
import time
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

st.title("📁 Excel Sheet Organizer")
st.write("Organise your sheets in a file into seperate Excel files. Help in case more data comes in and you want to merge them into one.")

# Step 1: Choose input method
input_method = st.radio("Choose input method:", ["Upload Excel file", "Enter folder path"])

sheet_dict = {}

if input_method == "Upload Excel file":
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx", "xls"])
    if uploaded_file:
        try:
            xls = pd.ExcelFile(uploaded_file)
            sheet_dict[uploaded_file.name] = xls.sheet_names
            st.write(f"**{uploaded_file.name}** contains sheets: {', '.join(xls.sheet_names)}")

            num_folders = st.number_input("How many folders do you want to create?", min_value=1, step=1)

            folder_sheet_map = {}
            for i in range(num_folders):
                st.write(f"### Folder {i+1}")
                folder_name = st.text_input(f"Enter name for Folder {i+1}", key=f"folder_{i}")
                selected_sheets = st.multiselect(
                    f"Select sheets to include in Folder {i+1}",
                    options=sheet_dict[uploaded_file.name],
                    key=f"sheet_select_{i}"
                )
                folder_sheet_map[folder_name] = selected_sheets

            if st.button("Organize Sheets"):
                base_dir = "organized_sheets"
                os.makedirs(base_dir, exist_ok=True)

                total = sum(len(sheets) for sheets in folder_sheet_map.values())
                progress = st.progress(0)
                count = 0

                for folder, sheets in folder_sheet_map.items():
                    folder_dir = os.path.join(base_dir, folder)
                    os.makedirs(folder_dir, exist_ok=True)

                    with pd.ExcelWriter(os.path.join(folder_dir, uploaded_file.name)) as writer:
                        for sheet in sheets:
                            df = pd.read_excel(uploaded_file, sheet_name=sheet)
                            df.to_excel(writer, sheet_name=sheet, index=False)
                            count += 1
                            progress.progress(count / total)

                st.success("All sheets organized successfully!")

        except Exception as e:
            st.error(f"Error reading uploaded file: {e}")

elif input_method == "Enter folder path":
    folder_path = st.text_input("Enter the path to the folder containing Excel files:")

    if folder_path and os.path.isdir(folder_path):
        excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') or f.endswith('.xls')]

        if excel_files:
            first_file = excel_files[0]
            first_file_path = os.path.join(folder_path, first_file)
            try:
                xls = pd.ExcelFile(first_file_path)
                sheet_dict[first_file] = xls.sheet_names
                st.write(f"**{first_file}** contains sheets: {', '.join(xls.sheet_names)}")

                num_folders = st.number_input("How many folders do you want to create?", min_value=1, step=1)

                folder_sheet_map = {}
                for i in range(num_folders):
                    st.write(f"### Folder {i+1}")
                    folder_name = st.text_input(f"Enter name for Folder {i+1}", key=f"folder_{i}")
                    selected_sheets = st.multiselect(
                        f"Select sheets from '{first_file}' to include in Folder {i+1}",
                        options=sheet_dict[first_file],
                        key=f"sheet_select_{i}"
                    )
                    folder_sheet_map[folder_name] = selected_sheets

                if st.button("Organize Sheets"):
                    output_base = os.path.join(folder_path, "organized_sheets")
                    os.makedirs(output_base, exist_ok=True)

                    total = len(excel_files) * sum(len(sheets) for sheets in folder_sheet_map.values())
                    progress = st.progress(0)
                    count = 0

                    for excel_file in excel_files:
                        file_path = os.path.join(folder_path, excel_file)
                        for folder, sheets in folder_sheet_map.items():
                            folder_dir = os.path.join(output_base, folder)
                            os.makedirs(folder_dir, exist_ok=True)

                            with pd.ExcelWriter(os.path.join(folder_dir, excel_file)) as writer:
                                for sheet in sheets:
                                    try:
                                        df = pd.read_excel(file_path, sheet_name=sheet)
                                        df.to_excel(writer, sheet_name=sheet, index=False)
                                    except Exception as e:
                                        st.error(f"Error reading sheet '{sheet}' from '{excel_file}': {e}")
                                    count += 1
                                    progress.progress(count / total)

                    st.success("All sheets organized successfully!")

            except Exception as e:
                st.error(f"Error reading first file '{first_file}': {e}")
        else:
            st.warning("No Excel files found in the specified folder.")
    elif folder_path:
        st.error("Invalid folder path. Please check and try again.")