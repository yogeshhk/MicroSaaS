import os
import streamlit as st
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq.chat_models import ChatGroq
from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re

# os.environ["TAVILY_API_KEY"]=st.secrets["TAVILY_API_KEY"]
# os.environ["GROQ_API_KEY"]=st.secrets["GROQ_API_KEY"]

tavily_api_key = os.getenv("TAVILY_API_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

#############################################################################
# 1. Define the GraphState (minimal fields: question, generation, websearch_content)
#############################################################################
class GraphState(TypedDict):
    question: str
    generation: str
    websearch_content: str  # we store Tavily search results here, if any
    web_flag: str #To know whether a websearch was used to answer the question

#############################################################################
# 2. Router function to decide whether to use web search or directly generate
#############################################################################
def route_question(state: GraphState) -> str:
    question = state["question"]
    web_flag = state.get("web_flag", "False")
    tool_selection = {
    "websearch": (
        "Questions requiring recent statistics, real-time information, recent news, or current updates. "
    ),
    "generate": (
        "Questions that require access to a large language model's general knowledge, but not requiring recent statistics, real-time information, recent news, or current updates."
    )
    }

    SYS_PROMPT = """Act as a router to select specific tools or functions based on user's question, using the following rules:
                    - Analyze the given question and use the given tool selection dictionary to output the name of the relevant tool based on its description and relevancy with the question. 
                    - The dictionary has tool names as keys and their descriptions as values. 
                    - Output only and only tool name, i.e., the exact key and nothing else with no explanations at all. 
                """

    # Define the ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYS_PROMPT),
            ("human", """Here is the question:
                        {question}
                        Here is the tool selection dictionary:
                        {tool_selection}
                        Output the required tool.
                    """),
        ]
    )

    # Pass the inputs to the prompt
    inputs = {
        "question": question,
        "tool_selection": tool_selection
    }

    # Invoke the chain
    tool = (prompt | st.session_state.llm | StrOutputParser()).invoke(inputs)
    tool = re.sub(r"[\\'\"`]", "", tool.strip()) # Remove any backslashes and extra spaces
    if tool == "websearch":
        state["web_flag"] = "True"
    print(f"Invoking {tool} tool through {st.session_state.llm.model_name}")
    return tool

#############################################################################
# 3. Websearch function to fetch context from Tavily, store in state["websearch_content"]
#############################################################################
def websearch(state: GraphState) -> GraphState:
    """
    Uses Tavily to search the web for the question, then appends results into `websearch_content`.
    """
    question = state["question"]
    
    if "tavily_client" not in st.session_state:
        st.session_state.tavily_client = TavilyClient(api_key=tavily_api_key)

    try:
        print("Performing Tavily web search...")
        search_result = st.session_state.tavily_client.get_search_context(
            query=question,
            search_depth="advanced",
            max_tokens=2048
        )
        # The tavily_client may return a string or dict
        if isinstance(search_result, dict) and "documents" in search_result:
            # Merge all doc contents
            docs = [doc.get("content", "") for doc in search_result["documents"]]
            state["websearch_content"] = "\n\n".join(docs)
            state["web_flag"] = "True"
        else:
            # If it's just a string or something else
            state["websearch_content"] = str(search_result)
            state["web_flag"] = "True"

    except Exception as e:
        print(f"Error during Tavily web search: {e}")
        state["websearch_content"] = f"Error from Tavily: {e}"

    return state

#############################################################################
# 4. Generation function that calls Groq LLM, optionally includes websearch content
#############################################################################
def generate(state: GraphState) -> GraphState:
    question = state["question"]
    context = state.get("websearch_content", "")
    web_flag = state.get("web_flag", "False")
    if "llm" not in st.session_state:
        raise RuntimeError("LLM not initialized. Please call initialize_app first.")

    prompt = (
        "You are a helpful assistant specialized in providing helpful information.\n\n"
        "If context is available, answer the question based on the context."
        "If there is no context with the question, answer the question from your own knowledge."
        "If web_flag is 'True', cite all the URLs in the context in this format: Sources: \n URL1\n URL2, ..."
        f"Question: {question}\n\n"
        f"Context: {context}\n\n"
        f"web_flag: {web_flag}"
        "Answer:"
        )
    try:
        response = st.session_state.llm.invoke(prompt)
        state["generation"] = response
    except Exception as e:
        state["generation"] = f"Error generating answer: {str(e)}"

    return state

#############################################################################
# 5. Build the LangGraph pipeline
#############################################################################
workflow = StateGraph(GraphState)
# Add nodes
workflow.add_node("websearch", websearch)
workflow.add_node("generate", generate)
# We'll route from "route_question" to either "websearch" or "generate"
# Then from "websearch" -> "generate" -> END
# From "generate" -> END directly if no search is needed.
workflow.set_conditional_entry_point(
    route_question,  # The router function
    {
        "websearch": "websearch",
        "generate": "generate"
    }
)
workflow.add_edge("websearch", "generate")
workflow.add_edge("generate", END)

#############################################################################
# 6. The initialize_app function
#############################################################################
def initialize_app(model_name: str):
    """
    Initialize the app with the given model name, avoiding redundant initialization.
    """
    # Check if the LLM is already initialized
    if "current_model" in st.session_state and st.session_state.current_model == model_name:
        return workflow.compile()  # Return the compiled workflow directly

    # Initialize the LLM for the first time or switch models
    st.session_state.llm = ChatGroq(model=model_name, temperature=0.0)
    st.session_state.current_model = model_name
    print(f"Using model: {model_name}")
    return workflow.compile()

