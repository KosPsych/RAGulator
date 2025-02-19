from retrieval import Retrieval
import os
from utils.prompts import rerank_system_prompt, rerank_user_prompt
from openai import AsyncAzureOpenAI
import asyncio
import re
import os
from dotenv import load_dotenv

load_dotenv()

def rerank(retrieved_results):
    client = AsyncAzureOpenAI(
                azure_endpoint=os.environ.get('OPENAI_API_URL'),
                api_key=os.environ.get('OPENAI_API_KEY'),
                api_version=os.environ.get('OPENAI_API_VERSION')
            )
    
    async def _call_azure_openai_async(prompt):
        try:
            response = await client.chat.completions.create(
                model=os.environ.get('OPENAI_MODEL_NAME'),
                messages=prompt['messages'],
                **prompt['params']
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    async def run_concurrent_calls():
        return await asyncio.gather(
            *[_call_azure_openai_async(prompt) for prompt in all_prompts]
        )
    
    all_prompts = []
    missing={0:False,1:False}
    for idx, res in enumerate(retrieved_results):
        if len(res['chunks']) == 0:
            missing[idx] = True
            continue
        query = res['query']
        doc_string = "".join(f"<document-{idx}>\n" + document['document'] + f"</document-{idx}>\n" for idx, document in enumerate(res['chunks']))

        inputs = {
            'messages': [
            {"role": "system", "content": rerank_system_prompt},
            {"role": "user", "content": rerank_user_prompt.format(query=query, documents=doc_string)},
            ],
            'params': {
            'temperature': 0
            }
        }
        all_prompts.append(inputs)

    responses = asyncio.run(run_concurrent_calls())
    if missing[0]:
        responses = [None,responses[0]]
    elif missing[1]:
        responses.append(None)
        
    threshold = 6
    all_chunks = []
    for i, response in enumerate(responses):
        if not response:
            continue
        match = re.search(r'<result>(.*?)<\/result>', response)
        match = match.group(1)
        ranked_results_idx = eval(match)
        print(ranked_results_idx, len(retrieved_results[i]["chunks"]))
        all_chunks_tmp = [retrieved_results[i]['chunks'][idx] for idx, k in enumerate(ranked_results_idx) if k >= threshold and len(retrieved_results[i]["chunks"])>0]
        all_chunks += all_chunks_tmp

    return all_chunks

if __name__ == '__main__':
    emb_url = os.getenv('EMBEDDING_URL')
    db_url = os.getenv('DB_URL')

    retrieval_obj = Retrieval(10, english_query="ensure that investors' rights are protected", greek_query='Ποια ειναι η Διαδικασία για την απόκτηση της ιδιότητας του Μέλους', 
                            category='legal', embedding_url=emb_url, db_url=db_url)
    
    retrieved_results = retrieval_obj.retrieve()
    all_chunks = rerank(retrieved_results)
    print(all_chunks[0]['document'], all_chunks[0]['pdf_name'])
    print('*=*' * 1000)
    print(all_chunks[0]['img'])
    print('*=*' * 1000)