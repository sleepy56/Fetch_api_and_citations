# from flask import Flask, jsonify, render_template

# from fetch_api import fetch_data_and_identify_citations
# app = Flask(__name__)

# citations = fetch_data_and_identify_citations()

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/citations')
# def get_citations():
#     return jsonify(citations)

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, jsonify, render_template, request
from flask_executor import Executor
from flask_caching import Cache
import fetch_api  # Import the fetch_api_data module

app = Flask(__name__)
executor = Executor(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Route to start the model in the background
@app.route('/run_model', methods=['POST'])
def run_model():
    executor.submit(fetch_api.fetch_data_and_identify_citations)
    return jsonify({'status': 'Model is running in the background'}), 202

# Route to get the citations
@app.route('/citations')
@cache.cached(timeout=60)
def get_citations():
    results = fetch_api.fetch_data_and_identify_citations()
    return jsonify(results)

# Route to render the main page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
