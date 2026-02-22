import os
import json
import torch
from dotenv import load_dotenv
from sentence_transformers import CrossEncoder
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from torch.cuda.amp import autocast
from langchain_core.documents import Document

# Load environment variables
load_dotenv()
MINIML_MODEL_PATH = os.getenv("MINIML_MODEL_PATH")  ## all-MiniLM-L6-v2-original
MODEL_RERANK = os.getenv("MODEL_RERANK")  ## bge-reranker-base

# Initialize HuggingFace embeddings
embeddings = HuggingFaceEmbeddings(model_name=MINIML_MODEL_PATH)

# Function to create mock data and load retrievers
def setup_retriever():
    data_path = "data/ehr_mock.json"

    # Check if the file exists, and if it's empty or invalid, recreate it
    if not os.path.exists(data_path) or os.path.getsize(data_path) == 0:
        print(f"File '{data_path}' is missing or empty. Recreating the file...")

        # Mock data to be written to the file
        mock_data = [
            {"type": "Condition", "content": "Patient has Type 2 Diabetes, diagnosed 2020."},
            {"type": "Medication", "content": "Prescribed Metformin 500mg BID."},
            {"type": "Lab", "content": "HbA1c level 7.5% recorded last month."}
        ]
        
        # Write mock data to the file
        os.makedirs("data", exist_ok=True)
        with open(data_path, "w") as f:
            json.dump(mock_data, f, indent=4)
        
        # Verify contents after writing
        with open(data_path, "r") as f:
            print(f"Written data to '{data_path}':\n{f.read()}")  # Ensure data is written correctly

    # Load the data with JSONLoader
    try:
        loader = JSONLoader(
            file_path=data_path,
            jq_schema=".[]", 
            text_content=False, 
            json_lines=False
        )
        docs = loader.load()

        # If the loader didn't return valid documents, raise an error
        if not docs:
            raise ValueError(f"No valid documents were loaded from {data_path}.")

        # Process the loaded documents into a format suitable for embeddings
        text_docs = []
        for doc in docs:
            content = doc.page_content if doc.page_content else str(doc.metadata)
            text_docs.append(Document(page_content=content, metadata=doc.metadata))

        # Split the documents into smaller chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        splits = splitter.split_documents(text_docs)

        # Create the vectorstore from the documents
        vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
        vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        # Create the BM25 retriever
        bm25_retriever = BM25Retriever.from_documents(splits)
        bm25_retriever.k = 5

        # Combine the two retrievers in an ensemble
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[0.5, 0.5]
        )

        return ensemble_retriever, splits

    except Exception as e:
        print(f"Error loading documents: {e}")
        return None, []

# Initialize retriever and documents
retriever, all_docs = setup_retriever()

# Automatically select device (GPU if available, otherwise CPU)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize the reranker model (move it to the selected device)
reranker = CrossEncoder(model_name_or_path=MODEL_RERANK, device=device)

# Function to retrieve and rerank documents based on the query
def retrieve_and_rerank(query: str, top_k: int = 3):
    # Ensure retriever is valid
    if retriever is None:
        return []  # Return empty if retriever failed to initialize

    try:
        # Perform initial retrieval
        initial_docs = retriever.invoke(query)

        if not initial_docs:
            return []  # Return empty if no documents are retrieved

        # Prepare the documents for re-ranking
        doc_pairs = [[query, doc.page_content] for doc in initial_docs]

        # Perform inference with mixed precision (FP16) if using GPU
        with torch.no_grad():
            with autocast():  # Use mixed precision if available
                scores = reranker.predict(doc_pairs)

        # Sort the documents based on reranking scores
        scored_docs = sorted(zip(initial_docs, scores), key=lambda x: x[1], reverse=True)

        # Return top_k ranked documents
        return [doc for doc, score in scored_docs[:top_k]]

    except Exception as e:
        print(f"Error during retrieval or reranking: {e}")
        return []

# Clear GPU memory cache (if running on GPU) after each retrieval
torch.cuda.empty_cache()  # Clears unused GPU memory
