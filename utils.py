import streamlit as st

def hide_streamlit_style():
    hide_style = """
        <style>
        /* Hide the GitHub and Fork icons in the Streamlit Cloud header */
        .stAppHeader .stToolbar > div:nth-child(2) {
            display: none !important;
        }
        </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)