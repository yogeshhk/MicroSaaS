###################################################################################################
# Problem statement : Create the following workflow using groq API
#
# Workflow 1
# Input : Requirements document
# Output : Point wise Summary of Document
#
# Workflow 2
# # Input : Point wise Summary of Document
# # Output : testcases in Gherkin format
#
# Workflow 3
# # Input : Gherkin testcases
# # Output : Selenium testcases for each scenario from Gherkin testcases


###################################################################################################
import requests
import json
import os
from groq import Groq

client = Groq(
    api_key= os.getenv("GROQ_API_KEY")
)

def simple_AI_Function_Agent(prompt):
    try:
        print("Prompt : \n", prompt)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        headers = {
            "Content-Type": "application/json"
        }

        summary = chat_completion.choices[0].message.content

        return summary

    except requests.exceptions.RequestException as e:
        return f"Error connecting to model: {e}"
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        return f"Error parsing model response: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
########################################################################################################################

requirements_doc = """
The system shall allow users to create and manage their accounts. 
Users shall be able to log in using their email address and password. 
The system must provide a password reset functionality. 
The system shall display a dashboard with key performance indicators. 
The system shall generate reports in PDF format. 
The system shall integrate with a third-party payment gateway.
The system needs to be scalable to handle 10,000 concurrent users.
The system must ensure data security and comply with GDPR regulations.
"""
print("#############################################################################")

prompt = "Generate a summary of following document : "+ requirements_doc
summary = simple_AI_Function_Agent(prompt)
print("Summary of Requirements document: \n", summary)

print("#############################################################################")

prompt = "Create testcases in Gherkin format using summary : " + summary
gherkin_testcases = simple_AI_Function_Agent(prompt)
print("Testcases in Gherkin format : \n", gherkin_testcases)

print("#############################################################################")

prompt = "Create selenium testcases for each scenario : " + gherkin_testcases
selenium_testcases = simple_AI_Function_Agent(prompt)
print(selenium_testcases)
