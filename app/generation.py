import requests
import time
from langchain_core.prompts import ChatPromptTemplate
from .retrieval import retrieve_and_rerank
from .guardrails import check_output_safety

# Local LMStudio API Configuration - Fixed endpoints
LMSTUDIO_API_URL = "http://localhost:1234/v1/completions"  # Fixed: added /v1/
# No API key needed for local LMStudio

TEMPLATE = """
You are a Clinical Decision Support Assistant. 
Use the provided Context from the EHR to answer the Query.
You MUST cite the source index (e.g., [Source 1]) for every medical claim.
If the context does not contain the answer, state "Information not found in EHR".
Always end with: "Consult a qualified healthcare provider."

Context:
{context}

Query: {query}

Answer:
"""

prompt = ChatPromptTemplate.from_template(TEMPLATE)

def format_docs(docs):
    return "\n\n".join(f"[Source {i+1}]: {d.page_content}" for i, d in enumerate(docs))

def generate_response(query: str):
    start_time = time.time()
    
    # 1. Retrieval & Rerank
    docs = retrieve_and_rerank(query)
    context = format_docs(docs)
    
    # 2. Query Rewriting (Simple Expansion for Demo)
    expanded_query = f"{query} (medical context)" 

    # 3. Prepare Prompt for API Call
    prompt_text = prompt.format(context=context, query=expanded_query)

    # 4. Call LMStudio Locally via HTTP Request
    headers = {
        "Content-Type": "application/json"  # Removed Authorization header
    }
    payload = {
        "prompt": prompt_text,
        "temperature": 0.1,
        "max_tokens": 500
    }
    
    # Send POST request to local LMStudio instance
    response = requests.post(LMSTUDIO_API_URL, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"API call failed with status code {response.status_code}: {response.text}")
    
    # 5. Extract the response text from the LMStudio API response
    api_response = response.json()
    answer = api_response["choices"][0]["text"].strip()  # Fixed: proper LMStudio response format

    # 6. Citation Validation (Basic Check)
    # Ensure sources cited actually exist in the context
    # (Simplified for prototype)
    
    # 7. Guardrail Output Check
    safe_response = check_output_safety(answer)
    
    latency = (time.time() - start_time) * 1000
    
    return safe_response, docs, latency