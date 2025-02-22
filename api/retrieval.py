import json
import requests
import concurrent.futures
from colorama import Fore

class Retrieval():
    def __init__(self, top_k, english_query, greek_query, category, embedding_url, db_url):
        """
        Initialize the Retrieval class with search parameters and endpoints.
        
        Args:
            top_k (int): Number of results to return
            english_query (str): Query text in English
            greek_query (str): Query text in Greek
            category (str): Category to filter results
            embedding_url (str): URL for the embedding model API
            db_url (str): URL for the database API
        """
        self.top_k = top_k
        self.english_query = english_query
        self.greek_query = greek_query
        self.category = category
        self.db_url = db_url
        self.embedding_url = embedding_url


    def get_embedding(self, text: str):
        """
        Send a request to the deployed embedding model to get the embedding.
        The endpoint expects a payload in the form: {'text': ['your text']}
        """
        url = self.embedding_url
        payload = {"text": [text]}
    
        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
    
        if result is None:
            raise ValueError("No embedding returned from the deployed model.")

        if result is None:
            raise ValueError("No embedding found in the response.")
        return result

    def embedding_retrieval(self, lang="en"):
        """
        Retrieve chunks using embedding-based similarity search.
        
        Args:
            lang (str): Language code ("en" for English, "gr" for Greek)
            
        Returns:
            list: Retrieved document chunks with similarity scores
        """
        emb = self.get_embedding(self.english_query)[0]
        
        # Base query to find chunks and calculate cosine similarity
        query_string_part1 = '''MATCH (d:Document)-[:CONTAINS]->(c:Chunk)
        WHERE c.embedding IS NOT NULL
        WITH c, d, gds.similarity.cosine(c.embedding, $embedding) AS score \n'''
        
        # Add filter based on category
        if self.category != 'unknown':
            where_clause = f''' WHERE d.tag = "{self.category}" AND d.language = "{lang}"'''
        else:
            where_clause = f''' WHERE d.language = "{lang}"'''
            
        query_string = query_string_part1 + where_clause
        
        # Order results and apply limit
        query_string_part2 = '''
        ORDER BY score DESC
        WITH score, COLLECT(DISTINCT {text: c.text, page: c.page, base64: c.base64, name: d.name}) AS chunks
        UNWIND chunks AS chunk
        RETURN chunk.text AS text, chunk.page AS page, chunk.base64 AS base64, chunk.name AS name, score
        LIMIT <top_k>
        '''.replace('<top_k>', str(self.top_k))
        
        query_string += query_string_part2
        
        # Make API request
        url = self.db_url + "/get_chunks"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "query_string": query_string,
            "embedding": emb
        }
    
        response = requests.get(url, headers=headers, json=data)
      
        return json.loads(response.text)
        

    
    def keyword_retieval(self, query, lang="en"):
        """
        Retrieve chunks using keyword-based search.
        
        Args:
            query (str): Keywords to search for
            lang (str): Language code ("en" for English, "gr" for Greek)
            
        Returns:
            list: Retrieved document chunks with relevance scores
        """
        # Base query using fulltext index
        query_string_part1 = '''CALL db.index.fulltext.queryNodes("keyword_search", $query) YIELD node, score
        MATCH (d:Document)-[:CONTAINS]->(node:Chunk)\n'''
        
        # Add filter based on category
        if self.category != 'unknown':
            where_clause = f'''WHERE d.tag = "{self.category}" AND d.language = "{lang}"'''
        else:
            where_clause = f'''WHERE d.language = "{lang}"'''
            
        query_string = query_string_part1 + where_clause
        
        # Order results and apply limit
        query_string_part3 = '''
        WITH score, COLLECT(DISTINCT {text: node.text, page: node.page, base64: node.base64, name: d.name}) AS chunks
        ORDER BY score DESC
        UNWIND chunks AS chunk
        RETURN chunk.text AS text, chunk.page AS page, chunk.base64 AS base64, chunk.name AS name, score
        LIMIT <top_k>'''.replace('<top_k>', str(self.top_k))
        
        query_string += query_string_part3
        
        # Make API request
        url = self.db_url + "/keyword_search"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "query_string": query_string,
            "query": query
        }

        response = requests.get(url, headers=headers, json=data)

        return json.loads(response.text)
    
    

    def retrieve(self):
        """
        Retrieve document chunks using both keyword-based and embedding-based methods,
        for both Greek and English languages, running requests in parallel.
        
        Returns:
            list: Combined list of retrieved document chunks
        """
        # Define functions to execute concurrently
        def get_greek_chunks():
            return self.keyword_retieval(lang="gr", query=self.greek_query)
        
        def get_english_keyword_chunks():
            return self.keyword_retieval(lang="en", query=self.english_query)
        
        def get_english_embedding_chunks():
            return self.embedding_retrieval(lang="en")
        
        # Execute all requests in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_greek = executor.submit(get_greek_chunks)
            future_english_keyword = executor.submit(get_english_keyword_chunks)
            future_english_embedding = executor.submit(get_english_embedding_chunks)
            
            # Wait for all tasks to complete and get results
            greek_chunks = future_greek.result()
            english_keyword_chunks = future_english_keyword.result()
            english_embedding_chunks = future_english_embedding.result()
        
       
       
        greek_chunks = [{'document': result[0], 'pg_number': result[1], 'pdf_name': result[2], 'img': result[3], 'score': result[4]} for result in greek_chunks]
        deduplicated = {result[0]: [result[1], result[2], result[3], result[4]] for result in english_keyword_chunks}
        for result in english_embedding_chunks:
            deduplicated[result[0]] = [result[1], result[2], result[3], result[4]]

        english_chunks = [{'document': key, 'pg_number': result[0], 'pdf_name': result[1], 'img': result[2], 'score': result[3]} for key, result in deduplicated.items()]

        
        
        result_dict = [
            {"query":self.greek_query, "chunks": greek_chunks},
            {"query":self.english_query, "chunks": english_chunks}
        ]
        
        print(Fore.BLUE +'ENGLISH CHUNKS')
        for chunk in english_chunks:
            print(chunk['pdf_name'], chunk['pg_number'], chunk['score'])
        print('-'*30)
        print(Fore.BLUE +'GREEK CHUNKS')
        for chunk in greek_chunks:
            print(chunk['pdf_name'], chunk['pg_number'], chunk['score'])
        print('-'*30)
        return result_dict


