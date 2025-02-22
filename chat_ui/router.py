from openai_acess import OpenAIModel
from dotenv import load_dotenv
import json
from utils.prompts import router_prompt, persona_prompt

load_dotenv()

model = OpenAIModel()

def Router(user_query: str, history):
    model = OpenAIModel()

    messages = [
            {
                "role": "system",
                "content": router_prompt
            }]

    if history:
            # Convert chat history to the format expected by OpenAI
        for chat in history:
            messages.append({"role": "user", "content": chat["query"]})
            messages.append({"role": "assistant", "content": chat["response"]})

    messages.append({
                "role": "user",
                "content": user_query
            })
    
    inputs = {
        'messages': messages,
        'params': {
            'temperature': 0.0,
            'max_tokens': 200
        }
    }
    
    response = model.predict(inputs)

    formated_response= json.loads(response["response"])

    print(formated_response)

    if formated_response["mode"]=='relevant':
        return [False, persona_prompt, user_query] 
    else:
        return [True, None, None]

# user_message = "What time is it?"


# x = Router(user_message)

#print(x)
