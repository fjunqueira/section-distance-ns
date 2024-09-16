import streamlit as st
import pandas as pd
from modules.claudia_api import update_section_api
from modules.mongo_queries import get_actual_section_data, get_sections_by_id, get_feedback_sections_with_join
from modules.topK_comparer import compare_past_conversations_topK, compare_negative_feedback_topK
from modules.metabase_api import embed_metabase_question
from bson import ObjectId
from datetime import datetime, timedelta

# Streamlit main application
def main():
    st.title("Section Editor and Distance Checker")
    
    embed_metabase_question()

    # Step 1: Input for Section ID
    if 'section_id' not in st.session_state:
        st.session_state['section_id'] = ""
    section_id_input = st.text_input("Enter Section ID:", st.session_state['section_id'])
    st.session_state['section_id'] = section_id_input

    # Step 2: Input JWT token
    jwt_token = st.secrets["JWT_TOKEN"]
    st.session_state['jwt_token'] = jwt_token

    if st.button("Fetch Section"):
        try:
            section_id = ObjectId(section_id_input)
            section = get_actual_section_data(str(section_id), "nuvemshopar")

            if section:
                st.session_state['section'] = section
                st.session_state['title'] = section['title']
                st.session_state['response'] = section['response']
            else:
                st.warning(f"No section found with ID: {section_id_input}")

        except Exception as e:
            st.error(f"Error: {e}")

    # Step 3: Show the inputs for title and response
    section_title = st.text_input("Title", value=st.session_state.get('title', ''))
    section_response = st.text_area("Response", value=st.session_state.get('response', ''))

    st.session_state['title'] = section_title
    st.session_state['response'] = section_response

    # Step 4: Submit updated fields and update section
    if 'section' in st.session_state and st.button("Update Section"):
        updated_section = st.session_state['section']
        updated_section['title'] = st.session_state['title']
        updated_section['response'] = st.session_state['response']

        headers = {'authorization': f'Bearer {jwt_token}', 'content-type': 'application/json'}
        response = update_section_api(updated_section, headers)

        if response.status_code == 200:
            st.success("Section updated successfully!")
        else:
            st.error(f"Failed to update section. Status code: {response.status_code}, Response: {response.text}")
    
    # Step 5: Always display date inputs for fetching distances
    if 'start_date' not in st.session_state:
        st.session_state['start_date'] = datetime.now() - timedelta(days=1)
    if 'end_date' not in st.session_state:
        st.session_state['end_date'] = datetime.now()

    start_date = st.date_input("Start Date", st.session_state['start_date'])
    end_date = st.date_input("End Date", st.session_state['end_date'])
    st.session_state['start_date'] = start_date
    st.session_state['end_date'] = end_date

    # Step 6: Fetch Distances button
    if st.button("Fetch Distances"):
        # Fetch feedback sections and display
        feedback_docs = get_feedback_sections_with_join(str(st.session_state['section_id']), start_date, end_date)
        if feedback_docs:
            processed_results = compare_negative_feedback_topK(feedback_docs, str(st.session_state['section_id']))
            feedback_result_df = pd.DataFrame(processed_results)
            st.subheader("Feedbacks Negativos")
            st.dataframe(feedback_result_df)
            
        # Fetch distances
        documents = get_sections_by_id(str(st.session_state['section_id']), str(start_date), str(end_date))

        # Use the refactored function to process documents
        results = compare_past_conversations_topK(documents, st.session_state['section_id'])

        # Convert the results into a DataFrame for easier analysis
        result_df = pd.DataFrame(results)
        st.subheader("Mensagens que retornaram a sessão")
        st.dataframe(result_df)

if __name__ == "__main__":
    main()
