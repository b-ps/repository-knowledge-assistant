from .search.retrieve import Retriever
from .llm import LLM


PROMPT_TEMPLATE = """
REPOSITORY CONTEXT: 
{context}

QUESTION: {question}
"""
INSTRUCTIONS = """
You are a helpful assistant for understanding and navigating software repositories. Your task is to answer the user's question based on the provided repository context. 

Rules:
- Use the repository context as the primary source of truth.
- Do not invent information that is not supported by the context.
- If the context does not contain enough information to answer the question, respond with "I don't know".
- When referring to code, mention the relevant file path when available.
- If the question asks about how something works, explain the relevant code and how the pieces are connected.
"""


class RAG:

    def __init__(self, retriever: Retriever, llm: LLM, instructions = INSTRUCTIONS, prompt_template = PROMPT_TEMPLATE):
        self.retriever = retriever
        self.llm = llm
        self.instructions = instructions
        self.prompt_template = prompt_template

    def answer(self, query, search_method = 'hybrid'):
        search_results = self.retriever.retrieve(query, search_method)
        prompt = self._build_prompt(query, search_results)
        answer = self.llm.generate(self.instructions, prompt)
        return answer, search_results

    def _build_context(self, results):
        lines = []

        for doc in results:
            lines.append(f"""<document path="{doc['path']}">""")
            lines.append(doc['text'])
            lines.append("</document>")
            lines.append("")

        return "\n".join(lines).strip()

    def _build_prompt(self, query, results):
        context = self._build_context(results)

        return self.prompt_template.format(question = query, context = context)