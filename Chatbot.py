import streamlit as st
import requests
import base64
import pyttsx3
import webbrowser
from bokeh.models.widgets import Div

def generate_audio(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def main():
    # Remove the second call to st.set_page_config
    # st.set_page_config(page_title="Student Information Retrieval", layout="wide")

    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

    st.title("Student Information Retrieval")

    # User input
    user_input = st.text_input("You", key="input", placeholder="Enter your query...")

    # Capture image
    # capture_image_button = st.button("Capture Image")
    # if capture_image_button:
    #     captured_image = st.camera_input("Capture Image")
    #     if captured_image is not None:
    #         # Convert the captured image to base64
    #         with open("captured_image.png", "wb") as f:
    #             f.write(captured_image.getvalue())
    #         with open("captured_image.png", "rb") as f:
    #             image_bytes = f.read()
    #         image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    #         if st.button("Submit Image"):
    #             # Send the base64-encoded image to localhost:8000
    #             try:
    #                 url = 'http://localhost:8000/upload_image'
    #                 data = {'image_base64': image_base64, 'status': 'Entry'}
    #                 response = requests.post(url, json=data)
    #                 if response.status_code == 200:
    #                     st.success("Image uploaded successfully!")
    #                 else:
    #                     st.error("Error uploading image.")
    #             except requests.exceptions.RequestException as e:
    #                 st.error(f"Error: {str(e)}")

    if st.button("Submit Query"):
        if user_input:
            try:
                url = 'http://localhost:5000/get_student_info'
                data = {'prompt': user_input}
                response = requests.post(url, json=data)
                response_data = response.json()

                if 'response' in response_data:
                    st.session_state.past.append(user_input)
                    st.session_state.generated.append(response_data['response'])
                    # Generate audio output
                    generate_audio(response_data['response'])
                elif 'error' in response_data:
                    st.session_state.past.append(user_input)
                    st.session_state.generated.append(f"Error: {response_data['error']}")
                else:
                    st.session_state.past.append(user_input)
                    st.session_state.generated.append("An error occurred while processing the request.")
            except requests.exceptions.RequestException as e:
                st.session_state.past.append(user_input)
                st.session_state.generated.append(f"Error: {str(e)}")
        else:
            st.session_state.past.append("")
            st.session_state.generated.append("Please enter a query.")

    url_to_open = "http://localhost:3000"

    # Create a button to open the link in the same tab
    if st.button("Capture Image"):
        webbrowser.open_new_tab(url_to_open)

    # Display the chat history (moved outside of the if statement)
    for i, (user_message, bot_message) in enumerate(zip(st.session_state.past, st.session_state.generated)):
        if user_message:
            st.markdown(
                f"<div style='background-color: #843799; color: white; padding: 10px; border-radius: 10px; margin-bottom: 10px; '>{user_message}</div>",
                unsafe_allow_html=True
            )
        if bot_message:
            st.markdown(
                f"<div style='background-color: #f58cc9; color: white; padding: 10px; border-radius: 10px; margin-bottom: 10px; '>{bot_message}</div>",
                unsafe_allow_html=True
            )

if __name__ == '__main__':
    main()
