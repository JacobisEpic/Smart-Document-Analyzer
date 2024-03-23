# from flask import Flask, request, jsonify, send_from_directory
# from db import Database
# from werkzeug.utils import secure_filename
# import os
# from bson.objectid import ObjectId
# from gridfs import GridFS


from flask import Flask, request, jsonify, send_file, render_template
from app.database import Database
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
db = Database()

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route('/')
def home():
    return render_template('index.html')

# @app.route('/register', methods=['POST'])
# def register():
#     # data = request.get_json()
#     data = request.form.get()
#     username = data.get('username')
#     password = data.get('password')
    
#     if not username or not password:
#         return jsonify({'success': False, 'message': 'Missing username or password'}), 400
    
#     success, message = db.insert_user_login(username, password)
#     return jsonify({'success': success, 'message': message}), (200 if success else 400)

@app.route('/register', methods=['POST'])
def register():
    # Using form data instead of JSON
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Missing username or password'}), 400
    
    success, message = db.insert_user_login(username, password)
    return jsonify({'success': success, 'message': message}), (200 if success else 400)



# @app.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     username = data.get('username')
#     password = data.get('password')
    
#     if not username or not password:
#         return jsonify({'success': False, 'message': 'Missing username or password'}), 400
    
#     success, message = db.authenticate_user(username, password)
#     return jsonify({'success': success, 'message': message}), (200 if success else 401)

@app.route('/login', methods=['POST'])
def login():
    # Using form data instead of JSON
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Missing username or password'}), 400
    
    success, message = db.authenticate_user(username, password)
    return jsonify({'success': success, 'message': message}), (200 if success else 401)



# @app.route('/upload_pdf', methods=['POST'])
# def upload_pdf():
#     if 'file' not in request.files:
#         return jsonify({'success': False, 'message': 'No file part'}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({'success': False, 'message': 'No selected file'}), 400
#     if file and file.filename.endswith('.pdf'):
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)
        
#         # Assuming you have a method to get the current user's username
#         username = "current_user"
#         success, message = db.add_pdf_to_user(username, filepath)
#         return jsonify({'success': success, 'message': message}), (200 if success else 400)
#     else:
#         return jsonify({'success': False, 'message': 'Invalid file type'}), 400
    
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    username = request.form.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Username is required'}), 400

    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'}), 400
    if not file.filename.endswith('.pdf'):
        return jsonify({'success': False, 'message': 'Invalid file type'}), 400

    filename = secure_filename(file.filename)
    file_content = file.read()  # Read the file content

    success, message = db.add_pdf_to_user(username, file_content, filename)
    return jsonify({'success': success, 'message': message}), (200 if success else 400)

@app.route('/get_pdf/<pdf_id>', methods=['GET'])
def get_pdf(pdf_id):
    # This calls the get_pdf method of the Database class.
    result = db.get_pdf(pdf_id)
    if isinstance(result, tuple):  # This is checking if the result is an error.
        return result
    else:
        return send_file(
            result,
            mimetype='application/pdf',
            as_attachment=True,
            attachment_filename=result.filename
        )
    
if __name__ == '__main__':
    app.run(debug=True)