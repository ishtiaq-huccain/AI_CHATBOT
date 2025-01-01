import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from flask import Flask, render_template, request


app = Flask(__name__)

# Load the CSV file into a Pandas DataFrame
df = pd.read_csv('products.csv')

# Combine relevant text columns for better matching
df['combined_text'] = df['Title'] + ' ' + df['review'].astype(str)

# Vectorize the text data
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['combined_text'])

# Function to filter items based on price range
def filter_by_price_range(df, min_price, max_price):
    return df[(df['Price'].apply(lambda x: min_price <= int(re.sub('[^0-9]', '', x)) <= max_price))]

# Function to filter items based on specs
def filter_by_specs(df, specs):
    return df[df['combined_text'].str.lower().str.contains(specs.lower())]

# Function to get the most similar item based on user input
def get_most_similar_item(user_input):
    user_input_vector = vectorizer.transform([user_input])
    similarity_scores = cosine_similarity(user_input_vector, tfidf_matrix).flatten()
    most_similar_index = similarity_scores.argmax()
    return df.loc[most_similar_index]

# Function to handle special cases
def handle_special_cases(user_input):
    # Extracting relevant information from user input
    min_price_match = re.search(r'(\d+)k', user_input)
    min_price = int(min_price_match.group(1)) * 1000 if min_price_match else 0

    max_price_match = re.search(r'(\d+)k', user_input)
    max_price = int(max_price_match.group(1)) * 1000 if max_price_match else float('inf')

    specs_match = re.search(r'(\d+) GB RAM.*(\d+) MP camera', user_input)
    ram, camera = specs_match.groups() if specs_match else (None, None)

    brand_match = re.search(r'Samsung', user_input, flags=re.I)
    brand = brand_match.group(0) if brand_match else None

    # Filter items based on the extracted information
    filtered_items = df
    if min_price or max_price:
        filtered_items = filter_by_price_range(filtered_items, min_price, max_price)
    
    if ram or camera:
        specs_query = f"{ram} GB RAM" if ram else ""
        specs_query += f" {camera} MP camera" if camera else ""
        filtered_items = filter_by_specs(filtered_items, specs_query)

    if brand:
        filtered_items = filter_by_brand(filtered_items, brand)

    # Sort items based on specified criteria
    sorted_items = filtered_items.sort_values(by=['rating', 'Price'], ascending=[False, True]).head(5)

    return sorted_items

# # Simple chatbot loop
# while True:
#     user_input = input("User: ")

#     if user_input.lower() in ['exit', 'quit', 'bye']:
#         print("Chatbot: Goodbye!")
#         break

#     # Handle special cases
#     if 'top 5 phones' in user_input.lower():
#         special_case_result = handle_special_cases(user_input)
#         print("Chatbot: Top 5 phones based on specified criteria:")
#         for index, item in special_case_result.iterrows():
#             print(f"- {item['Title']} priced at {item['Price']} with a rating of {item['rating']}.")
#         continue

#     # Get the most similar item from the dataset based on user input
#     most_similar_item = get_most_similar_item(user_input)

#     # Generate a response based on the most similar item
#     response = f"Chatbot: {most_similar_item['Title']} is priced at {most_similar_item['Price']} with a rating of {most_similar_item['rating']}."
#     print(response)

#     # Show reviews for the most similar item
#     print("\nReviews:")
#     for review in eval(most_similar_item['review']):
#         print(f"- {review}")

# Define routes
@app.route('/')
def home():
    return render_template('web.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    response_messages = []

    # Handle special cases
    if 'top 5 phones' in user_input.lower():
        special_case_result = handle_special_cases(user_input)
        for _, item in special_case_result.iterrows():
            response_messages.append(
                f"{item['Title']} priced at {item['Price']} with a rating of {item['rating']}. Review: {item['review']}"
            )
    else:
        most_similar_item = get_most_similar_item(user_input)
        response_messages.append(
            f"{most_similar_item['Title']} is priced at {most_similar_item['Price']} with a rating of {most_similar_item['rating']}."
        )

    return render_template('web.html', user_input=user_input, responses=response_messages)

if __name__ == '__main__':
    app.run(debug=True)
