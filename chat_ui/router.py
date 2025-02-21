from openai_acess import OpenAIModel
from dotenv import load_dotenv
import json
from utils.prompts import router_prompt, persona_prompt

load_dotenv()

model = OpenAIModel()

def Router(user_query: str):
    model = OpenAIModel()
    inputs = {
        'messages': [
            {
                "role": "system",
                "content": router_prompt
            },
            {
                "role": "user",
                "content": user_query
            }
        ],
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

user_message = "What time is it?"


x = Router(user_message)

#print(x)
