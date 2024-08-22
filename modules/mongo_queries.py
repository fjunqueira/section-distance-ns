import streamlit as st
import re
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime

import requests

API_URL = "https://generative-ids-api.us-east-1.prd.cloudhumans.io/api"


# Fetch section data by section ID and project name
def get_actual_section_data(section_id, project_name):
    params = {"section_id": section_id, "project_name": project_name}
    response = requests.get(f"{API_URL}/section_data", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching section data: {response.status_code}")
        return None

# Fetch sections by section ID, start date, and end date
def get_sections_by_id(section_id, start_date, end_date):
    params = {"section_id": section_id, "start_date": start_date, "end_date": end_date}
    response = requests.get(f"{API_URL}/sections", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching sections: {response.status_code}")
        return None

# Fetch feedback sections with join
def get_feedback_sections_with_join(section_id, start_date, end_date):
    params = {"section_id": section_id, "start_date": start_date, "end_date": end_date}
    response = requests.get(f"{API_URL}/feedback_sections", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching feedback sections: {response.status_code}")
        return None