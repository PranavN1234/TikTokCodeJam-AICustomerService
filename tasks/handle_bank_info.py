import os
from pinecone import Pinecone
from dotenv import load_dotenv
from utils import synthesize_audio, play_audio
from user_data import UserData
from ai_service import get_embedding, ai_response_with_context
from flask_socketio import emit

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "prime-bank-info"

def get_most_similar_chunks_for_query(query, recent_queries, index_name):
    combined_query = " | ".join(recent_queries[-2:] + [query])
    print(f'Combined Query: {combined_query}')
    print("\nEmbedding query using OpenAI ...")
    question_embedding = get_embedding(combined_query)

    print("\nQuerying Pinecone index ...")
    print("\nIndex name:", index_name)
    index = pc.Index(name=index_name)

    # Perform a general query without filters
    general_query_results = index.query(vector=question_embedding, top_k=5, include_metadata=True)
    all_results = [x['metadata']['text'] for x in general_query_results['matches'] if 'text' in x['metadata']]

    return all_results

def get_bank_info(user_query):
    user_data = UserData()
    recent_queries = user_data.get_recent_queries()
    results = get_most_similar_chunks_for_query(user_query, recent_queries, index_name)
    
    if results:
        response = ai_response_with_context(user_query, results)
        synthesize_audio(response)
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': response, 'response': 'no_response'})
    else:
        synthesize_audio("Sorry, I couldn't find any relevant information.")
        with open("output.mp3", "rb") as audio_file:
            tts_audio = audio_file.read()
        emit('tts_audio', {'audio': tts_audio, 'prompt': response, 'response': 'no_response'})
