from pymongo import MongoClient
import hashlib
from gridfs import GridFS
from bson.objectid import ObjectId


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
        
        self.users.update_one({'_id': user['_id']}, {'$set': {'pdfs': user['pdfs']}})
        return True, "PDF stored in GridFS successfully."

    def my_pdf(self, pdf_id):
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
