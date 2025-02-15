import os
from dotenv import load_dotenv
from openai_acess import OpenAIModel
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate


load_dotenv()

model = OpenAIModel()

## TODO: FIND QUESTIONS AND ANSWERS
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
        "question": "Ποιες είναι οι υποχρεώσεις διασποράς των εισηγμένων εταιρειών;",
        "answer": "",
    },
    {
        "question": "Θεωρείτε για ένα CSD κρίσιμη εξωτερική ανάθεση η ανάθεση του ελέγχου συμμόρφωσης συμμετεχόντων;",
        "answer": "",
    },
    {
        "question": "",
        "answer": "",
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


formatted_prompt = prompt.format(input="Whe Apostolis born?")

inputs = {
    'messages': [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": formatted_prompt}
    ],
    'params': {
        'temperature': 0.7,
        'max_tokens': 100
    }
}


response = model.predict(inputs)

print(response["response"])