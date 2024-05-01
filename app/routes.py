from flask import render_template, request, jsonify, redirect, url_for, session, send_file
from werkzeug.utils import secure_filename
from .database import Database
import fitz  # PyMuPDF
import re
from collections import Counter
from nltk.corpus import stopwords
import nltk
from .database import Database
from .database import task_processor
from .DataProtection import sanitize_input, validate_username, validate_password


# Functions
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def extract_text_from_pdf(pdf_data):
    text = ""
    with fitz.open(stream=pdf_data, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def analyze_text(text):
    words = re.findall(r'\w+', text.lower())
    filtered_words = [word for word in words if word not in stop_words and len(word) > 1]
    word_counts = Counter(filtered_words)
    return dict(word_counts)


def configure_routes(app):
    db = Database()

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Sanitize inputs
            username = sanitize_input(username)
            password = sanitize_input(password)
            
            # Validate inputs
            valid_username, user_message = validate_username(username)
            valid_password, pass_message = validate_password(password)
            if not valid_username or not valid_password:
                return jsonify({'success': False, 'message': user_message if not valid_username else pass_message}), 400
            
            # Proceed with registration if validation is successful
            success, message = db.insert_user_login(username, password)
            if success:
                return redirect(url_for('register_success'))
            else:
                return jsonify({'success': success, 'message': message}), 400
        
        return render_template('register.html')


    @app.route('/register_success')
    def register_success():
        return render_template('register_success.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                return jsonify({'success': False, 'message': 'Missing username or password'}), 400
            
            success, message = db.authenticate_user(username, password)
            if success:
                session['username'] = username
                return redirect(url_for('upload_pdf'))
            else:
                return jsonify({'success': success, 'message': message}), 401
        return render_template('login.html')

    @app.route('/upload_pdf', methods=['GET', 'POST'])
    def upload_pdf():
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'User not logged in'}), 401
        if request.method == 'POST':
            file = request.files.get('file')
            if not file or file.filename == '':
                return jsonify({'success': False, 'message': 'A valid PDF file is required'}), 400
            if not file.filename.endswith('.pdf'):
                return jsonify({'success': False, 'message': 'Invalid file type'}), 400
            filename = secure_filename(file.filename)
            file_content = file.read()
            username = session['username']
            success, message, pdf_id = db.add_pdf_to_user(username, file_content, filename)
            return jsonify({'success': success, 'message': message}), 200 if success else 400
        return render_template('upload_pdf.html')
    
    @app.route('/get_pdf/<pdf_id>')
    def get_pdf(pdf_id):
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'User not logged in'}), 401
        pdf_file = db.get_pdf(pdf_id)
        if pdf_file:
            return send_file(pdf_file, as_attachment=False, mimetype='application/pdf')
        else:
            return jsonify({'success': False, 'message': 'PDF not found or invalid PDF ID'}), 404
   
    @app.route('/my_pdfs')
    def my_pdfs():
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'User not logged in'}), 401
        
        username = session['username']
        pdfs = db.get_pdfs_for_user(username)
        if not pdfs:
            return jsonify({'success': False, 'message': 'No PDFs found for the user'}), 404
        
        return render_template('my_pdfs.html', pdfs=pdfs)

    @app.route('/view_pdf/<pdf_id>')
    def view_pdf(pdf_id):
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'User not logged in'}), 401

        pdf_file = db.get_pdf(pdf_id)
        if not pdf_file:
            return jsonify({'success': False, 'message': 'PDF not found or invalid PDF ID'}), 404

        pdf_url = url_for('get_pdf', pdf_id=pdf_id)
        return render_template('view_pdf.html', pdf_url=pdf_url, filename=pdf_file.filename)
