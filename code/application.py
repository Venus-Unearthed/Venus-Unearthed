#!/usr/bin/env python
# coding: utf-8

# In[46]:


from flask import Flask, request, jsonify
import requests
import os
from xml.etree import ElementTree
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from datetime import datetime,date

app = Flask(__name__)

endpoint = "https://resumedataextractor.cognitiveservices.azure.com/"
key = "ae61a24dc61845d4ba800108884bdd0c"
document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))


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


#Connect to Azure Cognitive Search service
search_endpoint = "https://resumematch343.search.windows.net"
index_name = "resume-match"
search_key = "kgR8HvvJ1SynLR68XQoVQKM13J4MTQxNLB9yP1txigAzSeChpQKh"
search_client = SearchClient(endpoint=search_endpoint, index_name=index_name, credential=AzureKeyCredential(search_key))
azure_url = ''
contextString = ''

def readBlobs(url):
    print('reading blobs..')
    authorization_header = requests.Request('GET', url).headers.get('Authorization')
    #Make request to Azure Blob Storage service
    response = requests.get(url, headers={'Authorization': authorization_header})
    root = ElementTree.fromstring(response.content)
    # Extract blob names
    blobs = [blob.text for blob in root.findall(".//Blob/Name")]
    print(blobs)
    for blob in blobs:
        readBlobContent(blob,get_base_url(url))

def get_base_url(url):
    url_split = url.split('?')
    return url_split[0]

def readBlobContent(name,url):
    print('reading blob file..')
    blob_url = url+'/'+name
    authorization_header = requests.Request('GET', blob_url).headers.get('Authorization')
    blob_response = requests.get(blob_url, headers={'Authorization': authorization_header})
    with open(name,'wb') as f:
        f.write(blob_response.content)
    extract_document(name)

def extract_document(name):
    print("extracting document")
    path_to_document = os.path.abspath(name)
    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    with open(path_to_document,"rb") as f:
        poller = document_intelligence_client.begin_analyze_document("resumeExtractorModel3", analyze_request=f, locale="en-US", content_type="application/octet-stream")
    result = poller.result()
    upload_document(result,name)
    return result

def upload_document(result,name):
    print("upload document")
    base_name,exte = os.path.splitext(name)
    print(".."+base_name)
    for idx, document in enumerate(result.documents):
        print(document.fields)
        extracted_data = {
        "id":str(base_name),
        "name":name,
        "role": document.fields['role'].content,
        "skills":document.fields['skills'].content,
        "softskills":document.fields['softskills'].content,
        "currentRole":document.fields['currentRole'].content,
        "certifications":document.fields['certifications'].content,
        "overallExperience":document.fields['overallExperience'].content,
        "education":document.fields['education'].content,
        "experience":read_expirence(document.fields['experience'].content)+' years of experience'
        }
       
    search_client.upload_documents([extracted_data])

def read_expirence(expirence):
    start_date,end_date = expirence.split(" to ")
    return calculate_experience(start_date,end_date)

def consturuct_response(result,count):
    result = {
        "status":"Success",
        "count":count,
        "metadata":{
            "confidenceScore":get_confidence_score(result,count)
        },
        "results":result
    }
    return result

def get_confidence_score(content,no_of_match):
    score = 0
    for data in content:
        score = score+data["score"]
    return score/no_of_match

def search_content(content,no_of_match):
    print(".........."+content)
    results = search_client.search(search_text=content)
    search_results = []
    for i,result in enumerate(results):
        search_results.append(result)
        if(i==no_of_match):
            break
    print(search_results)
    final = [{"id":d["id"],"score":d["@search.score"],"name":d["name"]} for d in search_results]
    return consturuct_response(final,len(search_results))

def calculate_experience(start_date_str, end_date_str):
    # Define date formats to try
    date_formats = ['%b %Y', '%m/%Y']

    # Convert string representations of dates to datetime objects
    start_date = None
    for fmt in date_formats:
        try:
            start_date = datetime.strptime(start_date_str, fmt)
            break
        except ValueError:
            pass

    # Check if the end_date_str is "current"
    if end_date_str.lower() == "current":
        end_date = date.today()
    else:
        end_date = None
        for fmt in date_formats:
            try:
                end_date = datetime.strptime(end_date_str, fmt)
                break
            except ValueError:
                pass

    # If end_date is still None, it means it's "current"
    if end_date is None:
        end_date = date.today()

    # Calculate the difference in years
    experience_years = (end_date.year - start_date.year) + (end_date.month - start_date.month) / 12

    return str(experience_years)


if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)

