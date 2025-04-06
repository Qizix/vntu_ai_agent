import json



with open("Data/processed/wiki_processed_results.json", "r", encoding="utf-8") as file:
    # Split objects assuming each JSON object is separated by a newline
    lines = file.readlines()
    data = [json.loads(line.strip()) for line in lines]

# Save corrected JSON into a valid format (array f JSON objects)
with open("Data/processed/wiki_processed_results_fixed.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print("Fixed JSON saved to 'wiki_processed_results_fixed.json'")