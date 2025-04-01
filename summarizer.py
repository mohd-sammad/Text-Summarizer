from flask import Flask, request, jsonify
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import string
import json
import os
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    # For development, set a default API key if environment variable is not available
    API_KEY = "default_dev_key"
    print("Warning: Using default development API key")

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
CORS(app)  # Enable CORS to allow requests from frontend

# Route to handle the root URL with example text summarization
@app.route('/')
def home():
    example_text = "Engineering colleges play a crucial role in shaping the future of students by providing top-notch education, cutting-edge research opportunities, and industry connections. Institutes like the Indian Institutes of Technology (IITs) and National Institutes of Technology (NITs) are considered the premier engineering institutions in India. These colleges offer various undergraduate, postgraduate, and research programs across multiple engineering disciplines. With a focus on innovation, technology, and real-world applications, these institutions prepare students to excel in the global job market and contribute to the advancement of engineering and technology.."
    summary = summarize_text(example_text, 2)
    
    return f"""
    <h1>Text Summarizer API</h1>
    <h2>Example:</h2>
    <h3>Original Text:</h3>
    <p>{example_text}</p>
    <h3>Summary (2 sentences):</h3>
    <p>{summary}</p>
    <h3>API Usage:</h3>
    <p>Send a POST request to <code>/summarize</code> with JSON payload containing:</p>
    <pre>
    {{
        "text": "Engineering colleges play a crucial role in shaping the future of students by providing top-notch education, cutting-edge research opportunities, and industry connections. Institutes like the Indian Institutes of Technology (IITs) and National Institutes of Technology (NITs) are considered the premier engineering institutions in India. These colleges offer various undergraduate, postgraduate, and research programs across multiple engineering disciplines. With a focus on innovation, technology, and real-world applications, these institutions prepare students to excel in the global job market and contribute to the advancement of engineering and technology.",
        "num_sentences": 3,
        "api_key": "AIzaSyAdTwUGKZSUN-VYfTjXvoGyRxJIcqimWkI"
    }}
    </pre>
    """

def summarize_text(text, num_sentences=3):
    """Summarize the given text based on word frequency."""
    # Handle empty text
    if not text:
        return ""
        
    sentences = sent_tokenize(text)
    
    # Return the text as is if it has fewer sentences than requested
    if len(sentences) <= num_sentences:
        return text
        
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words and word not in string.punctuation]
    
    word_freq = Counter(words)
    sentence_scores = {}
    
    # Assign scores to sentences based on the word frequency
    for i, sent in enumerate(sentences):
        sentence_score = 0
        for word in word_tokenize(sent.lower()):
            if word in word_freq:
                sentence_score += word_freq[word]
        sentence_scores[i] = sentence_score
    
    # Get indices of top-scoring sentences
    top_indices = sorted(range(len(sentences)), key=lambda i: sentence_scores[i], reverse=True)[:num_sentences]
    
    # Sort the selected indices to maintain original order
    top_indices.sort()
    
    # Extract the selected sentences in their original order
    summarized_sentences = [sentences[i] for i in top_indices]
    
    return ' '.join(summarized_sentences)

@app.route('/summarize', methods=['POST', 'GET'])
def summarize():
    """API endpoint to summarize text."""
    # Handle GET requests with demo page
    if request.method == 'GET':
        return """
        <h1>Text Summarizer API - Test Form</h1>
        <form id="summaryForm">
            <div>
                <label for="text">Text to summarize:</label><br>
                <textarea id="text" name="text" rows="10" cols="60">Medicine is the science and practice of diagnosing, treating, and preventing diseases. Modern medicine uses medications, surgery, and many other techniques. Doctors and other healthcare professionals provide medical care. Hospitals are institutions where medical care is provided. Medical research is conducted to improve treatments and find cures.</textarea>
            </div>
            <div>
                <label for="num_sentences">Number of sentences:</label><br>
                <input type="number" id="num_sentences" name="num_sentences" value="2" min="1">
            </div>
            <div>
                <label for="api_key">API Key (optional for testing):</label><br>
                <input type="text" id="api_key" name="api_key" value="">
            </div>
            <div>
                <button type="button" onclick="summarizeText()">Summarize Text</button>
            </div>
        </form>
        <div id="result" style="margin-top: 20px;"></div>
        
        <script>
        function summarizeText() {
            const text = document.getElementById('text').value;
            const num_sentences = document.getElementById('num_sentences').value;
            const api_key = document.getElementById('api_key').value;
            
            fetch('/summarize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: text,
                    num_sentences: parseInt(num_sentences),
                    api_key: api_key
                }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('result').innerHTML = `<div style="color: red;">Error: ${data.error}</div>`;
                } else {
                    document.getElementById('result').innerHTML = `
                        <h3>Summary:</h3>
                        <p>${data.summary}</p>
                        <h3>Details:</h3>
                        <ul>
                            <li>Original length: ${data.original_length} characters</li>
                            <li>Summary length: ${data.summary_length} characters</li>
                            <li>Original sentences: ${data.sentences_in_original}</li>
                            <li>Summarized to: ${data.sentences_requested} sentences</li>
                            <li>Compression ratio: ${Math.round((data.summary_length / data.original_length) * 100)}%</li>
                        </ul>
                    `;
                }
            })
            .catch(error => {
                document.getElementById('result').innerHTML = `<div style="color: red;">Error: ${error}</div>`;
            });
        }
        </script>
        """
    
    try:
        # Get data from the POST request
        data = request.get_json()
        
        # Check if data is None
        if data is None:
            return jsonify({"error": "No data provided"}), 400
        
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid JSON string"}), 400
        
        # Get the input text and the number of sentences for the summary
        text = data.get("text", "Engineering colleges play a crucial role in shaping the future of students by providing top-notch education, cutting-edge research opportunities, and industry connections. Institutes like the Indian Institutes of Technology (IITs) and National Institutes of Technology (NITs) are considered the premier engineering institutions in India. These colleges offer various undergraduate, postgraduate, and research programs across multiple engineering disciplines. With a focus on innovation, technology, and real-world applications, these institutions prepare students to excel in the global job market and contribute to the advancement of engineering and technology..")

        num_sentences = int(data.get("num_sentences", 3))
        api_key = data.get("api_key", "")
        
        # For development purposes, accept empty API key or match with the set API_KEY
        if API_KEY and api_key != "" and api_key != API_KEY:
            return jsonify({"error": "Invalid API Key"}), 403
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # Get the summary
        summary = summarize_text(text, num_sentences)
        
        # Return detailed response
        return jsonify({
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "sentences_requested": num_sentences,
            "sentences_in_original": len(sent_tokenize(text))
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)