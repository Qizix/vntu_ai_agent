from sentence_transformers import SentenceTransformer
import numpy as np
import faiss  # For efficientvecto search
import json
import os



# Load and process data
def load_data(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Extract texts from the dataset
    return [item['processed_text'] for item in data]


# Generate text embeddings
def generate_embeddings(texts, model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
    print(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name)
    print("Model loaded. Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings, model


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

# Save embeddings and index
def save_vector_data(embeddings, texts, index, model, output_dir="Data/processed"):
    os.makedirs(output_dir, exist_ok=True)

    print("Saving FAISS index...")
    faiss.write_index(index, f"{output_dir}/vector_index.faiss")

    print("Saving embeddings...")
    np.save(f"{output_dir}/embeddings.npy", embeddings)

    print("Saving texts...")
    with open(f"{output_dir}/texts.json", "w", encoding="utf-8") as file:
        json.dump(texts, file, ensure_ascii=False, indent=4)

    print("Saving model...")
    model.save(f"{output_dir}/sentence_transformer_model")

    print("All data saved successfully.")

# Load model, texts, and FAISS index
def load_vector_data(output_dir="Data/processed"):
    print("Loading data...")

    print("Loading FAISS index...")
    index = faiss.read_index(f"{output_dir}/vector_index.faiss")

    print("Loading embeddings...")
    embeddings = np.load(f"{output_dir}/embeddings.npy")

    print("Loading texts...")
    with open(f"{output_dir}/texts.json", "r", encoding="utf-8") as file:
        texts = json.load(file)

    print("Loading model...")
    model = SentenceTransformer(f"{output_dir}/sentence_transformer_model")

    print("Data loaded successfully.")
    return embeddings, texts, index, model

# Evaluate vectorizer (testing function)
def evaluate_vectorizer(query, model, index, texts, k=5):
    print(f"Evaluating vectorizer with query: '{query}'")
    results = find_similar_texts(query, model, index, texts, k)
    print("Top similar results:")
    for i, (text, distance) in enumerate(results):
        print(f"\nResult {i + 1}:")
        print(f"Text: {text}")
        print(f"Distance: {distance}")


# Main execution
if __name__ == "__main__":
    # Paths and settings
    data_path = "Data/processed/big_processed_results.json"
    output_dir = "Data/processed/big"

    # Load dataset
    print("Loading dataset...")
    texts = load_data(data_path)
    print("Dataset loaded successfully. Number of texts:", len(texts))

    # Generate embeddings using multilingual model
    embeddings, model = generate_embeddings(texts,
                                            model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

    # Create vector index
    index = create_faiss_index(embeddings)

    # Save vectorizer data
    save_vector_data(embeddings, texts, index, model, output_dir=output_dir)

    # Load vectorizer data (for testing)
    embeddings, texts, index, model = load_vector_data(output_dir=output_dir)

    # Test the vectorizer
    test_query = "Що ти знаєш про фііту?"
    evaluate_vectorizer(test_query, model, index, texts, k=5)
