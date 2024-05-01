from pymongo import MongoClient
import hashlib
from gridfs import GridFS
from bson.objectid import ObjectId
from threading import Thread
import queue
import time
import fitz 
from .DataProtection import sanitize_input, validate_username, validate_password
import requests
import os
# Use these functions as needed in your database operations

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
        pdf_text = self.extract_text_from_pdf(pdf_data)
        
        # Only pass the text to the function
        summary = self.summarize_text_with_chatgpt(pdf_text)
        
        pdf_entry = {'pdf_id': pdf_id, 'filename': filename, 'text': pdf_text, 'summary': summary}
        if 'pdfs' not in user:
            user['pdfs'] = [pdf_entry]
        else:
            user['pdfs'].append(pdf_entry)
        
        self.users.update_one({'_id': user['_id']}, {'$set': {'pdfs': user['pdfs']}})
        return True, "PDF stored in GridFS successfully.", str(pdf_id)

# This allow the use to receive text NLP Analysis
    def summarize_text_with_chatgpt(self, text):
        """Uses ChatGPT to generate a summary for the provided text."""
        # Load the API key from an environment variable
        api_key = 'KEY'
        if not api_key:
            raise ValueError("API key is not configured properly.")

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        data = {
            'model': 'gpt-3.5-turbo',  # Check if this model suits your needs
            'messages': [
                {'role': 'system', 'content': 'Summarize this text:'},
                {'role': 'user', 'content': text}
            ],
            'max_tokens': 150
        }
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        if response.status_code == 200:
            try:
                # Extracting the summary from the response JSON.
                return response.json()['choices'][0]['message']['content'].strip()
            except KeyError:
                # Handle possible KeyError if the response structure isn't as expected
                return "Error in extracting summary from the response."
        else:
            # Provide detailed information if the request fails
            return f"Failed to generate summary, status code {response.status_code}, response: {response.text}"


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
