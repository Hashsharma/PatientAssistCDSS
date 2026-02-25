import streamlit as st
import requests

st.set_page_config(page_title="MediAssist CDSS", layout="wide")

st.title("🏥 Clinical Decision Support System")
st.markdown("**⚠️ Research Prototype. Do not use for real patient care.**")

with st.sidebar:
    st.header("Patient Context")
    patient_id = st.text_input("Patient ID", value="P-12345")
    st.info("System running locally. No data leaves this machine.")

query = st.text_area("Clinical Query", placeholder="e.g., What is the current HbA1c level and medication status?")

if st.button("Analyze EHR"):
    if not query:
        st.warning("Please enter a query.")
    else:
        with st.spinner("Querying Local LLM & EHR..."):
            try:
                # Call Local Backend
                response = requests.post(
                    "http://localhost:8000/clinical/query",
                    json={"patient_id": patient_id, "query": query}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Analysis Complete")
                    
                    st.subheader("Recommendation")
                    st.write(data['answer'])
                    
                    with st.expander("View Audit & Sources"):
                        st.json(data['sources'])
                        st.caption(f"Latency: {data['latency_ms']:.2f}ms")
                else:
                    st.error(f"Error: {response.json().get('detail')}")
            except Exception as e:
                st.error(f"Connection Failed: {e}")