import os
import streamlit as st
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langchain_groq.chat_models import ChatGroq
from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re

## <YHK> Each client atomatically searches for these specific keys in ENV

# os.environ["TAVILY_API_KEY"]=st.secrets["TAVILY_API_KEY"]
# os.environ["GROQ_API_KEY"]=st.secrets["GROQ_API_KEY"]

# tavily_api_key = os.getenv("TAVILY_API_KEY")
# groq_api_key = os.getenv("GROQ_API_KEY")

#############################################################################
# 1. Define the GraphState 
#############################################################################
class GraphState(TypedDict):
    user_request: str
    requirements_docs_content: str
    requirements_docs_summary: str
    gherkin_testcases: str
    selenium_testcases: str  
    testcases_format_flag: str
    testcases: str

#############################################################################
# 2. Router function to decide whether to output gherkin or selenium
#############################################################################
def route_user_request(state: GraphState) -> str:
    print(f"YHK: inside route_user_request with state as {state}")
    user_request = state["user_request"]
    # testcases_format_flag = state.get("testcases_format_flag", "False")
    tool_selection = {
    "gherkin_testcases": (
        "Use requests generation of testcases in Gherkin format "
    ),
    "selenium_testcases": (
        "Use requests generation of testcases in Selenium format"
    )
    }

    SYS_PROMPT = """Act as a router to select specific testcase foramt or functions based on user's request, using the following rules:
                    - Analyze the given user's request and use the given tool selection dictionary to output the name of the relevant tool based on its description and relevancy. 
                    - The dictionary has tool names as keys and their descriptions as values. 
                    - Output only and only tool name, i.e., the exact key and nothing else with no explanations at all. 
                """

    # Define the ChatPromptTemplate
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYS_PROMPT),
            ("human", """Here is the user's request:
                        {question}
                        Here is the tool selection dictionary:
                        {tool_selection}
                        Output the required tool.
                    """),
        ]
    )

    # Pass the inputs to the prompt
    inputs = {
        "user_request": user_request,
        "tool_selection": tool_selection
    }

    # Invoke the chain
    tool = (prompt | st.session_state.llm | StrOutputParser()).invoke(inputs)
    tool = re.sub(r"[\\'\"`]", "", tool.strip()) # Remove any backslashes and extra spaces
    
    ## <YHK> Assuming only 2 for now
    if tool == "gherkin_testcases":
        state["testcases_format_flag"] = "gherkin_testcases"
    else:
        state["testcases_format_flag"] = "selenium_testcases"
        
    print(f"Invoking {tool} tool through {st.session_state.llm.model_name}")
    return tool

def generate_testcases(user_request, requirements_content, llm, format_type):
    prompt = (
    "You are an expert in generating QA testcases for any known formats"
    "Study the given 'Requirements Documents Content' carefully and generate about 5-10 testcases in the suggested 'Format'"
    "You may want to look at the original User Request just to make sure that you are ansering th request properly."
    f"User Request: {user_request}\n\n"
    f"equirements Documents Content: {requirements_content}\n\n"
    f"Format: {format_type}"
    "Answer:"
    )
    try:
        response = llm.invoke(prompt)
    except Exception as e:
        response = f"Error generating answer: {str(e)}"
        
    return response

#############################################################################
# 3. To generate Gherikin formatted Testcases
#############################################################################
def generate_gherkin_testcases(state: GraphState) -> GraphState:
    """
    Uses LLM to generate Gherikin formatted Testcases of `requirements_docs_summary`.
    """
    print(f"YHK: inside generate_gherkin_testcases with state as {state}")

    user_request = state["user_request"]
    requirements_docs_summary = state.get("requirements_docs_summary", "")
    testcases_format_flag = state.get("testcases_format_flag", "False")
    if "llm" not in st.session_state:
        raise RuntimeError("LLM not initialized. Please call initialize_app first.")

    response = generate_testcases(user_request, requirements_docs_summary,st.session_state.llm, testcases_format_flag)
    
    state ['testcases'] = response
    
    return state

#############################################################################
# 4. To generate Selenium formatted Testcase
#############################################################################
def generate_selenium_testcases(state: GraphState) -> GraphState:
    """
    Uses LLM to generate Selenium formatted Testcases of `requirements_docs_summary`.
    """    
    print(f"YHK: inside generate_selenium_testcases with state as {state}")
    
    user_request = state["user_request"]
    requirements_docs_summary = state.get("requirements_docs_summary", "")
    testcases_format_flag = state.get("testcases_format_flag", "False")
    if "llm" not in st.session_state:
        raise RuntimeError("LLM not initialized. Please call initialize_app first.")

    response = generate_testcases(user_request, requirements_docs_summary,st.session_state.llm, testcases_format_flag)
    
    state ['testcases'] = response
    
    return state


#############################################################################
# 5. Build the LangGraph pipeline
#############################################################################
workflow = StateGraph(GraphState)
# Add nodes
workflow.add_node("gherkin_testcases", generate_gherkin_testcases)
workflow.add_node("selenium_testcases", generate_selenium_testcases)
# We'll route from "route_user_request" to either "gherkin_testcases" or "selenium_testcases"
# From "gherkin_testcases" -> END
# From "geselenium_testcasesnerate" -> END 
workflow.set_conditional_entry_point(
    route_user_request,  # The router function
    {
        "gherkin_testcases": "generate_gherkin_testcases",
        "selenium_testcases": "generate_selenium_testcases"
    }
)
workflow.add_edge("gherkin_testcases", END)
workflow.add_edge("selenium_testcases", END)

#############################################################################
# 6. The initialize_app function
#############################################################################
def initialize_app(model_name: str):
    """
    Initialize the app with the given model name, avoiding redundant initialization.
    """
    # Check if the LLM is already initialized
    if "selected_model" in st.session_state and st.session_state.selected_model == model_name:
        return workflow.compile()  # Return the compiled workflow directly

    # Initialize the LLM for the first time or switch models
    st.session_state.llm = ChatGroq(model=model_name, temperature=0.0)
    st.session_state.selected_model = model_name
    print(f"Using model: {model_name}")
    return workflow.compile()

