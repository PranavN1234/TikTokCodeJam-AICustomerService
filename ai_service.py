from openai import OpenAI


client = OpenAI()

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
    