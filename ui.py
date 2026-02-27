import streamlit as st
import requests
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="MediAssist CDSS", layout="wide")

st.title("🏥 Clinical Decision Support System")
st.markdown("**⚠️ Research Prototype. Do not use for real patient care.**")

# Get backend URL from environment variable with fallback
BACKEND_URL = os.getenv("CDSS_BACKEND_URL", "")
print("backend url", BACKEND_URL)

with st.sidebar:
    st.header("Patient Context")
    patient_id = st.text_input("Patient ID", value="P-123456")
    st.info("System running locally. No data leaves this machine.")
    st.caption(f"Connected to: {BACKEND_URL}")

query = st.text_area("Clinical Query", placeholder="Type your clinical query (diagnosis, treatment, guidelines, drug dosing, etc.)")

if st.button("Analyze EHR"):
    if not query:
        st.warning("Please enter a query.")
    else:
        with st.spinner("Querying Local LLM & EHR..."):
            try:
                # Call Local Backend with environment variable
                response = requests.post(
                    f"{BACKEND_URL}/clinical/query",
                    json={"patient_id": patient_id, "query": query},
                    timeout=30  # Add timeout for better error handling
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
                    error_detail = response.json().get('detail', 'Unknown error')
                    st.error(f"Error: {error_detail}")
            except requests.exceptions.ConnectionError:
                st.error(f"Failed to connect to backend at {BACKEND_URL}. Make sure the server is running.")
            except requests.exceptions.Timeout:
                st.error("Request timed out. The backend might be overloaded.")
            except Exception as e:
                st.error(f"Connection Failed: {e}")