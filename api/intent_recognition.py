import os
import json
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
                "question": "Είναι κρίσιμη εξωτερική ανάθεση η χρήση πλατφόρμας δέουσας επιμέλειας για τον έλεγχο συμμόρφωσης των εκκαθαριστικών μελών;",
                "answer": "exchange_regulation",
            },
            {
                "question": "Which are the free float requirements for a listed company?",
                "answer": "exchange_regulation",
            },
            {
                "question": "Θεωρείτε για ένα CSD κρίσιμη εξωτερική ανάθεση η ανάθεση του ελέγχου συμμόρφωσης συμμετεχόντων;",
                "answer": "esma",
            },
            {
                "question": "Do you consider it critical for a CCP (Cost Center Planner) to outsource the compliance audit of clearing members?",
                "answer": "esma",
            },
            {
                "question": "Μπορεί ένα CCP (Cost Center Planner) που ανήκει σε όμιλο να δανείζεται Chief Auditor από τη μητρική εταιρεία και υπό ποιες προϋποθέσεις;",
                "answer": "emir",
            },
            {
                "question": "What are the responsibilities and the reporting line of the Chief Technology Officer in a CCP?",
                "answer": "emir"
            },
            {
                "question": "Μπορεί ένα CSD που ανήκει σε όμιλο να δανείζεται Chief Auditor από τη μητρική εταιρεία και υπό ποιες προϋποθέσεις;",
                "answer": "CSDR"
            },
            {
                "question": "What information regarding the CSD's activities and services should be included in the application for authorization?",
                "answer": "CSDR"
            }
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

    def classify_and_translate(self, question: str) -> dict:
        """
        1) Classify the question into one of the categories:
           'exchange_regulation', 'esma', 'emir', 'CSDR', or 'unknown'.
        2) Detect if the question is in Greek or English (or unknown).
        3) If Greek, translate to English; if English, translate to Greek; otherwise, 'unknown'.

        Returns a dict with:
        {
          "category": "...",
          "language": "...",
          "translation": "..."
        }
        """
        formatted_prompt = self.prompt.format(input=question)
        inputs = {
            'messages': [
                {
                    "role": "system",
                    "content": (
                        "You are an assistant specialized in query classification and simple language detection.\n\n"
                        "TASK 1: Classify the user's question into: "
                        "\"exchange_regulation\", \"esma\", \"emir\", \"CSDR\", or \"unknown\" if unsure.\n\n"
                        "TASK 2: Detect if the question is in English or Greek. If not sure, return \"unknown\".\n\n"
                        "TASK 3: If the question is in Greek, translate it to English. If the question is in English, "
                        "translate it to Greek. If you are not sure or it's another language, use \"unknown\".\n\n"
                        "Output your final answer as VALID JSON in this exact format (no extra keys):\n"
                        "{\n"
                        "  \"category\": \"exchange_regulation | esma | emir | csdr | unknown\",\n"
                        "  \"language\": \"english | greek | unknown\",\n"
                        "  \"translation\": \"...\"\n"
                        "}\n"
                    )
                },
                {"role": "user", "content": formatted_prompt}
            ],
            'params': {
                'temperature': 0.0,  # lower temperature for consistency
                'max_tokens': 200
            }
        }

        response = self.model.predict(inputs)
        raw_text = response["response"].strip()

        result = {
            "category": "unknown",
            "language": "unknown",
            "translation": "unknown"
        }

        try:
            parsed = json.loads(raw_text)

            valid_categories = {"exchange_regulation", "esma", "emir", "csdr", "unknown"}
            cat = parsed.get("category", "").lower().strip()
            if cat in valid_categories:
                result["category"] = cat

            valid_languages = {"english", "greek", "unknown"}
            lang = parsed.get("language", "").lower().strip()
            if lang in valid_languages:
                result["language"] = lang

            translation = parsed.get("translation", "").strip()
            if translation:
                result["translation"] = translation

        except json.JSONDecodeError:

            pass

        return result

    def run(self):
        """Run an interactive loop for classifying user questions and translating between Greek and English."""
        print("Enter 'quit' or 'exit' to end the conversation.")
        while True:
            user_input = input("Your question: ")
            if user_input.lower() in ['quit', 'exit']:
                break
            result = self.classify_and_translate(user_input)
            print("Response:", result)


if __name__ == "__main__":
    recognizer = IntentRecognizer()
    recognizer.run()
