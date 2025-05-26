import os
from typing import List

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
embedding_function = OpenAIEmbeddings()
vector_store = Chroma(persist_directory="../chroma_db", embedding_function=embedding_function)

# Document Loading and Splitting
def load_and_split_document(file_path: str) -> List[Document]:
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith('.html'):
        loader = UnstructuredHTMLLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")

    documents = loader.load()
    return text_splitter.split_documents(documents)

# Indexing Documents
def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    """This function takes a file path and a file ID, loads and splits the document,
    adds metadata (file ID) to each split, and then adds these document chunks to our
    Chroma vector store. The metadata allows us to link vector store entries back to
    our database records."""
    try:
        splits = load_and_split_document(file_path)

        # Add metadata to each split
        for split in splits:
            split.metadata['file_id'] = file_id

        vector_store.add_documents(splits)
        return True
    except Exception as e:
        print(f"Error indexing document: {e}")
        return False

# Deleting Documents
def delete_doc_from_chroma(file_id: int):
    """This function deletes all document chunks associated
    with a given file ID from the Chroma vector store. """
    try:
        docs = vector_store.get(where = {"file_id": file_id})
        print(f"Found {len(docs['ids'])} document chunks for file_id: {file_id}")

        vector_store._collection.delete(where={"file_id": file_id})
        print(f"Deleted all documents with file_id {file_id}")

        return True
    except Exception as e:
        print(f"Error deleting document with file_id: {file_id} from ChromaDB: {str(e)}")
        return False
