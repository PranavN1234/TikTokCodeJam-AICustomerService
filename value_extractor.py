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
model = ChatOpenAI(openai_api_key=key, model_name="gpt-4o", temperature=0.0)

class ValueExtraction(BaseModel):
    value: str = Field(description="Extracted value from the user query")

# Set up a parser
parser = PydanticOutputParser(pydantic_object=ValueExtraction)

# Define the prompt template
prompt_template = PromptTemplate(
    template="Extract the requested information.\n{format_instructions}\nUser Query: {query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

def get_value(user_query, variable, semantic_description):
    # Construct the prompt with the user query and semantic description
    prompt = prompt_template.format(query=f"Extract the {variable} from this query: {user_query}. {semantic_description}")
    
    # Get the response from the model using the chat endpoint
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
    )
    print(response.choices[0].message.content)
    output = response.choices[0].message.content
    
   
    parsed_output = parser.parse(output)
    
   
    return parsed_output
