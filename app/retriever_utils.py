import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma


from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
    EmbeddingsFilter,
)
from langchain_community.document_transformers import EmbeddingsRedundantFilter,LongContextReorder
from langchain.retrievers import ContextualCompressionRetriever
from langchain.text_splitter import CharacterTextSplitter
from typing import List
from langchain_core.documents import Document

# Direktori untuk vectorstore
VECTORSTORE_DIR = os.path.join(os.path.dirname(__file__), "../chroma_db")


def load_documents(doc_dir: str) -> List[Document]:
    """Memuat dokumen PDF dari direktori yang ditentukan."""
    all_documents = []
    for file_name in os.listdir(doc_dir):
        file_path = os.path.join(doc_dir, file_name)
        if file_name.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            for idx, doc in enumerate(documents):
                doc.metadata["source"] = file_name
                doc.metadata["page"] = idx + 1
            all_documents.extend(documents)
    return all_documents

def split_documents(documents: List[Document], chunk_size=1600, chunk_overlap=200) -> List[Document]:
    """Memecah dokumen menjadi chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return text_splitter.split_documents(documents)

# Inisialisasi embedding
embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

def create_vectorstore(documents: List[Document], persist_directory=VECTORSTORE_DIR) -> Chroma:
    """
    Membuat vectorstore.
    """
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embedding_model,
        persist_directory=persist_directory
    )
    vectorstore.persist()
    return vectorstore

def load_vectorstore() -> Chroma:
    """
    Memuat vectorstore yang sudah ada dari disk.
    Jika vectorstore tidak ditemukan, berikan informasi kepada pengguna.
    """
    if not os.path.exists(VECTORSTORE_DIR):
        raise FileNotFoundError(f"Vectorstore tidak ditemukan di {VECTORSTORE_DIR}. Harap buat vectorstore terlebih dahulu.")
    return Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embedding_model
    )

def create_standard_retriever(vectorstore: Chroma, k=20):
    """Membuat retriever berbasis similarity search."""
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": k})

def create_compression_retriever(retriever, embedding_model):
    """Membuat Contextual Compression Retriever."""
    # Splitting dokumen menjadi chunk kecil
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    
    # Menghapus chunk yang redundant
    redundant_filter = EmbeddingsRedundantFilter(embeddings=embedding_model)
    
    # Memilih chunk yang sangat relevan
    relevant_filter = EmbeddingsFilter(
        embeddings=embedding_model,
        similarity_threshold=0.75,  # Ambang batas relevansi
        k=16  # Jumlah maksimal chunk relevan
    )
    
    # Mengurutkan ulang dokumen berdasarkan relevansi
    reordering = LongContextReorder(embeddings=embedding_model)
    
    # Membuat pipeline compressor
    pipeline_compressor = DocumentCompressorPipeline(
        transformers=[splitter, redundant_filter, relevant_filter, reordering]
    )
    
    # Membuat Contextual Compression Retriever
    return ContextualCompressionRetriever(
        base_compressor=pipeline_compressor,
        base_retriever=retriever
    )
