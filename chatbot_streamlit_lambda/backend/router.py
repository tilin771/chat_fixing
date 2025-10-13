from services.query_kb import consultar_kb_streaming


def handle_action(decision_json, user_input):
    action = decision_json["action"]
    if action == "query_kb":
        return consultar_kb_streaming(user_input)
    
