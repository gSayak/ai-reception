from services.database import records
from services.pinecone_service import index
import random
from config.config import OPENAI_API_KEY
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

def fetch_emergency_action(emergency, cause=None):
    reason = f"The emergency: {emergency}, \n The cause: {cause}"
    searchFix = client.embeddings.create(
      input = reason,
      model = "text-embedding-ada-002"
    )

    doc = index.query(
        vector=searchFix.data[0].embedding,
        top_k=1
    )
    
    for match in doc['matches']:
        match_id = match['id']
        match_score = match['score']

    action = records.find_one({'emergency_type': match_id})["action"]
    print("ACTION: ", action)
    return action

def fetch_user_location(location):
    time = random.randint(5, 20)
    return f"Dr. Adrin is on the way. Estimated time of arrival is {time} minutes. Please continue the steps mentioned before until the doctor arrives."