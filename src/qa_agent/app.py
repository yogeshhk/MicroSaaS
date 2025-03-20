import streamlit as st

# App title
st.title("Testcase Generation Agent")

# Left sidebar
with st.sidebar:
    st.header("Configuration")
    uploaded_file = st.file_uploader("Upload Requirements Document", type=["txt", "pdf", "docx"])

    model_options = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    selected_model = st.selectbox("Select Model", model_options)

# Main window
user_query = st.text_input("Enter your query:")

if user_query:
    # Simulate AI processing (replace with actual AI logic)
    st.write("Generating test cases...")
    # Placeholder for AI output, replace with actual generated test cases
    generated_test_cases = f"**Generated Test Cases (using {selected_model}):**\n\nQuery: {user_query}\n\n1. Test Case 1\n2. Test Case 2\n3. Test Case 3\n\n... (more generated test cases)"
    st.markdown(generated_test_cases)