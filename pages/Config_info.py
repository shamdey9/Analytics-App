import streamlit as st
import pandas as pd

st.title("Configuration File Generation")
st.write("Tolerance & File Updater")
# Step 1: Ask user inputs
rot_tol = st.number_input("Enter Rotational Tolerance:", format="%.4f")
vert_tol = st.number_input("Enter Vertical Tolerance:", format="%.4f")
row_spacing = st.number_input("Enter Row Spacing:", format="%.4f")

pitch = st.number_input("Enter Pitch:", format="%.4f")
pitch_topo = st.radio("Topo:", ["Yes", "No"])
split_cell = st.radio("Split Cell:", ["Yes", "No"])

# Step 2: Upload Excel file
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.write("Original File Preview:")
    st.dataframe(df.head())

    # Step 3: Add new columns with user values
    df["Rotational_Tolerance"] = rot_tol
    df["Vertical_Tolerance"] = vert_tol
    df["Row_Spacing"] = row_spacing
    df["Pitch"] = pitch
    df["Topo"] = pitch_topo
    df["Split_Cell"] = split_cell

    st.write("Updated File Preview:")
    st.dataframe(df.head())

    # Step 4: Allow user to download as CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download updated file as CSV",
        data=csv,
        file_name="updated_file.csv",
        mime="text/csv",
    )