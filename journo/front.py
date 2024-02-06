import streamlit as st
from journo.modules import *
import pandas as pd

def show_database():
  if 'database' not in st.session_state:
    st.session_state.sheet = load_sheet()
    try:
      st.session_state.database = st.session_state.sheet.read(worksheet=st.session_state.email)
    except:
      nuevo_df = pd.DataFrame({'Transcripción': [None]*5, 'Cargo': [None]*5, 'Nombre': [None]*5, 'Tema': [None]*5, 'Donde': [None]*5, 'Cuando': [None]*5, 'Transcripción filtrada': [None]*5, 'Anotaciones': [None]*5, 'Noticia': [None]*5, 'Sesion': [None]*5}, index=range(5))
      st.session_state.sheet.create(worksheet=st.session_state.email,data=nuevo_df)
      st.session_state.database = st.session_state.sheet.read(worksheet=st.session_state.email)
