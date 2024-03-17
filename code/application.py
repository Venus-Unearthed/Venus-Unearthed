from hackathon.resumeDocAnalyser import readBlobs
from flask import Flask, request, jsonify

app = Flask(__name__)

# Define a route for your API endpoint
@app.route('/hackathon2024/team343/search', methods=['POST'])
def api():
    print('api call started')
    data = request.json  # Get JSON data from the request body
    azure_url = data.get("inputPath")
    readBlobs(azure_url)
    # Process the data as needed
    result = {"message": "Received data", "data": data}
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)