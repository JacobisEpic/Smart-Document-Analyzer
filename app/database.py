from pymongo import MongoClient
import hashlib
from gridfs import GridFS
from bson.objectid import ObjectId
from threading import Thread
import queue
import time
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
            # Hash the provided password and compare with the stored one
            hashed_password = self.hash_password(password)
            if hashed_password == user['password']:
                return True, "Authentication successful."
            else:
                return False, "Incorrect password."
        else:
            return False, "User not found."
    # def add_pdf_to_user(self, username, pdf_path):
    #     user = self.users.find_one({'username': username})
    #     if not user:
    #         return False, "User not found."
        
    #     if 'pdfs' not in user:
    #         user['pdfs'] = []
        
    #     user['pdfs'].append(pdf_path)
    #     self.users.update_one({'_id': user['_id']}, {'$set': {'pdfs': user['pdfs']}})
    #     return True, "PDF added successfully."
            


    def add_pdf_to_user(self, username, pdf_data, filename):
        user = self.users.find_one({'username': username})
        if not user:
            return False, "User not found."
        
        # The content of the file is read and stored in GridFS.
        pdf_id = self.fs.put(pdf_data, filename=filename)
        
        # The reference to the file in GridFS is stored in the user's record.
        pdf_entry = {'pdf_id': pdf_id, 'filename': filename}
        if 'pdfs' not in user:
            user['pdfs'] = [pdf_entry]
        else:
            user['pdfs'].append(pdf_entry)
        pdf_id = self.fs.put(pdf_data, filename=filename)
        self.users.update_one({'_id': user['_id']}, {'$set': {'pdfs': user['pdfs']}})
        return True, "PDF stored in GridFS successfully.", str(pdf_id)

    def my_pdf(self, pdf_id):
        try:
            pdf_file = self.fs.get(ObjectId(pdf_id))
            return pdf_file
        except Exception as e:
            return None, "PDF not found or invalid PDF ID"

    # def get_pdfs_for_user(self, username):
    #     user = self.users.find_one({'username': username})
    #     if not user or 'pdfs' not in user:
    #         return []
    #     return user['pdfs']
    def get_pdfs_for_user(self, username):
        user = self.users.find_one({'username': username})
        if not user or 'pdfs' not in user:
            return []
        
        pdfs_with_analysis = []
        for pdf_entry in user['pdfs']:
            pdf_id = pdf_entry['pdf_id']
            analysis_result = self.get_pdf_analysis(pdf_id)
            pdf_entry['analysis'] = analysis_result
            pdfs_with_analysis.append(pdf_entry)
        
        return pdfs_with_analysis

    def save_pdf_analysis(self, pdf_id, analysis_results):
        """Store the analysis results for a PDF."""
        self.db.pdf_analysis.insert_one({'pdf_id': pdf_id, 'analysis': analysis_results})
        return True
    
    def get_pdf_analysis(self, pdf_id):
        result = self.db.pdf_analysis.find_one({'pdf_id': pdf_id})
        return result['analysis'] if result else {}


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
