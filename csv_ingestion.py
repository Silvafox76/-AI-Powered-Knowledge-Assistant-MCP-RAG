
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def ingest_csv(file_path: str, collection_name: str = "my_documents"):
    """
    Ingests a CSV file, converts it to text, chunks it, generates embeddings, and stores them in ChromaDB.
    """
    try:
        df = pd.read_csv(file_path)
        # Convert DataFrame to a string representation for embedding
        text = df.to_string()

        # Chunk text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        chunks = text_splitter.create_documents([text])

        # Generate embeddings
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # Store in ChromaDB
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory="./chroma_db"
        )
        print(f"Successfully ingested {file_path} into ChromaDB collection {collection_name}")

    except Exception as e:
        print(f"Error ingesting CSV {file_path}: {e}")

if __name__ == "__main__":
    import os
    os.makedirs("../data", exist_ok=True)

    # Example for CSV
    data = {
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [30, 24, 35],
        'City': ['New York', 'Los Angeles', 'Chicago']
    }
    df = pd.DataFrame(data)
    df.to_csv("../data/dummy.csv", index=False)
    ingest_csv("../data/dummy.csv")


