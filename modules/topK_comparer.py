from modules.claudia_api import get_distances_from_api
from modules.topK_section_position import get_position_differences


def compare_negative_feedback_topK(joined_docs, section_id_input):
    results = []
    for joined_doc in joined_docs:
        feedback = joined_doc
        revision = joined_doc.get('revision_data', {})
        
        # Determine user_query based on the feedback
        user_query = feedback.get('sectionExistenceCheck', {}).get('searchSentence', '')
        if not user_query.strip():
            user_query = revision.get('response', {}).get('userQuery', '')

        active_intent = revision.get('conversation', {}).get('activeIntent', '')

        # Get distances from API
        distances_response = get_distances_from_api(user_query, active_intent)

        if distances_response is None:
            # Handle the case where the API response is None
            section_check = {
                'found_in_api': 'N/A',
                'original_position': 'N/A',
                'api_position': 'N/A',
                'position_changed': 'N/A'
            }
        else:
            section_check = get_position_differences(distances_response, revision.get('response', {}).get('sections', []), section_id_input)

        results.append({
            "Mensagem Usuário": user_query,
            "Pergunta presente após ajuste?": section_check['found_in_api'],
            "Posição topK antes do ajuste": section_check['original_position'],
            "Posição topK após ajuste": section_check['api_position'],
            "Posição mudou?": section_check['position_changed'],
            "Id Hub": revision.get('conversation', {}).get('cloudChatId', 'N/A'),
            "Resposta Claudia": revision.get('response', {}).get('rawFinalAnswer', 'N/A'),
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

            if distances_response is None:
                # Handle the case where the API response is None
                section_check = {
                    'found_in_api': 'N/A',
                    'original_position': 'N/A',
                    'api_position': 'N/A',
                    'position_changed': 'N/A'
                }
            else:
                section_check = get_position_differences(distances_response, document.get('response', {}).get('sections', []), section_id_input)

            results.append({
                "Mensagem Usuário": user_query,
                "Pergunta presente após ajuste?": section_check['found_in_api'],
                "Posição topK antes do ajuste": section_check['original_position'],
                "Posição topK após ajuste": section_check['api_position'],
                "Posição mudou?": section_check['position_changed'],
                "Id Hub": document.get('cloudChatId', 'N/A'),
                "Resposta Claudia": document.get('response', {}).get('rawFinalAnswer', 'N/A'),
                "Intent": active_intent
            })
        else:
            # Handle the case where user_query or active_intent is missing
            results.append({
                "Mensagem Usuário": user_query,
                "Pergunta presente após ajuste?": 'N/A',
                "Posição topK antes do ajuste": 'N/A',
                "Posição topK após ajuste": 'N/A',
                "Posição mudou?": 'N/A',
                "Id Hub": document.get('cloudChatId', 'N/A'),
                "Resposta Claudia": document.get('response', {}).get('rawFinalAnswer', 'N/A'),
                "Intent": active_intent
            })

    return results
