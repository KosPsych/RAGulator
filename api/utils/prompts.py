####################################################### Reranking #######################################################
rerank_system_prompt = '''You are Rank-GPT, an intelligent assistant that can rank documents based on their relevancy to the query.
Given a query and some documents, each indicated by number identifier, your task is provide a score from 0 to 10 which measures how relevant you think the documents are to the question.
Follow all the steps mentioned below:

Steps:
1. Iterate through each document and identify if it is relevant to the query.
2. Assign a score from 0 to 10 based on how relevant is the document to the query, where 0 indicates that the document is completely irrelevant and 10 the document is highly relevant.
3. If a document provides only general information about the topic, such as cover pages, tables of contents, or introductory sections it is completely irrelevant.
'''

rerank_user_prompt = """
Query:
{query}

Documents:
{documents}

Think this through step by step.

At the end of your response you should provide a list of scores contained in <result> </result> tags, where the index of each score is the number of the document. For example the list <result>[5, 1, 10]</result> means that 3 documents were provided with scores 5, 1 and 10 respectively.
"""

####################################################### Final Generation #######################################################

generation_prompt = """Along with each source, you will be provided with the filename and the pages of the source.
When responding, do not just reference specific pages and sources; instead, include relevant content from those sources directly in your response. This ensures a comprehensive and informative answer.
If the question cannot be answered completely based on the context, answer based on the information provided in the context without mentioning that the answer is incomplete.
When the context information is present in a different format than requested, answer based on the information provided in the context, do not give so much emphasis on the format.
If the context is empty answer that there is no relevant information in the database.
The question may reference a specific source but this source is different from the context sources and you should not pay attention to it, just answer based on the context.
Context: 
{context}

Question: {question}
Answer:"""

####################################################### Intent Classification #######################################################

# put your '#' separated prompt here for intent classification