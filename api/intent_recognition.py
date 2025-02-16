import os
from dotenv import load_dotenv
from openai_acess import OpenAIModel
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate

load_dotenv()

model = OpenAIModel()

examples = [
    {
        "question": "Είναι κρίσιμη εξωτερική ανάθεση η χρήση πλατφόρμας δέουσας επιμέλειας για τον έλεγχο συμμόρφωσης των εκκαθαριστικών μελών;",
        "answer": "Legal",
    },
    {
        "question": "Which are the free float requirements for a listed company?",
        "answer": "Legal",
    },
    {
        "question": "What happens when a company’s free float falls below 10% and dispersed among less than 30 shareholders?",
        "answer": "Legal",
    },
    {
        "question": "Απο πού μπορεί να προμηθευτεί ένας νέος υπάλληλος εταιρικό εξοπλισμό",
        "answer": "IT",
    },
    {
        "question": "When a employee can take personal leave?",
        "answer": "IT",
    },
]

example_prompt = PromptTemplate(
    input_variables=["question", "answer"],
    template="Question: {question}\nAnswer: {answer}\n"
)

print("Example Prompt:")
print(example_prompt.format(**examples[0]))

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    suffix="Question: {input}\nAnswer:",
    input_variables=["input"],
)

print("Enter 'quit' or 'exit' to end the conversation.")

while True:
    user_input = input("Your question: ")
    if user_input.lower() in ['quit', 'exit']:
        break
    formatted_prompt = prompt.format(input=user_input)
    inputs = {
        'messages': [
            {"role": "system", "content": """"You are an assistant specialized in query classification.
             When you receive a user query, analyze its content and determine whether it relates to "IT" (Information Technology) or "Legal" (Legal and Compliance).
             Your response should be a single word: either "IT" or "Legal". Do not include any additional commentary."""
            },
            {"role": "user", "content": formatted_prompt}
        ],
        'params': {
            'temperature': 0.7,
            'max_tokens': 100
        }
    }
    response = model.predict(inputs)
    print("Response:", response["response"])
