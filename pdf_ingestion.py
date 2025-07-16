
import pypdf
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def ingest_pdf(file_path: str, collection_name: str = "my_documents"):
    """
    Ingests a PDF file, extracts text, chunks it, generates embeddings, and stores them in ChromaDB.
    """
    try:
        # Load PDF
        loader = pypdf.PdfReader(file_path)
        text = ""
        for page in loader.pages:
            text += page.extract_text()

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
        print(f"Error ingesting PDF {file_path}: {e}")

if __name__ == "__main__":
    import os
    os.makedirs("../data", exist_ok=True)
    print("To test, create a PDF file in the ../data directory and uncomment the ingest_pdf line.")


