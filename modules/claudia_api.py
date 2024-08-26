from datetime import datetime
import requests

def update_section_api(section, headers):
    api_url = 'https://claudia-api.us-east-1.prd.cloudhumans.io/api/ids/entry'
    payload = {
        "id": str(section.get("_id", "not_found")),
        "title": section.get("title", ""),
        "response": section.get("response", ""),
        "content": section.get("content", ""),
        "label": section.get("label", ""),
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
import requests

def get_distances_from_api(user_query, active_intent):
    api_url = "https://claudia-api.us-east-1.prd.cloudhumans.io/api/semantic-search/ids/distance"
    payload = {
        "projectName": "nuvemshop",
        "message": user_query,
        "topK": 5,
        "intent": active_intent
    }
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

    try:
        # Print the raw response content for debugging
        print("Response content:", response.text)
        data = response.json()
    except ValueError as e:
        print(f"JSON deserialization failed: {e}")
        return None

    return data

