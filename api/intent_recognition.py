import os
import json
from dotenv import load_dotenv
from openai_acess import OpenAIModel
from langchain_core.prompts.few_shot import FewShotPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate
from utils.prompts import intent_classification_system_prompt, intent_classification_user_prompt
load_dotenv()
from colorama import Fore

class IntentRecognizer:
    def __init__(self):
        self.model = OpenAIModel()
       


    def classify_and_translate(self, question: str) -> dict:
        """
        1) Classify the question into one of the categories:
           'exchange_regulation', 'esma', 'emir', 'csdr', or 'unknown'.
        2) Detect if the question is in Greek or English (or unknown).
        3) If Greek, translate to English; if English, translate to Greek; otherwise, 'unknown'.

        Returns a dict with:
        {
          "category": "...",
          "language": "...",
          "translation": "..."
        }
        """
        print(Fore.RED +'INTENT CLASSIFICATION INPUT')
        print(intent_classification_system_prompt + '\n' + intent_classification_user_prompt.format(question=question))
        inputs = {
            'messages': [
                {
                    "role": "system",
                    "content": intent_classification_system_prompt
                },
                {"role": "user", "content": intent_classification_user_prompt.format(question=question)}
            ],
            'params': {
                'temperature': 0.0,  # lower temperature for consistency
                'max_tokens': 200
            }
        }

        response = self.model.predict(inputs)
        raw_text = response["response"].strip()
        print()
        print(Fore.GREEN +'INTENT CLASSIFICATION OUTPUT')
        print(raw_text)
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
