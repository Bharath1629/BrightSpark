from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime, time, date
import streamlit as st

credentials = service_account.Credentials.from_service_account_file('./chat-bot-414415-02b2c04511bf.json')

project_id = 'chat-bot-414415'
client = bigquery.Client(credentials=credentials,project=project_id,location="northamerica-northeast1")

# Function to insert data into BigQuery table
def insert_into_bigquery(table_name, data):
    columns = ', '.join(data.keys())
    values = ', '.join([f"'{value}'" for value in data.values()])
    query = f'INSERT INTO `{project_id}.chat_bot.{table_name}` ({columns}) VALUES ({values})'

    try:
        query_job = client.query(query)
        query_job.result()
        st.write("Thank You for contacting us. We will reach back ASAP!")
    except Exception as e:
        st.error(f"Error inserting data into BigQuery table {table_name}: {str(e)}")



# Function to extract form data and insert it into BigQuery table
def process_form_and_insert_data(form_data, form_type):
    if form_type == "schedule_installation_time":
        data = {
            "first_name": form_data["first_name"],
            "last_name": form_data["last_name"],
            "email": form_data["email"],
            "home_address": form_data["home_address"],
            "city": form_data["city"],
            "state": form_data["state"],
            "zipcode" : form_data["zipcode"],
            "appointment_date": form_data["appointment_date"].strftime("%Y-%m-%d"),
            "selected_time_slot": form_data["selected_time_slot"]
        }

        insert_into_bigquery("installation_schedule", data)
    elif form_type == "submit_ticket":
        data = {
            "business_type": form_data["business_type"],
            "issue": form_data["issue"],
            "first_name": form_data["first_name"],
            "last_name": form_data["last_name"],
            "email": form_data["email"],
            "description": form_data["description"]
        }

        insert_into_bigquery("tickets", data)

def insert_feedback(feedback):
    try:
        table_id = "chat-bot-414415.chat_bot.feedback"
        query = f"""
            INSERT INTO `{table_id}` (feedback)
            VALUES (@feedback)
        """
        # Define query parameters
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("feedback", "STRING", feedback)
            ]
        )

        # Execute the query
        query_job = client.query(query, job_config=job_config)
        query_job.result()
        return True
    except Exception as e:
        st.error(f"Error inserting feedback into BigQuery: {str(e)}")
        return False