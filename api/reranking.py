from retrieval import Retrieval
import os
from utils.prompts import rerank_system_prompt, rerank_user_prompt
from openai import AsyncAzureOpenAI
import asyncio
import re
import os
from dotenv import load_dotenv
from utils.constants import *
from colorama import Fore
load_dotenv()

def rerank(retrieved_results):
  
    OPENAI_API_URL
    client = AsyncAzureOpenAI(
                azure_endpoint=OPENAI_API_URL,
                api_key=OPENAI_API_KEY,
                api_version=OPENAI_API_VERSION
            )
    
    async def _call_azure_openai_async(prompt):
        try:
            response = await client.chat.completions.create(
                model=OPENAI_MODEL_NAME,
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
        
        print(Fore.RED +'RERANKING INPUT')
        print(rerank_system_prompt + rerank_user_prompt.format(query=query, documents=doc_string))
        print()
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
    if len(responses)==0:
        print()
        print()
        print(Fore.RED +'RERANKING OPENAI EMPTY LIST')
        print()
        print()
        return []
    if missing[0]:
        responses = [None,responses[0]]
        print()
        print(Fore.GREEN +'RERANKING OUTPUT')
        print(responses[1])
        print('-'*100)
    elif missing[1]:
        responses.append(None)
    else:
        print()
        print(Fore.GREEN +'RERANKING OUTPUT')
        for r in responses:
            print(r)
            print()
            print('-'*100)
        
    threshold = 6
    all_chunks = []
    all_chunks_back_up = []
    for i, response in enumerate(responses):
        if not response:
            continue
        match = re.search(r'<result>(.*?)<\/result>', response)
        if match:
            ranked_results_idx = eval(match.group(1))  # Convert string to list
            print(ranked_results_idx, len(retrieved_results[i]["chunks"]))

            all_chunks_tmp = []
            all_chunks_tmp_back_up = []
            for idx, score in enumerate(ranked_results_idx):
                # for back up 
                if score >= 4 and len(retrieved_results[i]["chunks"]) > 0:
                    chunk = retrieved_results[i]['chunks'][idx]
                    chunk["reranked_score"] = score  # Store reranked score in chunk
                    all_chunks_tmp_back_up.append(chunk) 

                # og
                if score >= threshold and len(retrieved_results[i]["chunks"]) > 0:
                    chunk = retrieved_results[i]['chunks'][idx]
                    chunk["reranked_score"] = score  # Store reranked score in chunk
                    all_chunks_tmp.append(chunk)        
            
            all_chunks += all_chunks_tmp
            all_chunks_back_up += all_chunks_tmp_back_up

    
    if len(all_chunks) == 0:
        print("Using chunks with score >= 4")
        all_chunks = all_chunks_back_up
    # print reranked chunks with rerank score
    all_chunks.sort(key=lambda x: x["reranked_score"], reverse=True)
    print(Fore.BLUE +'RERANKED CHUNKS')
    for chunk in all_chunks:
        print(chunk['pdf_name'], chunk['pg_number'], chunk['reranked_score'])
    return all_chunks

if __name__ == '__main__':
    emb_url = os.getenv('EMBEDDING_URL')
    db_url = os.getenv('DB_URL')

    retrieval_obj = Retrieval(10, english_query="ensure that investors' rights are protected", greek_query='Ποια ειναι η Διαδικασία για την απόκτηση της ιδιότητας του Μέλους', 
                            category='esma', embedding_url=emb_url, db_url=db_url)
    
    retrieved_results = retrieval_obj.retrieve()
    all_chunks = rerank(retrieved_results)
    # print(all_chunks[0]['document'], all_chunks[0]['pdf_name'])
    # print('*=*' * 1000)
    # print(all_chunks[0]['img'])
    # print('*=*' * 1000)