import streamlit as st
import pandas as pd

st.title("Uniform Nomenclature")
st.write("Data from various sources although containing same entity might have various name. To identify all of the different kinds here you unify all possible names to be used to make nomenclature unifrom across all different files.")

# Step 1: Ask user for number of inverters
num_inverters = st.number_input("Enter number of inverters:", min_value=1, step=1)

if num_inverters:
    # Step 1a: Ask if sheets have columns with different inverters
    add_column_name = st.radio(
        "Do sheets have columns containing different inverters?",
        ("No", "Yes")
    )

    # Step 2: Create column names
    columns = ["Sheet Name"] + [f"Inverter_{i+1}" for i in range(num_inverters)]
    if add_column_name == "Yes":
        columns.insert(1, "Column Name")  # add after Sheet Name

    # Step 3: Create empty dataframe
    df = pd.DataFrame(columns=columns)

    st.write("Enter values in the table below:")
    st.warning("⚠️ First row Sheet Name should be User's choice")

    # Step 4: Editable table
    edited_df = st.data_editor(df, num_rows="dynamic")  # allows adding rows

    # Step 5: Save to Excel with validation
    if st.button("Save to Excel"):
        # Check if any Sheet Name is missing
        if edited_df["Sheet Name"].isnull().any() or (edited_df["Sheet Name"] == "").any():
            st.warning("⚠️ Please fill in all 'Sheet Name' values before saving.")
        else:
            file_name = "inverter_data.xlsx"
            edited_df.to_excel(file_name, index=False)
            st.success(f"Data saved to {file_name}")
            st.download_button(
                label="Download Excel file",
                data=edited_df.to_excel(index=False, engine="openpyxl"),
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )