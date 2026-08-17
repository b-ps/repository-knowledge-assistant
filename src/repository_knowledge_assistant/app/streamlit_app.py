import streamlit as st
from repository_knowledge_assistant.assistant import RAG
from repository_knowledge_assistant.search.retrieve import Retriever
from repository_knowledge_assistant.ingestion.embed import RepositoryEmbedder
from repository_knowledge_assistant.search.elasticsearch import Index
from repository_knowledge_assistant.llm import LLM
from repository_knowledge_assistant.monitoring.feedback import Feedback, FeedbackIndex
from repository_knowledge_assistant.monitoring.interaction import Interaction, InteractionIndex
from datetime import datetime, timezone
import uuid


st.set_page_config(
    page_title="Repository Knowledge Assistant",
    page_icon="📚",
    layout="centered",
)

@st.cache_resource
def set_up():
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

    feedback_index = FeedbackIndex(index_name="sample_project_feedback")
    feedback_index.create_index()
    interaction_index = InteractionIndex(index_name = "sample_project_interactions")

    return RAG(retriever, llm), feedback_index, interaction_index



rag, fb_index, int_index = set_up()


st.title("📚 Repository Knowledge Assistant")
st.caption("Ask questions about your repository.")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

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

            time = datetime.now(timezone.utc)

            int_index.index_interaction(
                Interaction(
                    question = message["question"],
                    answer = message["content"],
                    timestamp = time,
                    session_id = st.session_state.session_id,
                    message_id = message["message_id"],
                    retrieved_documents=message["retrieved_documents"]
                )
            )

            feedback_key = f"feedback_{i}"

            feedback = st.feedback(
                "thumbs",
                key=feedback_key,
            )

            if feedback is not None:
                time = datetime.now(timezone.utc)
                if feedback == 1:
                    st.success(
                        "Thanks for your positive feedback! 👍"
                    )

                elif feedback == 0:
                    st.info(
                        "Thanks for your feedback! 👎"
                    )
                fb_index.index_feedback(
                    Feedback(
                        feedback = feedback,
                        timestamp = time,
                        session_id = st.session_state.session_id,
                        message_id = message["message_id"]
                    )
                )
            


query = st.chat_input("Ask something", submit_mode = "disable")

if query:
    st.session_state.messages.append({
        "role": "user",
        "content": query,
        "message_id": str(uuid.uuid4())
    })

    with st.chat_message("user"):
        st.write(query)
    with st.chat_message("assistant"):
        with st.spinner("Searching repository..."):
            answer, search_docs = rag.answer(query)
        st.write(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "retrieved_documents": [
            {"file": doc["path"], "chunk_id": doc["id"], "score": doc["score"]} 
            for doc in search_docs
        ],
        "question": query,
        "message_id": str(uuid.uuid4())
    })

    st.rerun()

    
