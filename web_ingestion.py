
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def ingest_web_page(url: str, collection_name: str = "my_documents"):
    """
    Ingests a web page, extracts text, chunks it, generates embeddings, and stores them in ChromaDB.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract text from common elements (paragraphs, headings, lists)
        text_elements = soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6", "li"])
        full_text = "\n".join([elem.get_text() for elem in text_elements])

        # Chunk text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        chunks = text_splitter.create_documents([full_text])

        # Generate embeddings
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        # Store in ChromaDB
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory="./chroma_db"
        )
        print(f"Successfully ingested {url} into ChromaDB collection {collection_name}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching web page {url}: {e}")
    except Exception as e:
        print(f"Error ingesting web page {url}: {e}")

if __name__ == "__main__":
    # Example usage
    print("Ingesting example web page...")
    ingest_web_page("https://www.prince2.com/usa/prince2-7-key-concepts")
    print("Ingestion complete.")


