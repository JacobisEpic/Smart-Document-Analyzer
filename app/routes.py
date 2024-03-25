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
            
            if not username or not password:
                return jsonify({'success': False, 'message': 'Missing username or password'}), 400
            
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
            if success:
                def process_pdf_task(file_content, pdf_id):
                    text = extract_text_from_pdf(file_content)
                    analysis_results = analyze_text(text)
                    db.save_pdf_analysis(pdf_id, analysis_results)

                task_processor.add_task(process_pdf_task, file_content, pdf_id)
            return jsonify({'success': success, 'message': message}), 200 if success else 400

        return render_template('upload_pdf.html')
    @app.route('/get_pdf/<pdf_id>')
    def get_pdf(pdf_id):
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'User not logged in'}), 401

        pdf_file = db.my_pdf(pdf_id)
        if pdf_file:
            # Note the corrected argument here is `filename=`, not `attachment_filename=`
            return send_file(pdf_file,
                            as_attachment=False,  # Serve inline
                            mimetype='application/pdf')  # Explicitly set the MIME type
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

        # Assuming my_pdf method returns the PDF file stream and filename
        pdf_file, filename = db.my_pdf(pdf_id)
        if not pdf_file:
            return jsonify({'success': False, 'message': 'PDF not found or invalid PDF ID'}), 404

        # Fetch the NLP analysis data for the PDF
        analysis_results = db.get_pdf_analysis(pdf_id)

        # Instead of sending the file directly, render a template passing the PDF URL for iframe and analysis results
        pdf_url = url_for('get_pdf', pdf_id=pdf_id)
        return render_template('view_pdf.html', pdf_url=pdf_url, analysis_results=analysis_results, filename=filename)
