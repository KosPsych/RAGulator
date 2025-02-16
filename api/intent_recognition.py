import os
from dotenv import load_dotenv
from openai_acess import OpenAIModel
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate

load_dotenv()

class IntentRecognizer:
    def __init__(self):
        self.model = OpenAIModel()
        self.examples = [
            {
                "question": "Είναι κρίσιμη εξωτερική ανάθεση η χρήση πλατφόρμας δέουσας επιμέλειας για τον έλεγχο συμμόρφωσης των εκκαθαριστικών μελών?",
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

        self.example_prompt = PromptTemplate(
            input_variables=["question", "answer"],
            template="Question: {question}\nAnswer: {answer}\n"
        )

        self.prompt = FewShotPromptTemplate(
            examples=self.examples,
            example_prompt=self.example_prompt,
            suffix="Question: {input}\nAnswer:",
            input_variables=["input"],
        )

        print("Example Prompt:")
        print(self.example_prompt.format(**self.examples[0]))

    def classify(self, question: str) -> str:
        """Classify a single question as 'IT' or 'Legal'."""
        formatted_prompt = self.prompt.format(input=question)
        inputs = {
            'messages': [
                {
                    "role": "system",
                    "content": (
                        "You are an assistant specialized in query classification. "
                        "When you receive a user query, analyze its content and determine whether it relates to "
                        "\"IT\" (Information Technology) or \"Legal\" (Legal and Compliance). "
                        "Your response should be a single word: either \"IT\" or \"Legal\". Do not include any additional commentary."
                    )
                },
                {"role": "user", "content": formatted_prompt}
            ],
            'params': {
                'temperature': 0.7,
                'max_tokens': 100
            }
        }
        response = self.model.predict(inputs)
        return response["response"]

    def run(self):
        """Run an interactive loop for classifying user questions."""
        print("Enter 'quit' or 'exit' to end the conversation.")
        while True:
            user_input = input("Your question: ")
            if user_input.lower() in ['quit', 'exit']:
                break
            result = self.classify(user_input)
            print("Response:", result)


if __name__ == "__main__":
    recognizer = IntentRecognizer()
    recognizer.run()
