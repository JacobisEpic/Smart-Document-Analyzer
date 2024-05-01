from pymongo import MongoClient
import hashlib
from gridfs import GridFS
from bson.objectid import ObjectId
from threading import Thread
import queue
import time
import fitz 
# import feedparser
# from apscheduler.schedulers.background import BackgroundScheduler


class Database:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['user_database']
        self.users = self.db['users']
        self.fs = GridFS(self.db)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def insert_user_login(self, username, password):
        if self.users.find_one({'username': username}):
            return False, "Username already exists."
        hashed_password = self.hash_password(password)
        self.users.insert_one({'username': username, 'password': hashed_password})
        return True, "User added successfully."

    def authenticate_user(self, username, password):
        user = self.users.find_one({'username': username})
        if user:
            hashed_password = self.hash_password(password)
            if hashed_password == user['password']:
                return True, "Authentication successful."
            else:
                return False, "Incorrect password."
        else:
            return False, "User not found."

    # def add_pdf_to_user(self, username, pdf_data, filename):
    #     user = self.users.find_one({'username': username})
    #     if not user:
    #         return False, "User not found."
    #     pdf_id = self.fs.put(pdf_data, filename=filename)
    #     pdf_entry = {'pdf_id': pdf_id, 'filename': filename}
    #     if 'pdfs' not in user:
    #         user['pdfs'] = [pdf_entry]
    #     else:
    #         user['pdfs'].append(pdf_entry)
    #     self.users.update_one({'_id': user['_id']}, {'$set': {'pdfs': user['pdfs']}})
    #     return True, "PDF stored in GridFS successfully.", str(pdf_id)

    def add_pdf_to_user(self, username, pdf_data, filename):
        user = self.users.find_one({'username': username})
        if not user:
            return False, "User not found."
        
        pdf_id = self.fs.put(pdf_data, filename=filename)
        pdf_text = self.extract_text_from_pdf(pdf_data)  # Extract text from PDF
        
        pdf_entry = {'pdf_id': pdf_id, 'filename': filename, 'text': pdf_text}
        if 'pdfs' not in user:
            user['pdfs'] = [pdf_entry]
        else:
            user['pdfs'].append(pdf_entry)
        
        self.users.update_one({'_id': user['_id']}, {'$set': {'pdfs': user['pdfs']}})
        return True, "PDF stored in GridFS successfully.", str(pdf_id)
    
    def extract_text_from_pdf(self, pdf_data):
        text = ""
        with fitz.open(stream=pdf_data, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
        return text

    def get_pdf(self, pdf_id):
        try:
            pdf_file = self.fs.get(ObjectId(pdf_id))
            return pdf_file
        except Exception as e:
            return None, "PDF not found or invalid PDF ID"

    def get_pdfs_for_user(self, username):
        user = self.users.find_one({'username': username})
        if not user or 'pdfs' not in user:
            return []
        return user['pdfs']

# Queueing
class BackgroundTaskProcessor:
    def __init__(self, db):
        self.db = db
        self.task_queue = queue.Queue()
        self.thread = Thread(target=self.run, daemon=True)
        self.thread.start()

    def add_task(self, task, *args):
        self.task_queue.put((task, args))

    def run(self):
        while True:
            task, args = self.task_queue.get()
            try:
                task(*args)
            except Exception as e:
                print(f"Error processing task: {e}")
            finally:
                self.task_queue.task_done()

# Initialize the background task processor
task_processor = BackgroundTaskProcessor(Database())
