from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the request contains a file
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    # Check if the file is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Assuming it's an image file, you can save it to a directory
    file.save('uploads/' + file.filename)

    return jsonify({'message': 'File successfully uploaded'})



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
