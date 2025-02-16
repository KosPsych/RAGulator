from dotenv import load_dotenv
load_dotenv() 

from intent_recognition import IntentRecognizer
from rag_system import RAGSystem

def main():
    print("Starting the combined system (Intent Recognition + RAG System)")
    
    intent_recognizer = IntentRecognizer()
    rag_system = RAGSystem()
    session_id = rag_system.create_session()

    print("\nEnter 'quit' or 'exit' to stop.")
    
    while True:
        user_query = input("\nEnter your query: ")
        if user_query.lower() in ["quit", "exit"]:
            break

        classification = intent_recognizer.classify(user_query)
        print(f"Intent Classification: {classification}")

        answer, sources = rag_system.rag_query(user_query, session_id)
        print("RAG System Answer:", answer)
        if sources:
            print("Sources:", sources)
        else:
            print("No sources found.")

if __name__ == '__main__':
    main()
