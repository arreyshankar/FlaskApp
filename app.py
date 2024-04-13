from flask import Flask, jsonify, request, render_template, send_file, Response
import os
import face_recognition
import io
import cv2
import numpy as np
from PIL import Image
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import base64

app = Flask(__name__)
directory = "images"

connect_str = "DefaultEndpointsProtocol=https;AccountName=mevodrive;AccountKey=UKmeMgZao+Tn44MqV+lvNC1xUyN7x18469fXkxMSyW8geHPQXesKSgWv143dO4vhXbIuaD493SMw+AStQaMdBQ==;EndpointSuffix=core.windows.net"
container_name = "patientimagess"
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

BlobImages = []
BlobImagesEncodings = []
BlobImageNames = []

def getImagesfromBlobStorage():
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        blob_client = container_client.get_blob_client(blob)
        save_path = os.path.join(app.root_path, 'images', blob.name)
        with open(save_path, "wb") as local_file:
            blob_data = blob_client.download_blob().readall()
            local_file.write(blob_data)
            BlobImageNames.append(local_file.name)
            BlobImages.append(local_file)

def load_images_from_directory(directory):
    image_files = [file for file in os.listdir(directory) if file.endswith(('jpg', 'jpeg', 'png'))]
    images = []
    for file in image_files:
        image_path = os.path.join(directory, file)
        image = face_recognition.load_image_file(image_path)
        images.append((image,file))
    return images

@app.route('/recog', methods=['POST'])
def compare_face():
    getImagesfromBlobStorage()
    if 'image' not in request.files:
        return jsonify({'error': 'No image file found'}), 400

    uploaded_image = request.files['image']
    uploaded_image_bytes = uploaded_image.read()
    uploaded_image_array = face_recognition.load_image_file(uploaded_image_bytes)

    directory = "images"
    images = load_images_from_directory(directory)

    uploaded_image_face_encodings = face_recognition.face_encodings(uploaded_image_array)
    if not uploaded_image_face_encodings:
        return jsonify({'error': 'No face found in the uploaded image'}), 400

    match_found = False
    for image, filename in images:
        image_face_encodings = face_recognition.face_encodings(image)
        if image_face_encodings:
            match = face_recognition.compare_faces(image_face_encodings, uploaded_image_face_encodings[0])
            if match[0]:
                match_found = True
                result = {'match': True, 'filename': filename}
                break

    if match_found:
        return jsonify(result), 200
    else:
        return jsonify({'match': False}), 200





''''
    reference_image_file = request.files['reference_image']
    print(reference_image_file)
    reference_image = Image.open(reference_image_file)
    reference_image = reference_image.convert('RGB')
    reference_image_np = np.array(reference_image)

    reference_face_locations = face_recognition.face_locations(reference_image_np)

    if not reference_face_locations:
        return jsonify({'error': 'No face detected in the reference image'})

    reference_face_encodings = face_recognition.face_encodings(reference_image_np, reference_face_locations)

    directory = 'images'

    image_files = [file for file in os.listdir(directory) if file.endswith(('jpg', 'jpeg', 'png'))]
    for i, file in enumerate(image_files, start=1):
        image_path = os.path.join(directory, file)
        image = face_recognition.load_image_file(image_path)
        image_face_locations = face_recognition.face_locations(image)
        if image_face_locations:
            image_face_encodings = face_recognition.face_encodings(image, image_face_locations)
            match = face_recognition.compare_faces(reference_face_encodings, image_face_encodings[0])
            if match[0]:
                return jsonify({'match': True, 'matching_image': file})

    return jsonify({'match': False})

    '''
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif','webp'}


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