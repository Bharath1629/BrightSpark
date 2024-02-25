import streamlit as st
from agent import *
import os
from PIL import Image
from google.oauth2 import service_account
from google.cloud import aiplatform
import logging
from datetime import datetime
from bigquery import process_form_and_insert_data, insert_feedback
from audio_recorder_streamlit import audio_recorder
from utils import text_to_speech, autoplay_audio, speech_to_text
from streamlit_float import *


# Environment setup
credentials = service_account.Credentials.from_service_account_file('credentials.json')
project_id = 'theta-cell-406519'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials.json"
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_ENDPOINT"]="https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"]="ls__2c71a48e75284d6792f6e31360d2ae3e"
os.environ["LANGCHAIN_PROJECT"]="ChatBot"

# Vertex AI
def predict_text_classification_single_label_sample(project="719559140092",location="us-central1", endpoint= "398667523068788736",content="{user_input}"):
    aiplatform.init(project=project, location=location)
    endpoint = aiplatform.Endpoint(endpoint)
    response = endpoint.predict(instances=[{"content": content}], parameters={})
    names=response[0][0]['displayNames']
    values=response[0][0]['confidences']
    max_index=values.index(max(values))
    return names[max_index]

logging.basicConfig(level=logging.INFO)
# Title of ChatBot
st.image("images/img.png",width=500)

# Sidebar Style
st.markdown(
    """
    <style>
    .sidebar .sidebar-content .block-container {
        padding: 2rem;
        color: white;
    }
    .middle-buttons {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    .user-message {
        background-color: #ffcc66;
        border-radius: 10px;
        padding: 5px 10px;
        margin: 0 0 10px auto;
        text-align: right;
        max-width: fit-content;
        
    }
    .agent-message {
        background-color: #ffeecc;
        border-radius: 10px;
        padding: 5px 10px;
        margin: 0 auto 10px 0;
        max-width:fit-content;
        text-align: left;
    }
        .chat-container {
        height: 100px;
        overflow-y: auto;
    }
    .logo-and-title {
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 1;
        padding: 10px;
    }
    .logo-and-title.sticky {
        position: fixed;
        width: 100%;
    }
    .sidebar-section {
        padding: 20px;
        background-color: #f0f0f0;
        border-radius: 10px;
        margin-bottom: 20px;
        cursor: pointer;
    }
    .button-container {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
    .appointment-button, .ticket-button {
        border: 2px solid #FFA500; 
        border-radius: 5px;
        background-color: transparent;
        color: #FFA500; 
        font-weight: bold;
        padding: 8px 16px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .appointment-button:hover, .ticket-button:hover {
        background-color: #FFA500; 
        color: white;
    }
    [data-testid=stSidebar] {
        background-color:  #FFD700;
        #border: 2px solid #FF0000; /* Red boundary */
        margin-bottom: 10px;
        border-radius: 5px;
        # border: 2px solid white;
    }  
    </style>
    """,
    unsafe_allow_html=True
)


st.sidebar.title("About Brightspeed")
# sidebar image
image = Image.open("images/bot_image1.png")

# Add a white border around the image
image_with_border = Image.new("RGB", (image.width + 4, image.height + 4), "white")
image_with_border.paste(image, (2, 2))
# Display the image with the white border
st.sidebar.image(image_with_border)
st.sidebar.link_button(label="🏠 Home",url="https://www.brightspeedsavings.com/")
st.sidebar.link_button(label="🛒 Data Plans",url="https://www.brightspeedplans.com/internet")
st.sidebar.link_button(label="☎️ Customer Service",url="https://www.brightspeedplans.com/customer-service")
st.sidebar.link_button(label="📰 Newsroom",url="https://www.brightspeed.com/brightspeed-news/")
st.sidebar.link_button(label="📝 FAQs",url="https://www.brightspeedplans.com/faq")
st.sidebar.image("images/Brightspeed_Logo_Full.png",caption="Let's Connect")

# Sidebar navigation
sidebar_selection = st.sidebar.radio("Navigation", ["Home", "About", "Feedback"])

