import os
import requests
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import streamlit as st
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import re
import speech_recognition as sr
import pyttsx3

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
sheet_id = "1hl3uC3BmTu7GNFF_ixkCuqn4apPNcVdOA53htNwZDIY"
sheet_name = "AllStudents"

import nltk
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.tree import Tree

import spacy

# Load the English language model
nlp = spacy.load("en_core_web_sm")

def extract_student_name(sentence):
    # Process the sentence with the NLP model
    doc = nlp(sentence)
    
    # Iterate over the entities in the sentence
    for ent in doc.ents:
        # Check if the entity is a person
        if ent.label_ == "PERSON":
            return ent.text
    
    # If no person entity is found, return "Name not found"
    return "Name not found"

# Get student data from Google API
def get_student_data(first_name):
    student_name = first_name
    url = f"https://script.google.com/macros/s/AKfycbwP3XOlI33GcQzZ1m7DWzt-CuwRy3YB8BBwGU_0lFf7KD56kUY/exec?spreadsheet=a&action=getbyname&id={sheet_id}&sheet={sheet_name}&sheetuser={student_name}&sheetuserIndex=2"
    response = requests.get(url)
    data = response.json()

    if isinstance(data, dict) and 'records' in data:
        return data['records']
    else:
        return None

# Split student data into chunks
def get_text_chunks(student_data):
    text = str(student_data)
    splitter = CharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = splitter.split_text(text)
    return chunks

# Get embeddings for each chunk
def get_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hi there! What information can I help you with today?"}]

from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

def get_conversational_chain():
    prompt_template = """
    You are an AI assistant that can provide information about students based on the data available. The data is represented as a dictionary where keys are the information fields and values are the corresponding details.

    Given the following context and query, provide the requested information if it's available in the data. If the requested information is not available, respond with "I'm sorry, but the requested information is not available in the student's data."

    Context:
    {context}

    Query:
    {question}

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro", client=genai, temperature=0.3)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(llm=model, chain_type="stuff", prompt=prompt)
    return chain

def user_input(prompt):
    student_name = extract_student_name(prompt)
    print(student_name)
    if student_name is None:
        return "No student name detected in the query."
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    student_data = get_student_data(student_name)
    if not student_data:
        return "No student found with the given name."
    elif len(student_data) > 1:
        print(student_data)
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
    
def get_user_input():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Speak your question:")
        audio = r.listen(source)
    try:
        user_input = r.recognize_google(audio)
        st.write(f"You asked: {user_input}")
        return user_input
    except sr.UnknownValueError:
        st.write("Sorry, I couldn't understand your question.")
        return None
    except sr.RequestError as e:
        st.write(f"Could not request results from Google Speech Recognition service; {e}")
        return None

# Function to generate audio response
def generate_audio(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

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

def main():
    st.set_page_config(page_title="Student Information Chatbot", page_icon="‍")
    st.title("Chat with Student Information ‍")
    st.write("Welcome to the chat!")
    st.button('Clear Chat History', on_click=clear_chat_history)
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [{"role": "assistant", "content": "Hi there! What information can I help you with today?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input("You:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # if st.session_state.messages[-1]["role"] != "assistant":
    if prompt is not None:  # Check if prompt is not None
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = user_input(prompt)
                placeholder = st.empty()
                full_response = ''
                if isinstance(response, list):
                    for item in response:
                        full_response += item
                        placeholder.markdown(full_response)
                        generate_audio(full_response)
                else:
                    placeholder.markdown(response)
                    generate_audio(response)
        if response is not None:
            greeting = ""
            if "hello" in prompt.lower() or "hi" in prompt.lower():
                greeting = "Hi again! "
            message = {"role": "assistant", "content": greeting + full_response}
            st.session_state.messages.append(message)


if __name__ == "__main__":
    main()