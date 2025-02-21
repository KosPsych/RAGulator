import openai

class OpenAIModel:

  def __init__(self, help=False):

    if help:
      print("Before running the 'predict' method, please configure env variables with the following keys:")
      print("'OPENAI_MODEL_NAME', 'OPENAI_API_TYPE', 'OPENAI_API_KEY', 'OPENAI_API_URL', OPENAI_API_VERSION")

      print("\n\nThe input to the predict method should have the following structure:")
      print("""inputs = {
            'messages': list of openai messages (with roles etc.),
            'params': {
              openai api params like temperature, max_tokens etc.
            }
          }""")
      
      print("Here is an input example:")
      print("""inputs = {
    'messages': [
      {"role": "system", "content": "You are a helpful assistant that always responds in json."},
      {"role": "user", "content": "Tell me a joke."},
      ],
    'params': {
      'temperature': 0.01,
      'max_tokens': 100
    }
  }""")
      
  def get_azure_openai(self):
    from openai import AzureOpenAI
    import os

    return AzureOpenAI(
      azure_endpoint=os.environ.get('OPENAI_API_URL'),
      api_key=os.environ.get('OPENAI_API_KEY'),
      api_version=os.environ.get('OPENAI_API_VERSION')
    )


  def predict(self, inputs):
    import openai
    import os

    if openai.__version__ > '0.28.1':
      # from openai import AzureOpenAI
      azure_client = self.get_azure_openai()
    else:
      import openai as ai
      assert isinstance(inputs['messages'], list), f"Variable {inputs} must be of type 'list'"

      scope_var = os.getenv("scope")
  
      ai.api_type = os.environ.get('OPENAI_API_TYPE')
      ai.api_key =  os.environ.get('OPENAI_API_KEY')
      ai.api_base = os.environ.get('OPENAI_API_URL')
      ai.api_version = os.environ.get('OPENAI_API_VERSION')

    try:
      if openai.__version__ > '0.28.1':
        response = azure_client.chat.completions.create(
            model=os.environ.get('OPENAI_MODEL_NAME'),
            messages=inputs['messages'],
            **inputs['params']
        )
      else:
        response = ai.ChatCompletion.create(
          engine=os.environ.get('OPENAI_MODEL_NAME'),
          messages=inputs['messages'],
          **inputs['params']
        )
    
      return {"response":response.choices[0].message.content, "input_tokens": response.usage.prompt_tokens, "output_tokens":response.usage.completion_tokens, "raw_response": response}
    
    except Exception as e:
      print(f"An error occurred: {e}")  # Print the error message if an exception is caught
      return {"response":'ERROR', "input_tokens":0, "output_tokens":0}