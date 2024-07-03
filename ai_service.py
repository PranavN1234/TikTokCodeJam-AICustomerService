from openai import OpenAI
import os
import requests
import json 

client = OpenAI()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_EMBEDDING_MODEL = 'text-embedding-ada-002'

def get_embedding(chunk):
    url = 'https://api.openai.com/v1/embeddings'
    headers = {
        'content-type': 'application/json; charset=utf-8',
        'Authorization': f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        'model': OPENAI_EMBEDDING_MODEL,
        'input': chunk
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_json = response.json()
    embedding = response_json["data"][0]["embedding"]
    return embedding

def ai_enhancher(custom_response, context):
    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {"role": "system", "content": "You are a banking assistant to answer userqueries, please look at the function context in which you were invoked along with additional context if you need to answer the user query"},
      {"role": "user", "content": f"Make the following system response more human friendly {custom_response}, you may use this context {context}"},
    ]
  )
    
    print(response.choices[0].message.content)

    return response.choices[0].message.content

def ai_response(user_query, function_context=None, additional_context=None):

    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {"role": "system", "content": "You are a banking assistant to answer userqueries, please look at the function context in which you were invoked along with additional context if you need to answer the user query"},
      {"role": "user", "content": f"Answer this: {user_query}, You were invoked in function:{function_context}, Additional Data that you might require(optional): {additional_context}"},
    ]
  )
    
    print(response.choices[0].message.content)

    return response.choices[0].message.content
    
def ai_response_with_context(user_query, chunks):
    context = "\n".join(chunks)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a banking assistant with access to the bank's information database. Please use the following context to answer the user's query."},
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": user_query},
        ]
    )

    print(response.choices[0].message.content)

    return response.choices[0].message.content

def analyze_transaction(transactions, categories):
    prompt = "Analyze the following transactions and provide insights:\n\n"
    for transaction in transactions:
        prompt += f"Transaction ID: {transaction['t_id']}, Amount: {transaction['amount']}, Category: {transaction['category']}\n"

    prompt += "\nCategories summary:\n"
    for category, amount in categories.items():
        prompt += f"{category}: {amount}\n"

    prompt += "\nPlease provide insights and suggestions based on the above transactions in under 50 words to me keeping the core message intact."

    response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {"role": "system", "content": "You are an AI assistant for a bank and you will be presented with information"},
      {"role": "user", "content": f"{prompt}"},
    ]
  )
    return response.choices[0].message.content
    
