import pandas as pd
import re
from nltk.tokenize import word_tokenize
import pymorphy2
import nltk
nltk.download('stopwords')
# Інсталюємо залежності перед запуском:
# pip install pandas nltk pymorphy2 pymorphy2-dicts-uk

# Ініціалізація аналізатора для української мови
morph = pymorphy2.MorphAnalyzer(lang='uk')

# Завантажуємо стоп-слова з власного файлу
with open("Data/stopwords_ua.txt", "r", encoding="utf-8") as file:
    stop_words = set(file.read().splitlines())

# Тепер stop_words містить ваш список українських стоп-слів
print(f"Кількість стоп-слів: {len(stop_words)}")

# Функція для обробки тексту
def preprocess_text(text):
    """
    Обробляє текст:
    - Приводить у нижній регістр
    - Видаляє зайві символи
    - Видаляє стоп-слова
    - Виконує лематизацію для кожного слова
    """
    # Приводимо до нижнього регістру
    text = text.lower()

    # Видаляємо всі небажані символи (залишаємо літери і пробіли)
    text = re.sub(r'[^а-яґєёіїґА-Яa-zA-Z\s]', '', text, flags=re.UNICODE)

    # Токенізація (перетворення тексту в список слів)
    words = word_tokenize(text)

    # Видалення стоп-слів
    words = [word for word in words if word not in stop_words]

    # Лематизація
    lemmatized_words = [morph.parse(word)[0].normal_form for word in words]

    return " ".join(lemmatized_words)


# Обробка DataFrame
def clean_dataframe(df):
    """
    Видаляє пусті текстові поля та обробляє колонки із текстом.
    """
    # Видалення рядків із пустим або невизначеним cleaned_main_text
    df = df[df['cleaned_main_text'].notnull()]  # Видаляємо None
    df = df[df['cleaned_main_text'].str.strip() != ""]  # Видаляємо порожній текст

    # Обробка тексту
    df['processed_text'] = df['cleaned_main_text'].apply(preprocess_text)
    df.drop(columns=['cleaned_main_text'], inplace=True)

    return df


# Приклад завантаження та обробки JSON
if __name__ == "__main__":
    # Завантаження "брудних" даних
    df = pd.read_json('Data/raw/results.json')  # Змінити на ваш шлях до даних

    # Виконаємо очищення та обробку
    processed_df = clean_dataframe(df)

    # Збереження оброблених даних у файл
    processed_df.to_json('Data/processed/processed_results.json', orient='records', lines=True, force_ascii=False)

    print(processed_df.head())