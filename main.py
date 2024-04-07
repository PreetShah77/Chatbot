# # import streamlit as st
# # import speech_recognition as sr
# # import requests
# # import re
# # import pyttsx3

# # # Google Sheet ID and sheet name
# # sheet_id = "1hl3uC3BmTu7GNFF_ixkCuqn4apPNcVdOA53htNwZDIY"
# # sheet_name = "AllStudents"

# # # Mapping of output types to column names
# # output_types = {
# #     "enrollment number": "Enrollment No.",
# #     "mobile number": "Student Phone No",
# #     "class": "Class",
# #     "email id": "Student gnu mail Id",
# #     "semester": "Semester",
# #     "batch": "Batch"
# # }

# # # Function to fetch student data from the Google Sheet
# # def get_student_data(first_name, last_name=None, output_type=None):
# #     if last_name:
# #         student_name = f"{last_name} {first_name}"
# #     else:
# #         student_name = first_name
# #     url = f"https://script.google.com/macros/s/AKfycbwP3XOlI33GcQzZ1m7DWzt-CuwRy3YB8BBwGU_0lFf7KD56kUY/exec?spreadsheet=a&action=getbyname&id={sheet_id}&sheet={sheet_name}&sheetuser={student_name}&sheetuserIndex=2"
# #     response = requests.get(url)
# #     data = response.json()

# #     if isinstance(data, dict) and 'records' in data:
# #         return data['records']
# #     else:
# #         return None  # Handle invalid API response format

# # # Function to extract information from a sentence
# # def extract_information(sentence):
# #     name = None
# #     output_type = None

# #     # Check for common output type patterns using regex
# #     for key, value in output_types.items():
# #         if re.search(f"{key} of", sentence.lower()):
# #             output_type = key
# #             name = re.search(f"{key} of (.+)", sentence.lower()).group(1)
# #             break

# #     # Check for full name
# #     if not name:
# #         name_match = re.search(r'(.+?) (.+)', sentence)
# #         if name_match:
# #             first_name = name_match.group(1)
# #             last_name = name_match.group(2)
# #             name = {"first_name": first_name, "last_name": last_name}

# #     return name, output_type

# # # Function to search Google API for the last name
# # def search_google_api(last_name):
# #     # Here you can implement the logic to search Google API for the last name
# #     # For demonstration purposes, we'll print a message
# #     print(f"Searching Google API for last name: {last_name}")

# # # Function to get user input using speech recognition
# # def get_user_input():
# #     r = sr.Recognizer()
# #     with sr.Microphone() as source:
# #         st.write("Speak your question:")
# #         audio = r.listen(source)
# #     try:
# #         user_input = r.recognize_google(audio)
# #         st.write(f"You asked: {user_input}")
# #         return user_input
# #     except sr.UnknownValueError:
# #         st.write("Sorry, I couldn't understand your question.")
# #         return None
# #     except sr.RequestError as e:
# #         st.write(f"Could not request results from Google Speech Recognition service; {e}")
# #         return None

# # # Function to generate audio response
# # def generate_audio(text):
# #     engine = pyttsx3.init()
# #     engine.say(text)
# #     engine.runAndWait()

# # # Streamlit app
# # def app():
# #     st.title("Student Information Retrieval")

# #     while True:
# #         # Get user question using speech recognition
# #         generate_audio("What is your Question?")
# #         user_input = get_user_input()
# #         if not user_input:
# #             st.write("Exiting conversation.")
# #             break

# #         # Extract information from the user's question
# #         name, output_type = extract_information(user_input)
# #         if not name or not output_type:
# #             st.write("Could not extract information from the question. Please try again.")
# #             continue

# #         if isinstance(name, dict):
# #             first_name = name.get("first_name")
# #             last_name = name.get("last_name")
# #         else:
# #             first_name = name
# #             last_name = None

# #         # Fetch student data based on first name and last name
# #         student_data = get_student_data(first_name, last_name, output_type)

# #         if not student_data:
# #             st.write(f"No data found for {first_name} {last_name}." if last_name else f"No data found for {first_name}.")
# #             continue

