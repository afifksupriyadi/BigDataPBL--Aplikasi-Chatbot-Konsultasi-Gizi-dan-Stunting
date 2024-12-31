from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from retriever_utils import load_vectorstore, create_standard_retriever, create_compression_retriever

# Muat vectorstore
vectorstore = load_vectorstore()

# Inisialisasi retriever
retriever = create_standard_retriever(vectorstore)

# Inisialisasi Embeddings
embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")

# Inisialisasi compression retriever
compression_retriever = create_compression_retriever(retriever, embedding_model)

# Prompt untuk standalone question
contextualize_q_system_prompt = (
    "Diberikan riwayat percakapan (chat history) dan pertanyaan. "
    "Pertanyaan mungkin merujuk pada konteks di dalam chat history. "
    "Susun ulang pertanyaan menjadi pertanyaan yang utuh tanpa referensi ke chat history. "
    "Jangan memberikan jawaban, hanya reformulasi pertanyaan."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

def get_history_aware_retriever(model="gpt-4o-mini"):
    llm = ChatOpenAI(model=model, temperature=0)
    return create_history_aware_retriever(llm, compression_retriever, contextualize_q_prompt)


# Prompt untuk menjawab pertanyaan berdasarkan dokumen relevan
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "Anda adalah AI asisten yang membantu menjawab berdasarkan dokumen berikut."),
    ("system", "Konteks: {context}"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])


def get_question_answer_chain(model="gpt-4o-mini"):
    llm = ChatOpenAI(model=model)
    return create_stuff_documents_chain(llm, qa_prompt)

def get_rag_chain_full(model="gpt-4o-mini"):
    llm = ChatOpenAI(model=model)
    history_aware_retriever = get_history_aware_retriever(model)
    question_answer_chain = get_question_answer_chain(model)
    return create_retrieval_chain(history_aware_retriever, question_answer_chain)
