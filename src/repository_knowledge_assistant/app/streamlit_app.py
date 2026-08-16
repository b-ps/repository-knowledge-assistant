import streamlit as st
from repository_knowledge_assistant.assistant import RAG
from repository_knowledge_assistant.search.retrieve import Retriever
from repository_knowledge_assistant.ingestion.embed import RepositoryEmbedder
from repository_knowledge_assistant.search.elasticsearch import Index
from repository_knowledge_assistant.llm import LLM

st.set_page_config(
    page_title="Repository Knowledge Assistant",
    page_icon="📚",
    layout="centered",
)

@st.cache_resource
def set_up_rag():
    embedder = RepositoryEmbedder(
        model_name="all-MiniLM-L6-v2"
    )

    index = Index(
        index_name="sample_project"
    )

    retriever = Retriever(
        index,
        embedder
    )

    llm = LLM()

    return RAG(retriever, llm)

rag = set_up_rag()

st.title("📚 Repository Knowledge Assistant")
st.caption("Ask questions about your repository.")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! Ask me anything about the repository."
        }
    ]

for i, message in enumerate(st.session_state.messages):

    with st.chat_message(message["role"]):

        st.write(message["content"])

        if message["role"] == "assistant" and i > 0:

            feedback_key = f"feedback_{i}"

            feedback = st.feedback(
                "thumbs",
                key=feedback_key,
            )

            if feedback is not None:
                if feedback == 1:
                    st.success(
                        "Thanks for your positive feedback! 👍"
                    )

                elif feedback == 0:
                    st.info(
                        "Thanks for your feedback! 👎"
                    )


query = st.chat_input("Ask something", submit_mode = "disable")

if query:
    st.session_state.messages.append({
        "role": "user",
        "content": query,
    })

    with st.chat_message("user"):
        st.write(query)
    with st.chat_message("assistant"):
        with st.spinner("Searching repository..."):
            answer = rag.answer(query)
        st.write(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
    })

    st.rerun()

    
