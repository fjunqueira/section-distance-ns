def get_position_differences(api_response, original_sections, section_id_input):
    section_positions = {}
    found_in_api = False
    api_position = None
    for i, result in enumerate(api_response):
        if section_id_input in result['id']:
            found_in_api = True
            api_position = i
            break

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
