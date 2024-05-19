import requests
from sentence_transformers import SentenceTransformer, util

API_ENDPOINT = "https://devapi.beyondchats.com/api/get_message_with_sources"
model = SentenceTransformer('all-MiniLM-L6-v2')

# Fetch data from the API
def fetch_data_from_api(endpoint):
    data = []
    next_page_url = endpoint

    while next_page_url:
        response = requests.get(next_page_url)
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            break

        response_data = response.json()
        inner_data = response_data.get('data', {})
        items = inner_data.get('data', [])

        if not items:
            break

        data.extend(items)
        next_page_url = inner_data.get('next_page_url')

    return data

# Check similarity between response text and context
def check_similarity(response_text, context, model):
    embeddings1 = model.encode(response_text, convert_to_tensor=True)
    embeddings2 = model.encode(context, convert_to_tensor=True)
    cosine_scores = util.pytorch_cos_sim(embeddings1, embeddings2)
    return cosine_scores.item() > 0.7  # Adjust threshold as needed

# Identify citations based on similarity
def identify_citations(response_text, sources, model):
    citations = []
    for source in sources:
        context = source.get('context')
        if isinstance(context, str) and check_similarity(response_text, context, model):
            citation = {"id": source["id"]}
            if source.get("link"):
                citation["link"] = source["link"]
            citations.append(citation)
    return citations

# Fetch data and identify citations
def fetch_data_and_identify_citations():
    data = fetch_data_from_api(API_ENDPOINT)
    if not data:
        print("No data fetched from the API.")
        return []

    results = []
    for item in data:
        response_text = item.get('response')
        sources = item.get('source')

        if not response_text or not isinstance(sources, list):
            print(f"Missing or invalid data in item: {item}")
            continue

        citations = identify_citations(response_text, sources, model)
        results.append(citations)

    return results
