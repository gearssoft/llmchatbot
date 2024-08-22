import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to Streamlit! 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    폴더 구성은 아래와 같이 한다.
    - home.py
    - pages/  
        - about.py
        - contact.py
        - gallery.py
        - plot.py
        
    pages 폴더에는 각각의 페이지를 구성하는 파일들을 넣는다.
    
    
"""
)