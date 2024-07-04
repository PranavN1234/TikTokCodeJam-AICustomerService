import os
import openai
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Set the OpenAI API key
key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI model
model = ChatOpenAI(openai_api_key=key, model_name="gpt-4o", temperature=0.7)

class ModifiedQury(BaseModel):
    value: str = Field(description="Modify the AI response to stem it naturally as a human would. Just remember it's a continous conversation.")

# Set up a parser
parser = PydanticOutputParser(pydantic_object=ModifiedQury)

# Define the prompt template
prompt_template = PromptTemplate(
    template="Modify the AI response to stem it naturally as human would in that situation after user prompted something\n{format_instructions}\nUser Query: {query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

def modify_prompt(ai_response, semantic_description):
    # Construct the prompt with the user query and semantic description
    prompt = prompt_template.format(query=f"Modify the AI response from this: {ai_response}, Here is some semantic description to help you parse the response: {semantic_description}")
    
    # Get the response from the model using the chat endpoint
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful banking customer relation assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=1.0,
    )
    print(response.choices[0].message.content)
    output = response.choices[0].message.content
    
   
    parsed_output = parser.parse(output)
    
   
    return parsed_output.value

# # Test function for validation
# if __name__ == "__main__":
#     ai_response = "Authentication completed. Welcome to Premier Trust Bank. I am Jessica your AI Assistant. How can I assist you today?"
#     semantic_description = "Make the response more conversational and natural and make sure that user is authenticated. This is the user name for your reference: Pranav Iyer"
    
#     modified_response = modify_prompt(ai_response, semantic_description)
#     print(f"Modified Response: {modified_response.value}")