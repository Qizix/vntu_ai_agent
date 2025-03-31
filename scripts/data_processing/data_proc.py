import json
import re
import pandas as pd
import stanza
import pymorphy2


# Завантаження стоп-слі
def load_stopwords(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return set(word.strip() for word in file.readlines())


# Очищення тексту
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^а-яєґіїї\s]', '', text)  # Залишаємо тільки літери та пробіли
    return text


# Токенізація
def tokenize_text(text, nlp):
    doc = nlp(text)
    return [word.text for sentence in doc.sentences for word in sentence.words]


# Видалення стоп-слів
def remove_stopwords(tokens, stopwords):
    return [token for token in tokens if token not in stopwords]


# Лематизація
def lemmatize_tokens(tokens, morph):
    return [morph.parse(token)[0].normal_form for token in tokens]


# Повна обробка тексту
def process_text(text, nlp, morph, stopwords):
    cleaned_text = clean_text(text)
    tokens = tokenize_text(cleaned_text, nlp)
    tokens = remove_stopwords(tokens, stopwords)
    lemmatized_text = lemmatize_tokens(tokens, morph)
    return ' '.join(lemmatized_text)


# Обробка DataFrame
def process_dataframe(df, nlp, morph, stopwords):
    df['processed_text'] = df['cleaned_main_text'].apply(
        lambda text: process_text(text, nlp, morph, stopwords) if pd.notna(text) else '')
    df = df[df['processed_text'].str.strip() != '']
    return df[['processed_text']]


# Завантаження JSON, обробка та збереження результату
def process_json(input_file, output_file, stopwords_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    df = pd.DataFrame(data)
    stopwords = load_stopwords(stopwords_file)
    nlp = stanza.Pipeline('uk', processors='tokenize')
    morph = pymorphy2.MorphAnalyzer(lang='uk')

    processed_df = process_dataframe(df, nlp, morph, stopwords)

    processed_df.to_json(output_file, orient='records', force_ascii=False, indent=4)
    print("Обробка завершена. Результат збережено у файл", output_file)

if __name__ == "__main__":
    # Завантаження даних
    input_json = 'Data/raw/big_results.json'
    output_json = 'Data/processed/big_processed_results.json'
    stopwords_file = 'Data/stopwords_ua.txt'

    process_json(input_json, output_json, stopwords_file)

    print("Обробка завершена. Результат збережено!")
