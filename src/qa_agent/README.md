# **AI-Powered Testcase Generation Agent**  

This repository contains an AI-driven agent workflow that processes a requirements document, summarizes it, and generates test cases in a selected format. It leverages **GROQ - Llama-3.2 1B-instruct** for AI processing and **LangGraph framework** for agent orchestration.  

## **Problem Statement**  

The goal of this project is to develop an AI-powered agent workflow that automates the generation of test cases from a given requirements document. The process consists of the following steps:  

1. **Summarizing the Requirements Document**  
   - **Agent 1** reads the requirements document (in `.doc` or `.txt` format) and extracts a point-wise summary.  
   - **Input:** Requirements document  
   - **Output:** Point-wise summary of the document  

2. **Router Functionality**  
   - The summarized requirements are formatted based on the desired test case structure (e.g., Gherkin, Selenium, etc.).  

3. **Generating Test Cases**  
   - **Agent 2** takes the summarized requirements and generates test cases in the selected format.  
   - **Input:** Point-wise summary of the document  
   - **Output:** Test cases in the selected format  

## **Tech Stack**  

- **AI Model:** GROQ - Llama-3.2 1B-instruct  
- **Agent Orchestration:** LangGraph framework  

## **Installation & Usage**  

### **1. Clone the Repository**  
```sh
git clone https://github.com/yogeshhk/MicroSaas.git
```

### **2. Navigate to the Project Directory**  
```sh
cd MicroSaaS/src/qa_agent
```

### **3. Install Dependencies**  
```sh
pip install -r requirements.txt
```

### **4. Set Up API Keys**  
Create a `.streamlit` folder in the root directory and add a `secrets.toml` file with the following contents:  
```toml
GROQ_API_KEY = "your_GROQ_api_key"
TAVILY_API_KEY = "your_Tavily_api_key"
```

### **5. Run the Application**  
```sh
python -m streamlit run app.py
```

## **Contributing**  

Contributions are welcome! Feel free to open issues or submit pull requests to improve the project.  

## **License**  

This project is licensed under the **MIT License**.  
