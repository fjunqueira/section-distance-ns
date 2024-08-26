from modules.claudia_api import get_distances_from_api
from modules.topK_section_position import get_position_differences


def compare_negative_feedback_topK(joined_docs, section_id_input):
    results = []
    for joined_doc in joined_docs:
        feedback = joined_doc
        revision = joined_doc['revision_data']
        user_query = revision['response']['userQuery']
        active_intent = revision.get('conversation', {}).get('activeIntent', "")
        distances_response = get_distances_from_api(user_query, active_intent)
        section_check = get_position_differences(distances_response, revision['response']['sections'], section_id_input)

        results.append({
            "Mensagem Usuário": user_query,
            "Pergunta presente após ajuste?": section_check['found_in_api'],
            "Posição topK antes do ajuste": section_check['original_position'],
            "Posição topK após ajuste": section_check['api_position'],
            "Posição mudou?": section_check['position_changed'],
            "Id Hub": revision['conversation']['cloudChatId'],
            "Resposta Claudia": revision['response']['rawFinalAnswer'],
            "Intent": active_intent
        })
    return results

def compare_past_conversations_topK(documents, section_id_input):
    results = []
    for document in documents:
        user_query = document.get("response", {}).get("userQuery", "")
        active_intent = document.get("conversation", {}).get("activeIntent", "")
        
        if user_query and active_intent:
            distances_response = get_distances_from_api(user_query, active_intent)
            section_check = get_position_differences(distances_response, document['response']['sections'], section_id_input)
            print(document)
            results.append({
                "Mensagem Usuário": user_query,
                "Pergunta presente após ajuste?": section_check['found_in_api'],
                "Posição topK antes do ajuste": section_check['original_position'],
                "Posição topK após ajuste": section_check['api_position'],
                "Posição mudou?": section_check['position_changed'],
                "Id Hub": document['cloudChatId'],
                "Resposta Claudia": document['response']['rawFinalAnswer'],
                "Intent": active_intent
            })
    return results
