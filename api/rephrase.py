from utils.constants import *
from colorama import Fore
from openai_acess import OpenAIModel
import re


def rephrase(chat_history, query):
    if chat_history == []:
        return query
    # Reverse the chat history
    chat_hist_str = ''
    for idx, item in enumerate(chat_history):
        chat_hist_str += f'Previous question {str(idx + 1)}#: \n' + item['question'] + '\n' + \
                          f'Previous answer {str(idx + 1)}#: \n' + item['answer'] + '\n' + '\n'

    from utils.prompts import rephrase_system_prompt, rephrase_user_prompt
    rephrase_user_prompt = rephrase_user_prompt.format(chat_history=chat_hist_str, question=query)

    print(Fore.RED + 'REPHRASE INPUT')
    print(rephrase_system_prompt + '\n' + rephrase_user_prompt)
    
    inputs = {
        'messages': [
            {
                "role": "system",
                "content": rephrase_system_prompt
            },
            {"role": "user", "content": rephrase_user_prompt}
        ],
        'params': {
            'temperature': 0.3,  # lower temperature for consistency
            'max_tokens': 200
        }
    }
    model = OpenAIModel()
    response = model.predict(inputs)
    rephrased_question = response["response"].strip()
    match = re.search(r'<question>(.*?)</question>', rephrased_question)

    print()
    print(Fore.GREEN + 'REPHRASE OUTPUT')
    print(rephrased_question)
    print()
    print()
    print()
    if match:
        question_content = match.group(1)
        return question_content
    else:
        return query

   

        
    