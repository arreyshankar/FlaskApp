from flask import Flask, jsonify, request, render_template
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import base64

app = Flask(__name__)

connect_str = "DefaultEndpointsProtocol=https;AccountName=mevodrive;AccountKey=UKmeMgZao+Tn44MqV+lvNC1xUyN7x18469fXkxMSyW8geHPQXesKSgWv143dO4vhXbIuaD493SMw+AStQaMdBQ==;EndpointSuffix=core.windows.net"
container_name = "patientimagess"

blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

@app.route('/')
def index():
    blob_list = container_client.list_blobs()
    images = []
    for blob in blob_list:
        blob_client = container_client.get_blob_client(blob)
        stream = blob_client.download_blob().readall()
        encoded_image = base64.b64encode(stream).decode('utf-8')
        images.append(encoded_image)
    
    return render_template('index.html', images=images)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
