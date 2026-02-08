import streamlit as st
import os
import shutil
from pathlib import Path
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

st.title("📁 Folder Organizer")
st.write("Once downloaded and extracted all the files from different sources, you need to simply pick files and organise them into individual folder. This tool will help you accomplish your goal to do so, without requiring much maual work.")

# Step 1: User inputs base folder path
base_path = st.text_input("Enter the folder path to organize")

if base_path and os.path.isdir(base_path):
    st.success("Valid folder path detected.")

    # Step 2: List files and folders
    all_files = [f for f in Path(base_path).rglob("*") if f.is_file()]
    file_names = [str(f.relative_to(base_path)) for f in all_files]

    selected_files = st.multiselect("Select files to move", file_names)

    # Step 3: Destination folder input
    new_folder_name = st.text_input("Enter name for new folder (inside base path)")

    if st.button("Organize Files"):
        if selected_files and new_folder_name:
            new_folder_path = Path(base_path) / new_folder_name
            new_folder_path.mkdir(exist_ok=True)

            for file in selected_files:
                src = Path(base_path) / file
                dst = new_folder_path / Path(file).name
                shutil.copy2(src, dst)

            st.success(f"✅ Moved {len(selected_files)} files to '{new_folder_name}'")
        else:
            st.warning("Please select files and enter a folder name.")
else:
    if base_path:
        st.error("❌ Invalid folder path. Please check and try again.")