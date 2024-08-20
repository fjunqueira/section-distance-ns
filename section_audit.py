import streamlit as st
import pandas as pd
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import requests

# Step 1: Connect to MongoDB
@st.cache_resource
def get_mongo_collection():
    client = MongoClient(st.secrets["connection_string"])
    db = client['claudia-db']
    return db['promptRevision']

# Function to update the section via the API
def update_section_api(section, headers):
    api_url = 'https://claudia-api.us-east-1.prd.cloudhumans.io/api/ids/entry'
    payload = {
        "id": str(section.get("_id", "not_found")),
        "title": section.get("title", ""),
        "response": section.get("response", ""),
        "content": section.get("content", ""),
        "label": section.get("tag", ""),
        "projectName": "nuvemshop",
        "createdAt": datetime.utcnow().isoformat(),
        "updatedAt": datetime.utcnow().isoformat(),
        "topic": section.get("topic", "DEFAULT"),
        "type": section.get("type", ""),
        "flowId": section.get("flowId", None),
        "createdBy": "fabio@cloudhumans.com",
        "source": "ADMIN"
    }
    response = requests.put(api_url, headers=headers, json=payload)
    return response

# Function to fetch distances from API
def get_distances_from_api(user_query, active_intent):
    api_url = "https://claudia-api.us-east-1.prd.cloudhumans.io/api/semantic-search/ids/distance"
    payload = {
        "projectName": "nuvemshop",
        "message": user_query,
        "topK": 3,
        "intent": active_intent
    }
    response = requests.post(api_url, json=payload)
    return response.json()

# Function to fetch the actual title and response from idsEntry collection
def get_actual_section_data(section_id, project_name):
    collection = get_mongo_collection().database['idsEntry']
    
    # Query to find the section by section ID and projectName
    query = {
        "_id": ObjectId(section_id),
        "projectName": project_name
    }
    # Fetch the section data
    return collection.find_one(query)

# Function to fetch all documents with the section ID in the sections list and within the date range
def get_sections_by_id(section_id, start_date, end_date):
    collection = get_mongo_collection()
    
    # Query to find documents within the date range with the specified section ID in the sections array
    query = {
        "project.name": "nuvemshop",
        "createdAt": {
            "$gte": datetime.strptime(start_date, '%Y-%m-%d'),
            "$lte": datetime.strptime(end_date, '%Y-%m-%d')
        },
        "response.sections._id": ObjectId(section_id)
    }
    projection = {"response.sections": 1, "conversation.activeIntent": 1, "response.userQuery": 1, "_id": 0}
    documents = list(collection.find(query, projection))
    return documents

# Streamlit main application
def main():
    st.title("Section Editor and Distance Checker")

    # Step 1: Input for Section ID
    if 'section_id' not in st.session_state:
        st.session_state['section_id'] = ""
    section_id_input = st.text_input("Enter Section ID:", st.session_state['section_id'])
    st.session_state['section_id'] = section_id_input

    # Step 2: Date range input
    if 'start_date' not in st.session_state:
        st.session_state['start_date'] = datetime.now()
    if 'end_date' not in st.session_state:
        st.session_state['end_date'] = datetime.now()

    start_date = st.date_input("Start Date", st.session_state['start_date'])
    end_date = st.date_input("End Date", st.session_state['end_date'])
    st.session_state['start_date'] = start_date
    st.session_state['end_date'] = end_date

    # Step 3: Input JWT token
    if 'jwt_token' not in st.session_state:
        st.session_state['jwt_token'] = ""
    jwt_token = st.text_input("Enter JWT Token:", st.session_state['jwt_token'], type="password")
    st.session_state['jwt_token'] = jwt_token

    # Initialize session state for title and response
    if "title" not in st.session_state:
        st.session_state['title'] = ""
    if "response" not in st.session_state:
        st.session_state['response'] = ""

    if st.button("Fetch Sections"):
        try:
            section_id = ObjectId(section_id_input)

            # Fetch actual title and response from the idsEntry collection
            section = get_actual_section_data(str(section_id), "nuvemshop")

            if section:
                st.session_state['section'] = section

                # Store section_id, start_date, and end_date in session state
                st.session_state['section_id'] = section_id_input
                st.session_state['start_date'] = start_date
                st.session_state['end_date'] = end_date

                # Update session state with fetched values
                st.session_state['title'] = section['title']
                st.session_state['response'] = section['response']

            else:
                st.warning(f"No section found with ID: {section_id_input}")

        except Exception as e:
            st.error(f"Error: {e}")

    # Step 4: Show the inputs for title and response
    st.subheader("Edit Section Fields")
    section_title = st.text_input("Title", value=st.session_state['title'])
    section_response = st.text_area("Response", value=st.session_state['response'])

    # Store updated values in session state
    st.session_state['title'] = section_title
    st.session_state['response'] = section_response

    # Step 5: Submit updated fields and update section
    if 'section' in st.session_state and st.button("Update Section and Fetch Distances"):
        updated_section = st.session_state['section']
        updated_section['title'] = st.session_state['title']
        updated_section['response'] = st.session_state['response']

        # Headers for the PUT request (use the input JWT token here)
        headers = {
            'authorization': f'Bearer {jwt_token}',  # Use the input JWT token
            'content-type': 'application/json'
        }

        # Step 4a: Update the section via the API
        response = update_section_api(updated_section, headers)
        if response.status_code == 200:
            st.success("Section updated successfully!")
        else:
            st.error(f"Failed to update section. Status code: {response.status_code}, Response: {response.text}")
            return

        # Step 4b: Fetch distances for all userQueries returned by get_sections_by_id
        documents = get_sections_by_id(
            str(st.session_state['section_id']), 
            str(st.session_state['start_date']), 
            str(st.session_state['end_date'])
        )

        if not documents:
            st.error("Documents not found in session. Please re-fetch sections.")
            return

        results = []
        for document in documents:
            user_query = document.get("response", {}).get("userQuery", "")
            active_intent = document.get("conversation", {}).get("activeIntent", "")

            if user_query and active_intent:
                distances_response = get_distances_from_api(user_query, active_intent)

                # Check the section position in the response and original
                section_check = check_section_position(distances_response, document['response']['sections'], st.session_state['section_id'])
                
                # Store the result for this iteration
                results.append({
                    "userQuery": user_query,
                    "activeIntent": active_intent,
                    "found_in_api": section_check['found_in_api'],
                    "api_position": section_check['api_position'],
                    "found_in_original": section_check['found_in_original'],
                    "original_position": section_check['original_position'],
                    "position_changed": section_check['position_changed']
                })

        # Convert the results into a DataFrame for easier analysis
        result_df = pd.DataFrame(results)

        # Display the results to the user
        st.dataframe(result_df)


# Helper function to check section position in API response
def check_section_position(api_response, original_sections, section_id_input):
    section_positions = {}

    # Check if section exists in API response
    found_in_api = False
    api_position = None
    for i, result in enumerate(api_response):
        if section_id_input in result['id']:
            found_in_api = True
            api_position = i
            break

    # Check original position
    found_in_original = False
    original_position = None
    for i, section in enumerate(original_sections):
        if str(section['_id']) == section_id_input:
            found_in_original = True
            original_position = i
            break

    section_positions['found_in_api'] = found_in_api
    section_positions['api_position'] = api_position
    section_positions['found_in_original'] = found_in_original
    section_positions['original_position'] = original_position
    section_positions['position_changed'] = found_in_api and found_in_original and api_position != original_position

    return section_positions


if __name__ == "__main__":
    main()
