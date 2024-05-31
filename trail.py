
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


