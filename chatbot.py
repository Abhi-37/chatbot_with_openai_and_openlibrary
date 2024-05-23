import os
import logging
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from langchain import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from dotenv import load_dotenv

# Initialize Flask app and CORS
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.logger.setLevel(logging.ERROR)

# Load environment variables
load_dotenv()

# Initialize global variables
conversation_retrieval_chain = None
chat_history = []

# Function to process a PDF document
def process_document(document_path):
    global conversation_retrieval_chain
    loader = PyPDFLoader(document_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    db = Chroma.from_documents(texts)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 2})
    conversation_retrieval_chain = ConversationalRetrievalChain.from_retriever(retriever)

# Function to process a user prompt
def process_prompt(prompt):
    global conversation_retrieval_chain, chat_history
    result = conversation_retrieval_chain({"question": prompt, "chat_history": chat_history})
    chat_history.append((prompt, result["answer"]))
    return result['answer']

# Function to fetch book-related data from the Open Library API
def fetch_book_data(query):
    url = f"https://openlibrary.org/search.json?q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# Define the route for the index page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Define the route for processing documents
@app.route('/process-document', methods=['POST'])
def process_document_route():
    if 'file' not in request.files:
        return jsonify({
            "botResponse": "It seems like the file was not uploaded correctly, can you try again. If the problem persists, try using a different file"
        }), 400
    file = request.files['file']
    file_path = 'documents/' + file.filename
    file.save(file_path)
    process_document(file_path)
    return jsonify({
        "botResponse": "Thank you for providing your PDF document. I have analyzed it, so now you can ask me any questions regarding it!"
    }), 200

# Define the route for processing messages
@app.route('/process-message', methods=['POST'])
def process_message_route():
    user_message = request.json['userMessage']
    bot_response = process_prompt(user_message)
    return jsonify({
        "botResponse": bot_response
    }), 200

# Define the route for fetching book-related data from Open Library API
@app.route('/fetch-book-data', methods=['GET'])
def fetch_book_data_route():
    query = request.args.get('query')
    if query:
        data = fetch_book_data(query)
        if data:
            return jsonify(data), 200
    return jsonify({"error": "Invalid query or unable to fetch data from Open Library API"}), 400

if __name__ == "__main__":
    app.run(debug=True, port=8000, host='0.0.0.0')
