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


def get_distances_from_api(user_query, active_intent):
    api_url = "https://claudia-api.us-east-1.prd.cloudhumans.io/api/semantic-search/ids/distance"
    payload = {
        "projectName": "nuvemshop",
        "message": user_query,
        "topK": 5,
        "intent": active_intent
    }
    
    # Print the request parameters for debugging
    print("Request URL:", api_url)
    print("Request Payload:", payload)
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)
        
        # Print the raw response content for debugging
        print("Response Status Code:", response.status_code)
        print("Response Content:", response.text)
        
        try:
            data = response.json()
            return data
        except ValueError as e:
            print(f"JSON deserialization failed: {e}")
            return None
    
    except requests.exceptions.RequestException as e:
        # Log the request exception details
        print(f"Request failed: {e}")
        
        # Print the response content if available
        if e.response is not None:
            print("Failed Response Status Code:", e.response.status_code)
            print("Failed Response Content:", e.response.text)
        
        return None

