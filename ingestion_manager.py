
import os
from typing import Literal

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

from backend.ingestion.pdf_ingestion import ingest_pdf
from backend.ingestion.pptx_ingestion import ingest_pptx
from backend.ingestion.text_ingestion import ingest_text, ingest_docx # Corrected import
from backend.ingestion.csv_ingestion import ingest_csv
from backend.ingestion.web_ingestion import ingest_web_page

class IngestionManager:
    def __init__(self):
        self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectordb = Chroma(persist_directory="./chroma_db", embedding_function=self.embeddings)

    def ingest_document(self, file_path: str, file_type: Literal["pdf", "pptx", "txt", "docx", "csv", "web"]):
        if file_type == "pdf":
            ingest_pdf(file_path, self.vectordb)
        elif file_type == "pptx":
            ingest_pptx(file_path, self.vectordb)
        elif file_type == "txt":
            ingest_text(file_path, self.vectordb) # Corrected function call
        elif file_type == "docx":
            ingest_docx(file_path, self.vectordb)
        elif file_type == "csv":
            ingest_csv(file_path, self.vectordb)
        elif file_type == "web":
            ingest_web_page(file_path, self.vectordb)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        print(f"Successfully ingested {file_path} as {file_type}")

if __name__ == "__main__":
    manager = IngestionManager()

    # Create dummy files for testing
    os.makedirs("data", exist_ok=True)
    with open("data/dummy.txt", "w") as f:
        f.write("This is a dummy text file for testing.")
    with open("data/dummy.csv", "w") as f:
        f.write("col1,col2\nval1,val2\nval3,val4")

    # Test ingestion of dummy files
    manager.ingest_document("data/dummy.txt", "txt")
    manager.ingest_document("data/dummy.csv", "csv")
    # manager.ingest_document("https://www.example.com", "web") # Requires internet access

    print("Ingestion manager test complete.")


