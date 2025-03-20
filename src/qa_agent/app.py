import streamlit as st
from agent import initialize_app
import sys
import io

# Configure the Streamlit page layout
st.set_page_config(
    page_title="LangGraph Chatbot",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🤖"
)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar layout
with st.sidebar:
    st.title("🤖 LangGraph Chatbot")

    # Initialize session state for the model if it doesn't exist
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "llama-3.1-8b-instant"

    model_list = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]

    st.session_state.selected_model = st.selectbox(
        "🤖 Select Model",
        model_list,
        key="model_selector",
        index=model_list.index(st.session_state.selected_model)
    )

    reset_button = st.button("🔄 Reset Conversation", key="reset_button")
    if reset_button:
        st.session_state.messages = []

# Initialize the LangGraph application with the selected model
app = initialize_app(model_name=st.session_state.selected_model)

# Title and description
st.title("📘 LangGraph Chat Interface")
st.markdown(
    """
    <div style="text-align: left; font-size: 18px; margin-top: 20px; line-height: 1.6;">
        🤖 <b>Welcome to the LangGraph Chatbot!</b><br>
        I can assist you by answering your questions using AI-powered workflows.
        <p style="margin-top: 10px;"><b>Start by typing your question below, and I'll provide an intelligent response!</b></p>
    </div>
    """,
    unsafe_allow_html=True
)

# Display conversation history
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"**You:** {message['content']}")
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(f"**Assistant:** {message['content']}")

# Input box for new messages
if user_input := st.chat_input("Type your question here (Max. 150 char):"):
    if len(user_input) > 150:
        st.error("Your question exceeds 150 characters. Please shorten it.")
    else:
        # Add user's message to session state and display it
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(f"**You:** {user_input}")

        # Capture print statements from agentic_rag.py
        output_buffer = io.StringIO()
        sys.stdout = output_buffer  # Redirect stdout to the buffer

        try:
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                debug_placeholder = st.empty()
                streamed_response = ""

                # Show spinner while streaming the response
                with st.spinner("Thinking..."):
                    inputs = {"question": user_input}
                    for i, output in enumerate(app.stream(inputs)):
                        # Capture intermediate print messages
                        debug_logs = output_buffer.getvalue()
                        debug_placeholder.text_area(
                            "Debug Logs",
                            debug_logs,
                            height=100,
                            key=f"debug_logs_{i}"
                        )

                        if "generate" in output and "generation" in output["generate"]:
                            chunk = output["generate"]["generation"]

                            # Safely extract the text content
                            if hasattr(chunk, "content"):  # If chunk is an AIMessage
                                chunk_text = chunk.content
                            else:  # Otherwise, convert to string
                                chunk_text = str(chunk)

                            # Append the text to the streamed response
                            streamed_response += chunk_text

                            # Update the placeholder with the streamed response so far
                            response_placeholder.markdown(f"**Assistant:** {streamed_response}")

                # Store the final response in session state
                st.session_state.messages.append({"role": "assistant", "content": streamed_response or "No response generated."})

        except Exception as e:
            # Handle errors and display in the conversation history
            error_message = f"An error occurred: {e}"
            st.session_state.messages.append({"role": "assistant", "content": error_message})
            with st.chat_message("assistant"):
                st.error(error_message)
        finally:
            # Restore stdout to its original state
            sys.stdout = sys.__stdout__
