from flask import Flask, jsonify, request, render_template, send_file, Response
import os
import face_recognition
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import numpy as np
from bson.objectid import ObjectId
from PIL import Image
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import base64

app = Flask(__name__)
directory = "images"

client = MongoClient('mongodb+srv://sarvesh:mevo123@testingcluster.tg9uqrx.mongodb.net/?retryWrites=true&w=majority&appName=TestingCluster')
db = client['mevo']
PatientsCollection = db['patients'] 
RoomsCollection = db['rooms'] 
NotificationsCollection = db['notifications'] 
DoctorsCollection = db['doctors'] 
UsersCollection = db['users'] 
MedicinesCollection = db['medicines'] 
recordsCollection = db['records']
connect_str = "DefaultEndpointsProtocol=https;AccountName=mevodrive;AccountKey=UKmeMgZao+Tn44MqV+lvNC1xUyN7x18469fXkxMSyW8geHPQXesKSgWv143dO4vhXbIuaD493SMw+AStQaMdBQ==;EndpointSuffix=core.windows.net"
container_name = "patientimagess"
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

BlobImages = []
BlobImagesEncodings = []
BlobImageNames = []

def save_base64_as_jpg(base64_string, output_file):
    image_bytes = base64.b64decode(base64_string)
    with open(output_file, "wb") as file:
        file.write(image_bytes)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif','webp'}

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
    if 'reference_image' not in request.files:
        return 'No file part'
    reference_image_file = request.files['reference_image']
    if reference_image_file.filename == '':
        return 'No selected file'
    reference_image_file.save('reference_image.jpg')
    reference_image = Image.open('reference_image.jpg')
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
                filename = os.path.basename(file)
                underscore_index = filename.find('_')
                if underscore_index == -1:
                    return None 
    
                extension_index = filename.find('.jpg')
                if extension_index == -1:
                    return None  

                patientID = filename[underscore_index + 1:extension_index]
                result = PatientsCollection.find_one({ "_id" : ObjectId(patientID) })
                result['_id'] = str(result['_id'])
                return jsonify(result) ,200

    return jsonify({'match': False})

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

@app.post('/signup')
def signup():
    user = request.get_json()
    id = UsersCollection.insert_one(user).inserted_id
    reesponse_data = { "message" : "Registered with id " + str(id) }
    return jsonify(reesponse_data),200

@app.post('/login')
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = UsersCollection.find_one( { "email" : email , "password" : password } )
    if user is not None:
        user['_id'] = str(user['_id'])
        return jsonify(user), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

@app.get('/GetDoctors')
def getDoctors():
    result = list(DoctorsCollection.find())
    for doc in result:
        doc['_id'] = str(doc['_id'])
    return jsonify(result)

@app.get('/GetRooms')
def getRooms():
    result = list(RoomsCollection.find())
    for doc in result:
        doc['_id'] = str(doc['_id'])
    return jsonify(result)

@app.get('/GetNotifications')
def getNotifications():
    result = list(NotificationsCollection.find())
    for doc in result:
        doc['_id'] = str(doc['_id'])
    return jsonify(result)

@app.post('/DeleteRoom')
def DeleteRoom():
    room = request.get_json()
    result = RoomsCollection.delete_one(room)
    if result.deleted_count > 0:
        print("A room document was deleted with the roomNo: ",room['roomNo'])
        obj = { 'message' : 'Room Deleted Successfully' }
        return jsonify(obj),200
    else:
        obj = { 'message' : 'Error while Deleting' }
        return jsonify(obj),200
        
@app.get('/GetPatients')
def getPatients():
    result = list(PatientsCollection.find())
    for doc in result:
        doc['_id'] = str(doc['_id'])
    return jsonify(result)

@app.post('/AddPatient')
def addPatient():
    patient = request.get_json()
    patient['_id'] = ObjectId()
    result = PatientsCollection.insert_one(patient)
    print("A Patient document was inserted with the _id: ",result.inserted_id)
    output_file = 'images/' + patient['PatientName'] + '_' + str(result.inserted_id) + '.jpg'
    save_base64_as_jpg(patient['PatientImage'],output_file)
    print("Image saved as: ",output_file)
    obj = { "message" : "Patient Added Successfully" }
    return jsonify(obj),200

@app.get('/GetMedicines')
def getMedicines():
    result = list(MedicinesCollection.find())
    for doc in result:
        doc['_id'] = str(doc['_id'])
    return jsonify(result)

@app.post('/AddMedicine')
def addMedicine():
    medicine = request.get_json()
    result = MedicinesCollection.insert_one(medicine)
    obj = { "message" : "Medicine inserted with id: " + str(result.inserted_id) }
    return jsonify(obj) ,200

@app.post('/DeletePatient')
def DeletePatient():
    patient = request.get_json()
    result = PatientsCollection.delete_one({ "_id" : ObjectId(patient['_id']) })
    if result.deleted_count > 0:
        print("A patient document was deleted with the id: ",patient['_id'])
        filepath = "images/" + patient['PatientName']+ '_' + str(patient['_id']) + '.jpg'
        os.remove(filepath)
        obj = { 'message' : 'Patient Deleted Successfully' }
        return jsonify(obj),200
    else:
        obj = { 'message' : 'Error while Deleting' }
        return jsonify(obj),400

@app.post('/EditRoom')
def editRoom():
    room = request.get_json()
    filter_criteria = {'roomNo': result['roomNo']}  
    update_operation = {'$set': {'isAvailable': result['isAvailable'] }}
    print("A Room document was updated by Room No: ",room['roomNo'])
    result = RoomsCollection.update_one(filter_criteria,update_operation)
    obj = { "message" : "Room Updated" }
    return jsonify(obj),200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')