# #         # Display student data
# #         output_text = None
# #         if len(student_data) == 1:
# #             st.write(f"The {output_type} is: {student_data[0][output_types[output_type]]}")
# #             output_text = f"The {output_type} is: {student_data[0][output_types[output_type]]}"
# #             generate_audio(output_text)
# #         else:
# #             st.write(f"Multiple records found for {first_name} {last_name}." if last_name else f"Multiple records found for {first_name}.")

# #             # Ask for semester from the user
# #             generate_audio("Please provide the semester to filter the records.")
# #             user_semester = get_user_input()
# #             if not user_semester:
# #                 st.write("No semester provided. Please try again.")
# #             else:
# #                 filtered_data = [data for data in student_data if data.get("Semester") == user_semester]
# #                 if not filtered_data:
# #                     st.write(f"No records found for {first_name} {last_name} with semester {user_semester}.")
# #                 else:
# #                     for data in filtered_data:
# #                         st.write(data)

# #         # Search Google API for the last name
# #         if last_name:
# #             search_google_api(last_name)

# # if __name__ == "__main__":
# #     app()
# import spacy

# # Load the English language model
# nlp = spacy.load("en_core_web_sm")

# def extract_name(sentence):
#     # Process the sentence with the NLP model
#     doc = nlp(sentence)
    
#     # Iterate over the entities in the sentence
#     for ent in doc.ents:
#         # Check if the entity is a person
#         if ent.label_ == "PERSON":
#             return ent.text
    
#     # If no person entity is found, return "Name not found"
#     return "Name not found"

# # Example usage
# sentence = "what is enrollment number of Manthan Mehta"
# name = extract_name(sentence)
# print(f"The name in the sentence is: {name}")
from flask import Flask, request, jsonify
import os
import requests
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import re
import spacy

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
sheet_id = "1hl3uC3BmTu7GNFF_ixkCuqn4apPNcVdOA53htNwZDIY"
sheet_name = "AllStudents"

nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)

@app.route('/api/submit', methods=['POST'])
def submit_message():
    data = request.json
    message = data['message']
    response = user_input(message)
    return jsonify({'response': response})

def extract_student_name(sentence):
    doc = nlp(sentence)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Name not found"

def get_student_data(first_name):
    student_name = first_name
    url = f"https://script.google.com/macros/s/AKfycbwP3XOlI33GcQzZ1m7DWzt-CuwRy3YB8BBwGU_0lFf7KD56kUY/exec?spreadsheet=a&action=getbyname&id={sheet_id}&sheet={sheet_name}&sheetuser={student_name}&sheetuserIndex=2"
    response = requests.get(url)
    data = response.json()
    if isinstance(data, dict) and 'records' in data:
        return data['records']
    else:
        return None

def user_input(prompt):
    student_name = extract_student_name(prompt)
    if student_name is None:
        return "No student name detected in the query."
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    student_data = get_student_data(student_name)
    if not student_data:
        return "No student found with the given name."
    elif len(student_data) > 1:
        return handle_multiple_students(student_data, prompt)
    else:
        student_dict = student_data[0]
        context = str(student_dict)
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        chunks = text_splitter.split_text(context)
        documents = [Document(page_content=chunk) for chunk in chunks]
        chain = get_conversational_chain()
        response = chain({"input_documents": documents, "question": prompt}, return_only_outputs=True)
        return response['output_text']

def handle_multiple_students(student_data, prompt):
    st.write("Multiple students found with the same name:")
    options = []
    for i, student in enumerate(student_data, start=1):
        name = student['Name of Student']
        options.append(f"Option {i}: {name}")
        st.write(f"Option {i}: {name}")

    selected_option = st.selectbox("Select the student you want information about:", options)
    selected_index = options.index(selected_option)
    selected_student = student_data[selected_index]
    print(selected_student)
    context = str(selected_student)
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    chunks = text_splitter.split_text(context)
    documents = [Document(page_content=chunk) for chunk in chunks]
    chain = get_conversational_chain()
    response = chain({"input_documents": documents, "question": prompt}, return_only_outputs=True)
    return response['output_text']

if __name__ == "__main__":
    app.run(debug=True)