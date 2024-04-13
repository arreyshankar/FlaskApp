from flask import Flask, jsonify, request, render_template, send_file
import os
import face_recognition
import io
import cv2
import numpy as np
from PIL import Image
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import base64

app = Flask(__name__)

connect_str = "DefaultEndpointsProtocol=https;AccountName=mevodrive;AccountKey=UKmeMgZao+Tn44MqV+lvNC1xUyN7x18469fXkxMSyW8geHPQXesKSgWv143dO4vhXbIuaD493SMw+AStQaMdBQ==;EndpointSuffix=core.windows.net"
container_name = "patientimagess"
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

@app.route('/recog', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the request', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if not allowed_file(file.filename):
        return 'File type not allowed', 400
    #save_path = os.path.join(app.root_path, 'images', file.filename)
    #file.save(save_path)
    recognise(file)
    return 'File uploaded successfully', 200

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif','webp'}

def recognise(image):
    pass

@app.route('/testing')
def testing():
    blob_list = container_client.list_blobs()
    
    return 'yes'+blob_list , 200

@app.route('/')
def getImages():
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