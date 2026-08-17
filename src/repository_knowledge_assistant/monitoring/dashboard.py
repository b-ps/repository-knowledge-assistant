import streamlit as st
from repository_knowledge_assistant.monitoring.feedback import FeedbackIndex

@st.cache_resource
def set_up():
    fb_index = FeedbackIndex(index_name = "sample_project_feedback")
    return fb_index

fb_index = set_up()

st.title("Repository Knowledge Assistant Dashboard")

feedback = fb_index.get_all_documents()

