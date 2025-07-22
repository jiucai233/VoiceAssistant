import os
from typing import List
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph
from langgraph.graph import END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool


class LLMRAGModule:
    def __init__(self, model_name: str = "gpt-4o-mini", vector_db_path: str = "./index/faiss_ko_sbert"):
        """
        Initialize LLM-RAG module
        """
        load_dotenv(dotenv_path=".env")

        self.llm = init_chat_model(model_name, model_provider="openai", temperature=0.1, max_tokens=128)

        self.embeddings = HuggingFaceEmbeddings(
            model_name="jhgan/ko-sroberta-nli",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        self.vector_db_path = vector_db_path
        self.vector_store = FAISS.load_local(
            vector_db_path,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )

        @tool(response_format="content_and_artifact")
        def retrieve(query: str):
            """Retrieve relevant documents from vector store using similarity search."""
            retrieved_docs = self.vector_store.similarity_search(query, k=2)
            serialized = "\n\n".join(
                (f"Source: {doc.metadata}\nContent: {doc.page_content}")
                for doc in retrieved_docs
            )
            return serialized, retrieved_docs

        self.retrieve_tool = retrieve
        self.memory = MemorySaver()
        self.graph = self.build_graph()

    def build_graph(self):
        def query_or_respond(state: MessagesState):
            llm_with_tools = self.llm.bind_tools([self.retrieve_tool])
            response = llm_with_tools.invoke(state["messages"])
            return {"messages": [response]}

        tools = ToolNode([self.retrieve_tool])

        def generate(state: MessagesState):
            recent_tool_messages = []
            for message in reversed(state["messages"]):
                if message.type == "tool":
                    recent_tool_messages.append(message)
                else:
                    break
            tool_messages = recent_tool_messages[::-1]

            docs_content = "\n\n".join(doc.content for doc in tool_messages)
            system_message_content = (
                "You are an assistant for question-answering tasks. "
                "Use the following pieces of retrieved context to answer "
                "the question. If you don't know the answer, say that you "
                "don't know. Use three sentences maximum and keep the "
                "answer concise.\n\n"
                f"{docs_content}"
            )
            conversation_messages = [
                message
                for message in state["messages"]
                if message.type in ("human", "system")
                or (message.type == "ai" and not message.tool_calls)
            ]
            prompt = [SystemMessage(system_message_content)] + conversation_messages
            response = self.llm.invoke(prompt)
            return {"messages": [response]}

        graph_builder = StateGraph(MessagesState)
        graph_builder.add_node(query_or_respond)
        graph_builder.add_node(tools)
        graph_builder.add_node(generate)

        graph_builder.set_entry_point("query_or_respond")
        graph_builder.add_conditional_edges(
            "query_or_respond",
            tools_condition,
            {END: END, "tools": "tools"},
        )
        graph_builder.add_edge("tools", "generate")
        graph_builder.add_edge("generate", END)

        return graph_builder.compile(checkpointer=self.memory)

    def add_documents(self, documents: List[str]) -> bool:
        from langchain_community.vectorstores import FAISS
        from langchain.docstore.document import Document

        try:
            docs = [Document(page_content=content) for content in documents]
            self.vector_store.add_documents(docs)
            self.vector_store.save_local(self.vector_db_path)
            return True
        except Exception as e:
            print(f"[Error adding documents] {e}")
            return False

    def retrieve_relevant_docs(self, query: str, top_k: int = 5) -> List[str]:
        docs = self.vector_store.similarity_search(query, k=top_k)
        return [doc.page_content for doc in docs]

    def generate_response(self, query: str, context_docs: List[str]) -> str:
        system_msg = (
            "You are a helpful assistant. Answer using the context below:\n\n"
            + "\n\n".join(context_docs)
        )
        messages = [
            SystemMessage(content=system_msg),
            HumanMessage(content=query),
        ]
        response = self.llm.invoke(messages)
        return response.content

    def chat(self, user_input: str, session_id: str = "default-thread") -> str:
        try:
            for step in self.graph.stream(
                {"messages": [{"role": "user", "content": user_input}]},
                config={"configurable": {"thread_id": session_id}},
                stream_mode="values",
            ):
                last = step["messages"][-1]
            return last.content
        except Exception as e:
            print(f"[Chat error] {e}")
            return "Error occurred during chat."

