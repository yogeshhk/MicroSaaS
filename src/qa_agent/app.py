import streamlit as st
from agent import initialize_app
import io
import pypdf 

requirements_docs_content = ""

# App title
# st.title("Testcase Generation Agent")

# Configure the Streamlit page layout
st.set_page_config(
    page_title="Testcase Generation Agent",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🤖"
)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Left sidebar
with st.sidebar:
    st.header("Configuration")
    uploaded_file = st.file_uploader("Upload Requirements Document", type=["txt", "pdf", "docx"])
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            requirements_docs_content = uploaded_file.getvalue().decode("utf-8")
        elif uploaded_file.type == "application/pdf":
            pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            for page in pdf_reader.pages:
                requirements_docs_content += page.extract_text()

    # Now 'requirements_docs_content' contains the text from the uploaded file

    # Initialize session state for the model if it doesn't exist
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = "./content.txt"
        
    # Initialize session state for the model if it doesn't exist
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "llama-3.1-8b-instant"
        
    model_options = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    selected_model = st.selectbox("Select Model", model_options, key="model_selector", index=model_options.index(st.session_state.selected_model))
    
    reset_button = st.button("🔄 Reset Conversation", key="reset_button")
    if reset_button:
        st.session_state.messages = []    

# Initialize the LangGraph application with the selected model
app = initialize_app(model_name=st.session_state.selected_model)

# Main window
user_request = st.text_input("Enter your request:")

if user_request:
    if len(user_request) > 150:
        st.error("Your question exceeds 150 characters. Please shorten it.")
    else:
        # Add user's message to session state and display it
        st.session_state.messages.append({"role": "user", "content": user_request})
        with st.chat_message("user"):
            st.markdown(f"**You:** {user_request}")

    inputs = {"user_request": user_request, "requirements_docs_content": requirements_docs_content}
    print(f"YHK Inputs are {inputs}")
    
    # Simulate AI processing (replace with actual AI logic)
    st.write("Generating test cases...")
    # Placeholder for AI output, replace with actual generated test cases
    generated_test_cases = app.stream(inputs)

    # generated_test_cases = f"**Generated Test Cases (using {selected_model}):**\n\nQuery: {user_query}\n\n1. Test Case 1\n2. Test Case 2\n3. Test Case 3\n\n... (more generated test cases)"
    st.markdown(generated_test_cases)