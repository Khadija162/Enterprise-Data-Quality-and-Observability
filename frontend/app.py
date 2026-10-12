import os
import pandas as pd
import requests
import streamlit as st
st.set_page_config(page_title="Data Quality Control Center",layout="wide")
st.title("Enterprise Data Quality & Observability")
st.caption("Open UCI Iris data · Bronze/Silver/Gold · Read-only AI incident analysis")
api=os.getenv("API_URL","http://localhost:8000")
try:
    r=requests.get(api+"/api/quality",timeout=8);r.raise_for_status();payload=r.json()
except requests.RequestException:payload={"report":None,"classes":[]}
report=payload.get("report")
if report:
    a,b,c=st.columns(3)
    a.metric("Source rows",report["raw"])
    b.metric("Validated rows",report["valid"])
    c.metric("Rejected rows",report["rejected"])
    st.write("Quality alerts")
    st.json(report["alerts"])
    if st.button("Investigate with AI"):
        try:
            r=requests.post(api+"/api/ai/investigate",timeout=100);r.raise_for_status()
            st.json(r.json())
        except requests.RequestException as exc:st.error(str(exc))
else:st.info("Run python -m quality.pipeline to create the initial report.")
if payload.get("classes"):
    st.subheader("Gold-layer analytics")
    df=pd.DataFrame(payload["classes"])
    st.dataframe(df,use_container_width=True)
    st.bar_chart(df.set_index("species")["records"])