# Handle sidebar navigation
if sidebar_selection == "Home":
    if 'chat-history' not in st.session_state:
        st.session_state['chat-history'] = [{
            "content": "Hi, I'm a Brightspeed agent. How can I help you today?",
            "role": "ai"
        }]
        #Chat input
    user_input = st.chat_input('Message:', key="user_input")
    # Hide both forms when the user starts typing
    if user_input:
        st.session_state['show_installation_form'] = False
        st.session_state['show_ticket_form'] = False
    col1, col2 = st.columns(2, gap="small")
    with col1:
        if st.button("Appointment", key="appointment_button"):
            st.session_state['show_installation_form'] = True
            st.session_state['show_ticket_form'] = False
    with col2:
        if st.button("Submit Ticket", key="ticket_button"):
            st.session_state['show_ticket_form'] = True
            st.session_state['show_installation_form'] = False

    if st.session_state.get('show_installation_form', False):
        with st.form(key="appointment_form",clear_on_submit=True):
            # Display installation form if "Schedule Installation Time" button is clicked
            st.title("Schedule Installation Time")
            # Form for user information and time slot selection
            st.write("Please fill out the following information:")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            home_address = st.text_input("Home Address")
            city = st.text_input("City")
            state = st.text_input("State")
            zipcode = st.text_input("Zipcode")
            phone_num = st.text_input("Phone Number")
            st.write("Please select a date and time for the appointment:")
            st.session_state.appointment_date = st.date_input("Select Date")
            time_slots = ["9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM",
                          "12:00 PM", "12:30 PM", "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM",
                          "3:00 PM", "3:30 PM", "4:00 PM", "4:30 PM", "5:00 PM"]
            default_time_slot = st.session_state.get("selected_time_slot", time_slots[0]) if st.session_state.get("selected_time_slot") else time_slots[0]
            st.session_state.selected_time_slot = st.selectbox("Select Time Slot", time_slots, index=time_slots.index(default_time_slot))
            submit_button = st.form_submit_button("Submit")
            if submit_button:
                form_data ={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "home_address": home_address,
                    "city": city,
                    "state": state,
                    "zipcode" : zipcode,
                    "phone_num": phone_num,
                    "appointment_date": st.session_state.appointment_date,
                    "selected_time_slot": st.session_state.selected_time_slot
                }
                process_form_and_insert_data(form_data,"schedule_installation_time")
                st.session_state['show_installation_form'] = False

    #Submit Ticket Button
    if st.session_state.get('show_ticket_form', False):
        with st.form(key="ticket_form", clear_on_submit=True):
            #Submit Ticket Form
            st.title("Submit Ticket")
            st.write("Please select the type of business you have:")
            business_type = st.selectbox("Business Type:", ["Residential Home", "Small Business", "Wholesale", "Medium and Enterprise"])
            st.write("What issue are you experiencing?")
            issue = st.selectbox("Issue", ["Slow Internet Connection", "Connection Drop", "Wifi Connectivity Problems", "Router Configuration", "Device Connectivity", "Internet Browser Problems", "Network Congestion"])
            st.write("Please fill out the following information:")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            description = st.text_area("Description")
            submit_button = st.form_submit_button("Submit")
            if submit_button:
                form_data = {
                    "business_type": str(business_type),
                    "issue": str(issue),
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "description":description
                }
                process_form_and_insert_data(form_data,"submit_ticket")
    audio_bytes = audio_recorder(text=" ",icon_size="2x")
    while user_input or audio_bytes:
        if user_input:
            # message = anonymize(user_input) #add
            st.session_state['chat-history'].append({
                "content": user_input,#message
                "role": "user"
            })
            classifier = predict_text_classification_single_label_sample(content=user_input)
            get_agent_type(classifier)

            try:
                agent_response = agent_execution.invoke({'input':user_input})

                st.session_state['chat-history'].append({
                    "content": agent_response["output"],
                    "role": "ai"})
                # print(agent_response)
                audio_bytes = None
                break
            except:
                st.session_state['chat-history'].append({
                    "content": "Sorry, I'm not sure I can help with that.For more information contact our customer support at 833-692-7773",
                    "role": "ai"})
                audio_bytes = None
                break

        elif audio_bytes:
            try:
                with st.spinner("Transcribing..."):

                    webm_file_path = "temp_audio.mp3"
                    with open(webm_file_path, "wb") as f:
                        f.write(audio_bytes)


                    transcript = speech_to_text(webm_file_path)
                    if transcript:
                        st.session_state['chat-history'].append({"role": "user", "content": transcript})
                        # with st.chat_message("user"):
                        #     st.write(transcript)
                        os.remove(webm_file_path)
                        classifier = predict_text_classification_single_label_sample(content=transcript)
                        # agent = get_agent(classifier)
                        get_agent_type(classifier)
                        if st.session_state['chat-history'][-1]['role'] != "ai":
                            with st.chat_message("ai"):
                                with st.spinner("Thinking🤔..."):
                                    final_response = agent_execution.invoke({"input":transcript})
                                    with st.spinner("Generating audio response..."):
                                        audio_file = text_to_speech(final_response["output"])
                                        autoplay_audio(audio_file)
                                # st.write(final_response["output"])
                                st.session_state['chat-history'].append({"role": "ai", "content": final_response["output"]})
                                os.remove(audio_file)


                                user_input = None
                                break
            except:
                st.session_state['chat-history'].append({"role": "ai","content": "Sorry, I'm not sure I can help with that.For more information contact our customer support at 833-692-7773"})
                audio_file = text_to_speech(st.session_state['chat-history'][-1]["content"])
                autoplay_audio(audio_file)
                st.write(st.session_state['chat-history'][-1]["content"])
                user_input=None
                break

    else:
        st.session_state['show_buttons'] = True

    # Function to get current timestamp
    def get_timestamp():
        now = datetime.now()
        return now.strftime("%I:%M:%S %p")

    # Function to display chat messages
    def display_chat_message_with_timestamp(role, content, timestamp):
        if role == "user":
            message_class = "user-message"
            timestamp_style = "float: right;"
        else:
            message_class = "agent-message"
            timestamp_style = ""

        st.write(f'<div class="chat-message">', unsafe_allow_html=True)
        st.write(f'<div class="timestamp" style="{timestamp_style}">{timestamp}</div>', unsafe_allow_html=True)
        st.write(f'<div class="{message_class}">{content}</div>', unsafe_allow_html=True)
        st.write('</div>', unsafe_allow_html=True)
    # Display chat messages with timestamps above inside a container with a scrollbar
    with st.container(height=700):
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        if st.session_state['chat-history']:
            for i in range(0, len(st.session_state['chat-history'])):
                user_message = st.session_state['chat-history'][i]
                display_chat_message_with_timestamp(user_message["role"], user_message['content'], get_timestamp())
        st.markdown('</div>', unsafe_allow_html=True)

elif sidebar_selection == "About":
    st.write("""Bright Spark is a chat bot leverages Retrieval Augmented Generation (RAG) powered by LangChain and a variety of "
            tools,including document retrieval from vector databases and cloud services. With a Streamlit interface, users can
            engage with an AI agent equipped with conversational memory, providing personalized interactions based on past discussions.
            
            Here are some example queries you can try with SnowChat:

            Can you tell me about BrightSpeed?
            Who is the CEO of Brightspeed?
            What Internet Plan are offer by BrightSpeed?
            Display the list of products with their prices.
            """)

elif sidebar_selection == "Feedback":
    st.markdown('<div class="feedback-container">', unsafe_allow_html=True)
    with st.form(key="feedback_form", clear_on_submit= True):
        feedback = st.text_area("Please provide your feedback:", height=200)
        submit_button = st.form_submit_button("Submit")
        if submit_button:
            insert_feedback(feedback)
            st.write("Thank you for your feedback!")
    st.markdown('</div>', unsafe_allow_html=True)