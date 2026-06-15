"""
📦 Storage Module — MongoDB GridFS Interaction
Purpose:
  Handles raw binary file streams (resumes, certificates, appointment letters, pay slips, incentives) 
  uploaded from the admin dashboard and stores them in MongoDB GridFS.
Connections:
  - app/extensions.py: Utilizes get_mongo_db() to retrieve the active PyMongo database instance.
  - app/admin/*.py: Mapped inside admin upload handlers (resume.py, certificate.py, experience.py, etc.) to persist uploads.
  - app/routes/downloads.py: Queried in preview and download endpoints to retrieve stored binary streams from Atlas.
"""
import gridfs
import mimetypes
from app.extensions import get_mongo_db

def save_file(file_data, filename, content_type=None):
    """
    Saves binary data or a file stream to MongoDB GridFS.
    Avoids duplicate entries for the same filename.
    """
    db = get_mongo_db("portfolioDB")
    if db is None:
        return False
    
    fs = gridfs.GridFS(db)
    
    # Delete existing file with the same name to prevent duplicates
    existing = fs.find_one({"filename": filename})
    if existing:
        fs.delete(existing._id)
        
    # Guess mime type if not provided
    if not content_type:
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = "application/octet-stream"
            
    # Write to GridFS
    fs.put(file_data, filename=filename, content_type=content_type)
    return True

def get_file(filename):
    """
    Retrieves a file stream from MongoDB GridFS by filename.
    """
    db = get_mongo_db("portfolioDB")
    if db is None:
        return None
        
    fs = gridfs.GridFS(db)
    return fs.find_one({"filename": filename})

def delete_file(filename):
    """
    Deletes a file from MongoDB GridFS by filename.
    """
    db = get_mongo_db("portfolioDB")
    if db is None:
        return False
        
    fs = gridfs.GridFS(db)
    existing = fs.find_one({"filename": filename})
    if existing:
        fs.delete(existing._id)
        return True
    return False
