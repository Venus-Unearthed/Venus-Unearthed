#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, request, jsonify
import requests
import os
from xml.etree import ElementTree
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

app = Flask(__name__)
endpoint = "https://resumeanalyser.cognitiveservices.azure.com/"
key = "d6bb5644282347b8a9c74626a13e48bc"
document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))

#Connect to Azure Cognitive Search service
search_endpoint = "https://resumematch343.search.windows.net"
index_name = "resume-match"
search_key = "kgR8HvvJ1SynLR68XQoVQKM13J4MTQxNLB9yP1txigAzSeChpQKh"
search_client = SearchClient(endpoint=search_endpoint, index_name=index_name, credential=AzureKeyCredential(search_key))
azure_url = ''
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

def readBlobs(url):
    print('reading blob started..')
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
    print('reading file...')
    blob_url = url+"/{name}"
    authorization_header = requests.Request('GET', blob_url).headers.get('Authorization')
    blob_response = requests.get(blob_url, headers={'Authorization': authorization_header})
    with open(name,'wb') as f:
        f.write(blob_response.content)
    extract_document(name)

def extract_document(name):
    print('calling document intelligence client')
    path_to_document = os.path.abspath(name)
    document_intelligence_client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    with open(path_to_document,"rb") as f:
        poller = document_intelligence_client.begin_analyze_document("resume-match", analyze_request=f, locale="en-US", content_type="application/octet-stream")
    result = poller.result()
    return result

def upload_document(result,name):
    print('uplloading document')
    for idx, document in enumerate(result.documents):
        extracted_data = {
        "id":name,
        "role": document.fields['role'].content,
        "skills":document.fields['skills'].content,
        "education":document.fields['education'].content,
        "experience": "10"
        }
        print(document.fields['role'].content)
        print(document.fields['skills'].content)
        print(document.fields['education'].content)

    search_client.upload_documents([extracted_data])

def search_client(context):
    print('calling search client')
    result = search_client.search(search_text=context)



if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)


# In[ ]:




