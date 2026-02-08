import streamlit as st

st.sidebar.success("Please select below pages")


st.title("🏠 Home Page")
st.write("Welcome to the GCS Analytics")
st.write("This is a web page which helps to provide data cleaning solution, data visualization, feature extraction and feature engineering.  \n This is a work in progress and more features are to be added.")
    





# def about():
#     st.title("ℹ️ About Page")
#     st.write("This is the about page.")

# def contact():
#     st.title("📞 Contact Page")
#     st.write("Reach out to us here.")

# def ws_page():
#     st.title("WeatherSmart")
    
# def bt_page():
#     st.title("Backtracking")
#     #st.write("Need help? You're in the right place.")

# def AS_page():
#     st.title("Antishading")
#     #st.write("Need help? You're in the right place.")

# def ss_page():
#     st.title("Split Cell")
#     #st.write("Need help? You're in the right place.")

# def smartstow_page():
#     st.title("SmartStow")
#     #st.write("Need help? You're in the right place.")

# def MH_page():
#     st.title("Motor Health")
#     #st.write("Need help? You're in the right place.")

# def BH_page():
#     st.title("Battery Health")
#     #st.write("Need help? You're in the right place.")

# def nf_page():
#     st.title("Node Failure")
#     #st.write("Need help? You're in the right place.")

# def mf_page():
#     st.title("Master Failure")
#     #st.write("Need help? You're in the right place.")

# def wsh_page():
#     st.title("Wind Sensor Health")
#     #st.write("Need help? You're in the right place.")

# def cd_page():
#     st.title("Call and Response duration")
#     #st.write("Need help? You're in the right place.")

# def cfr_page():
#     st.title("Component Failure Rate")
#     #st.write("Need help? You're in the right place.")

# def pvana_page():
#     st.title("PVLib Analysis")
#     #st.write("Need help? You're in the right place.")

# def power_page():
#     st.title("Power Generation Analysis")
#     #st.write("Need help? You're in the right place.")

# def pb_page():
#     st.title("PowerBoost")
#     #st.write("Need help? You're in the right place.")

# def IV_page():
#     st.title("IV Curve")
#     #st.write("Need help? You're in the right place.")

# def PR_page():
#     st.title("Performance Ratio Analysis")
#     #st.write("Need help? You're in the right place.")


# def inverter_page():
#     st.title("Inverter Analysis")
#     #st.write("Need help? You're in the right place.")

# def string_page():
#     st.title("String Current")
#     #st.write("Need help? You're in the right place.")

# def help_page():
#     st.title("❓ Help Page")
#     st.write("Need help? You're in the right place.")


# st.markdown("### Choose a page:")
# #col1, col2, col3, col4 , col5,col6,col7,col8,col9,col10,col11,col12,col13,col14,col15,col16,col17,col18,col19,col20,col21,col22,col23 = st.columns(23)
# #with col1:
# if st.button("Home"):
#         st.session_state.page = "Home"
# #with col2:
# if st.button("About"):
#         st.session_state.page = "About"
# #with col3:
# if st.button("Contact"):
#         st.session_state.page = "Contact"
# #with col4:
# if st.button("WeatherSmart"):
#         st.session_state.page = "WeatherSmart"
# #with col5:
# if st.button("Backtracking"):
#         st.session_state.page = "Backtracking"
# #with col6:
# if st.button("Antishading"):
#         st.session_state.page = "Antishading"
# #with col7:
# if st.button("Split Cell"):
#         st.session_state.page = "Split Cell"
# #with col8:
# if st.button("SmartStow"):
#         st.session_state.page = "SmartStow"
# #with col9:
# if st.button("Motor Health"):
#         st.session_state.page = "Motor Health"
# #with col10:
# if st.button("Battery Health"):
#         st.session_state.page = "Battery Health"
# #with col11:
# if st.button("Node Failure"):
#         st.session_state.page = "Node Failure"
# #with col12:
# if st.button("Master Failure"):
#         st.session_state.page = "Master Failure"
# #with col13:
# if st.button("Wind Sensor Health"):
#         st.session_state.page = "Wind Sensor Health"
# #with col14:
# if st.button("Call And Response Duration"):
#         st.session_state.page = "Call And Response Duration"
# #with col15:
# if st.button("Component Failure Rate"):
#         st.session_state.page = "Component Failure Rate"
# #with col16:
# if st.button("PvlibAnalysis"):
#         st.session_state.page = "PvlibAnalysis"

# if st.button("Power Analysis"):
#         st.session_state.page = "Power Analysis"
# #with col18:
# if st.button("IV Analysis"):
#         st.session_state.page = "IV Curve Analysis"
# #with col19:
# if st.button("PowerBoost Analysis"):
#         st.session_state.page = "Powerboost Analysis"
# #with col20:
# if st.button("Performance Ratio Analysis"):
#         st.session_state.page = "Performance Ratio Analysis"
# #with col21:
# if st.button("Inverter Analysis"):
#         st.session_state.page = "Inverter Analysis"
# #with col22:
# if st.button("String Analysis"):
#         st.session_state.page = "String Analysis"
# #with col23:
# if st.button("Help"):
#         st.session_state.page = "Help"

# # Render selected page

# elif st.session_state.page == "About":
#     about()
# elif st.session_state.page == "Contact":
#     contact()
# elif st.session_state.page == "WeatherSmart":
#     ws_page()
# elif st.session_state.page == "Backtracking":
#     bt_page()
# elif st.session_state.page == "Antishading":
#     AS_page()
# elif st.session_state.page ==  "Split Cell":
#     ss_page()
# elif st.session_state.page == "SmartStow":
#     smartstow_page()
# elif st.session_state.page == "Motor Health":
#     MH_page()
# elif st.session_state.page == "Battery Health":
#     BH_page()
# elif st.session_state.page == "Node Failure":
#     nf_page()
# elif st.session_state.page == "Master Failure":
#     mf_page()
# elif st.session_state.page ==  "Wind Sensor Health":
#     wsh_page()
# elif st.session_state.page == "Call And Response Duration":
#     cd_page()
# elif st.session_state.page == "Component Failure Rate":
#     cfr_page()
# elif st.session_state.page == "PvlibAnalysis":
#     pvana_page()
# elif st.session_state.page == "Power Analysis":
#     power_page()
# elif st.session_state.page == "IV Curve Analysis":
#     IV_page()
# elif st.session_state.page == "Powerboost Analysis":
#     pb_page()
# elif st.session_state.page == "Performance Ratio Analysis":
#     PR_page()
# elif st.session_state.page == "Inverter Analysis":
#     inverter_page()
# elif st.session_state.page =="String Analysis":
#     string_page()
# elif st.session_state.page == "Help":
#     help_page()
