from sentence_transformers import SentenceTransformer
import numpy as np
import faiss  # For efficient vector search
import json


# Load and process data
def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Extract texts from the dataset
    return [item['cleaned_main_text'] for item in data]


# Generate text embeddings
def generate_embeddings(texts, model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
    model = SentenceTransformer(model_name)
    return model.encode(texts, show_progress_bar=True), model


# Create a FAISS index
def create_faiss_index(embeddings):
    # IndexFlatL2 uses Euclidean distance
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index


# Perform semantic search
def find_similar_texts(query, model, index, texts, k=5):
    query_vector = model.encode([query])
    distances, indices = index.search(query_vector, k)
    return [(texts[i], distances[0][idx]) for idx, i in enumerate(indices[0])]


# Main execution
if __name__ == "__main__":
    # Load dataset
    texts = load_data("Data/processed/processed_results.json")

    # Generate embeddings
    embeddings, model = generate_embeddings(texts)

    # Create vector index
    index = create_faiss_index(embeddings)

    # Interactive search
    while True:
        query = input("Enter a query (type 'exit' to quit): ")
        if query.lower() == "exit":
            break

        results = find_similar_texts(query, model, index, texts, k=3)

        # Display results
        for rank, (text, distance) in enumerate(results, start=1):
            print(f"{rank}. {text[:200]}... (Distance: {distance:.4f})")
