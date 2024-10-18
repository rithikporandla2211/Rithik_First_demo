from flask import Flask, render_template, request, session
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import openai
import os
from dotenv import load_dotenv
from datetime import datetime
import json


# Load environment variables
load_dotenv()

app = Flask(__name__)
#app.secret_key = 'your_secret_key'

# Azure Cognitive Search credentials
search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
search_key = os.getenv('AZURE_SEARCH_KEY')
index_name = os.getenv('INDEX_NAME')
credential = AzureKeyCredential(search_key)
search_client = SearchClient(endpoint=search_endpoint, index_name=index_name, credential=credential)

# Azure OpenAI credentials
openai.api_type = "azure"
openai.api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
openai.api_version = "2024-05-01-preview"
openai.api_key = os.getenv('AZURE_OPENAI_KEY')
deployment_id = 'demodeploy'


# Log queries and responses to a JSON file
def log_query_json(user_query, answer):
    log_entry = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'query': user_query,
        'response': answer
    }

    # Check if the file exists, if not create a new one
    if not os.path.isfile('query_logs.json'):
        with open('query_logs.json', 'w') as f:
            json.dump([], f)

    # Append the new log entry to the JSON file
    with open('query_logs.json', 'r+') as file:
        logs = json.load(file)
        logs.append(log_entry)
        file.seek(0)
        json.dump(logs, file, indent=4)


def retrieve_documents(user_query):
    # Search relevant documents using Azure Cognitive Search
    search_results = search_client.search(
        search_text=user_query,
        top=10  # Retrieve top 10 relevant documents
    )

    retrieved_content = ''
    for result in search_results:
        if 'content' in result:
            retrieved_content += result['content'] + '\n'

    return retrieved_content

def generate_openai_response(user_query, retrieved_documents):
    # Build the prompt with retrieved documents and user query
    prompt = f"""You are an enterprise assistant. Use the following documents to answer the question.
    If the answer is not contained in the documents below, say you don't know.

    Documents:
    {retrieved_documents}

    Question: {user_query}
    Answer:"""

    try:
        response = openai.ChatCompletion.create(
            deployment_id=deployment_id,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.OpenAIError as e:
        return f"Error: {str(e)}"


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_query = request.form['query']

        # Step 1: Retrieve relevant documents
        retrieved_documents = retrieve_documents(user_query)

        # Step 2: Generate response using Azure OpenAI
        assistant_response = generate_openai_response(user_query, retrieved_documents)
        
        # Log the query and response to the JSON file
        log_query_json(user_query, assistant_response)

        return render_template('result.html', query=user_query, answer=assistant_response)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
