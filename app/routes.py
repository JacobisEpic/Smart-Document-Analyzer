from flask import render_template, request, jsonify, redirect, url_for, session, send_file
from .database import Database
from werkzeug.utils import secure_filename
from bson import ObjectId

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

    # @app.route('/login', methods=['GET', 'POST'])
    # def login():
    #     if request.method == 'POST':
    #         username = request.form.get('username')
    #         password = request.form.get('password')
            
    #         if not username or not password:
    #             return jsonify({'success': False, 'message': 'Missing username or password'}), 400
            
    #         success, message = db.authenticate_user(username, password)
    #         if success:
    #             return redirect(url_for('upload_pdf'))
    #         else:
    #             return jsonify({'success': success, 'message': message}), 401
    #     return render_template('login.html')

    # @app.route('/upload_pdf', methods=['GET', 'POST'])
    # def upload_pdf():
    #     if request.method == 'POST':
    #         username = request.form.get('username')
    #         file = request.files.get('file')
            
    #         if not username or not file or file.filename == '':
    #             return jsonify({'success': False, 'message': 'Username and a valid PDF file are required'}), 400
    #         if not file.filename.endswith('.pdf'):
    #             return jsonify({'success': False, 'message': 'Invalid file type'}), 400
            
    #         filename = secure_filename(file.filename)
    #         file_content = file.read()  # Read the file content
            
    #         success, message = db.add_pdf_to_user(username, file_content, filename)
    #         return jsonify({'success': success, 'message': message}), (200 if success else 400)
    #     return render_template('upload_pdf.html')


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                return jsonify({'success': False, 'message': 'Missing username or password'}), 400
            
            success, message = db.authenticate_user(username, password)
            if success:
                session['username'] = username  # Store the username in the session
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
            file_content = file.read()  # Read the file content
            username = session['username']  # Retrieve the username from the session
            
            success, message = db.add_pdf_to_user(username, file_content, filename)
            return jsonify({'success': success, 'message': message}), (200 if success else 400)
        return render_template('upload_pdf.html')
    
    @app.route('/get_pdf/<pdf_id>')
    def get_pdf(pdf_id):
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'User not logged in'}), 401
        
        pdf_file = db.my_pdf(pdf_id)  # Fetch the PDF file using the provided method
        if pdf_file:
            return send_file(pdf_file, attachment_filename=pdf_file.filename, as_attachment=True)
        else:
            return jsonify({'success': False, 'message': 'PDF not found or invalid PDF ID'}), 404

    @app.route('/my_pdfs')
    def my_pdfs():
        if 'username' not in session:
            return jsonify({'success': False, 'message': 'User not logged in'}), 401

        username = session['username']
        pdfs = db.get_pdfs_for_user(username)  # Fetch all PDFs for the user
        if not pdfs:
            return jsonify({'success': False, 'message': 'No PDFs found for the user'}), 404
        
        return render_template('my_pdfs.html', pdfs=pdfs)