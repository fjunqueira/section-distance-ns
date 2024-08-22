import streamlit as st
import jwt
import time
import streamlit.components.v1 as components

def embed_metabase_question():
    METABASE_SITE_URL = "https://chmetabase.us-east-1.prd.cloudhumans.io"
    METABASE_SECRET_KEY = st.secrets["METABASE_SECRET_KEY"]

    payload = {
      "resource": {"question": 129},
      "params": {},
      "exp": round(time.time()) + (60 * 10)
    }
    
    token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")
    iframeUrl = f"{METABASE_SITE_URL}/embed/question/{token}#bordered=true&titled=true&theme=night"

    components.html(
        f"""
        <iframe src="{iframeUrl}" frameborder="0" width="700" height="600" style="overflow:auto;" scrolling="yes" allowtransparency></iframe>
        """,
        height=600
    )
