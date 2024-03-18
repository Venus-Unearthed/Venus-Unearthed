from resumeDocAnalyser import readBlobs
from flask import Flask, request, jsonify
import subprocess
import requests

def install_dependecies():
    try:
        subprocess.ceck_call(["pip","install","-r","requirements.txt"])
        print("done")
    except: subprocess.CalledProcessError as e
        print("error")
app = Flask(__name__)

# Define a route for your API endpoint
@app.route('/hackathon2024/team343/ping', methods=['GET'])
def ping_api():
    print('ping call started')
    result = {
            "status":"Success"
        }
    return jsonify(result)

# Define a route for your API endpoint
@app.route('/hackathon2024/team343/search', methods=['POST'])
def search_api():
    print('search api call started')
    data = request.json  # Get JSON data from the request body
    azure_url = data.get("inputPath")
    contextString = data.get("context")
    categoty = data.get("category")
    no_of_match = data.get("noOfMatches")
    threshold = data.get("threshold")
    if(categoty == 'resume'):
        #readBlobs(azure_url)
        result = search_content(data.get("context"),no_of_match)
    else:
        result = {
            "status":"Bad Request Please check category should be resume!"
        }
    return jsonify(result)


if __name__ == '__main__':
    install_dependecies()
    app.run(debug=True,use_reloader=False)
