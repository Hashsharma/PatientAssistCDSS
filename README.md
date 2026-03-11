# 🏥 Local Medical Clinical Decision Support System (CDSS)

> **⚠️ CRITICAL DISCLAIMER**  
> **This software is for EDUCATIONAL and RESEARCH purposes ONLY.**  
> **DO NOT** use this system for actual patient care, diagnosis, or treatment decisions.  
> **DO NOT** input real Protected Health Information (PHI) unless you are in a compliant, air-gapped environment.  
> Local LLMs can hallucinate. Always verify medical information with authoritative sources.

---

## 📖 Overview

This project is a privacy-focused **Clinical Decision Support System (CDSS)** prototype. It leverages **Retrieval-Augmented Generation (RAG)** to assist healthcare providers by querying simulated Electronic Health Records (EHR) using local Large Language Models (LLMs).

Unlike cloud-based solutions, this system runs **entirely locally**, ensuring patient data privacy and reducing latency dependencies. It prioritizes **accuracy, auditability, and safety** over raw speed, implementing strict guardrails and comprehensive logging.

## 🚀 Key Features

*   **🔒 Privacy-First Architecture:** Runs entirely offline using local LLMs (Ollama) and local vector stores. No data leaves the machine.
*   **🛡️ Safety Guardrails:** Input filtering for PHI (PII) detection and output validation for medical disclaimers.
*   **📝 Immutable Audit Logging:** Every query, response, and source citation is logged to a JSONL file for compliance and traceability.
*   **🔍 Hybrid Retrieval:** Combines **Keyword Search (BM25)** and **Semantic Search (Vector Embeddings)** for higher accuracy.
*   **🎯 Re-Ranking:** Uses a Cross-Encoder model to re-rank retrieved documents for better context relevance.
*   **📚 Citation Enforcement:** The LLM is prompted to cite specific EHR sources for every claim made.
*   **🖥️ Provider UI:** A clean Streamlit interface for clinicians to interact with the system.

## 🏗️ Architecture

```text
[ Provider UI (Streamlit) ] 
          |
          v
[ API Orchestrator (FastAPI) ] <===> [ Audit Logger ]
          |
          +===> [ Guardrail Service (PII/Safety) ]
          |
          +===> [ Retrieval Engine ]
                  |
                  +===> [ Vector DB (Chroma) ]
                  +===> [ Keyword Index (BM25) ]
                  +===> [ Re-Ranker (Cross-Encoder) ]
                  |
                  v
          [ Generation Engine (Ollama/Llama3) ]
```

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Language** | Python 3.9+ |
| **LLM Runtime** | [Ollama](https://ollama.com/) (Llama 3) |
| **Orchestration** | [LangChain](https://www.langchain.com/) |
| **API Framework** | [FastAPI](https://fastapi.tiangolo.com/) |
| **Frontend** | [Streamlit](https://streamlit.io/) |
| **Vector Store** | [ChromaDB](https://www.trychroma.com/) |
| **Embeddings** | HuggingFace (`all-MiniLM-L6-v2`) |
| **Re-Ranker** | HuggingFace (`bge-reranker-base`) |
| **Search** | `rank-bm25` |

## 📦 Prerequisites

1.  **Python 3.9 or higher**
2.  **Ollama** installed and running ([Download](https://ollama.com/))
3.  **Git**

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Hashsharma/PatientAssistCDSS.git
cd PatientAssistCDSS
```

### 2. Setup Python Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Setup Local LLM
Pull the required model via Ollama:
```bash
ollama pull llama3
```

### 4. Initialize Data
The system will automatically generate mock EHR data on the first run. However, you can manually ensure the directory exists:
```bash
mkdir -p data
```

## 🏃 Running the System

You need to run two services: the **Backend API** and the **Frontend UI**.

### Terminal 1: Start Backend
```bash
python -m app.main
```
*Server will start on `http://localhost:8000`*

### Terminal 2: Start UI
```bash
streamlit run ui.py
```
*UI will open on `http://localhost:8501`*

## 💡 Usage Example

1.  Open the Streamlit UI in your browser.
2.  Enter a **Patient ID** (e.g., `P-12345`).
3.  Enter a **Clinical Query**:
    > *"What is the patient's current HbA1c level and medication status?"*
4.  Click **Analyze EHR**.
5.  Review the **Recommendation** and check the **Sources** tab to verify citations.

## 📂 Project Structure

```text
.
├── app/
│   ├── main.py            # FastAPI Entry Point
│   ├── audit.py           # Audit Logging Service
│   ├── guardrails.py      # Safety & PII Filters
│   ├── retrieval.py       # Hybrid Search & Re-Ranking
│   └── generation.py      # LLM Chain & Prompting
├── data/
│   ├── ehr_mock.json      # Simulated Patient Records
│   └── audit_logs.jsonl   # Immutable Audit Trail
├── ui.py                  # Streamlit Frontend
├── requirements.txt       # Python Dependencies
└── README.md
```

## 🔒 Security & Privacy Notes

*   **No Authentication:** This prototype excludes authentication layers for simplicity. **Do not expose this API to the public internet.**
*   **PHI Detection:** The guardrail service uses regex patterns to detect potential SSNs or IDs. This is not foolproof; it does not rely on it for HIPAA compliance.
*   **Data Residency:** All data (vectors, logs, models) resides locally on your machine.
*   **Audit Trail:** All interactions are appended to `data/audit_logs.jsonl`. Do not delete this file if compliance tracking is required.

## 🚧 Limitations & Future Roadmap

| Current Limitation | Future Improvement |
| :--- | :--- |
| Mock EHR Data | Integrate with real FHIR Server (HAPI FHIR) |
| No User Auth | Implement OAuth2/OIDC (Keycloak) |
| Basic PII Check | Integrate dedicated Medical NER (e.g., Microsoft Presidio) |
| Single Local LLM | Support for model switching & fine-tuned medical models |
| Basic Citation Check | Automated fact-checking against retrieved context |

---

**Built for Research & Education.**  
*Contributions regarding safety, accuracy, and privacy enhancements are welcome.*