"""
📦 GridFS Migration Script
Purpose:
  Scans all locally uploaded files under the static/uploads folder on disk and migrates them
  into MongoDB GridFS to prevent file loss on ephemeral hosting servers (like Render).
Connections:
  - app/storage.py: Operates on the same portfolioDB.fs GridFS collection.
  - .env: Reads the MONGO_URI variable to access the remote database cluster.
"""
import os
import mimetypes
import gridfs
from pymongo import MongoClient
from dotenv import load_dotenv

def migrate_local_files_to_gridfs():
    # Load environment variables
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("[ERROR] MONGO_URI not found in environment or .env file.")
        return

    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client["portfolioDB"]
    fs = gridfs.GridFS(db)

    # Base uploads folder
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "app", "static", "uploads"))
    if not os.path.exists(base_dir):
        print(f"[ERROR] Uploads directory does not exist at: {base_dir}")
        return

    print(f"[INFO] Scanning local files in: {base_dir}")
    
    uploaded_count = 0
    skipped_count = 0

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file == ".gitkeep":
                continue
                
            file_path = os.path.join(root, file)
            # Find the path relative to the uploads folder
            relative_path = os.path.relpath(file_path, base_dir)
            filename = file # Use the safe UUID filename stored in DB

            # Check if file is already in GridFS
            existing = fs.find_one({"filename": filename})
            if existing:
                print(f"[SKIP] File already exists in GridFS: {relative_path} ({filename})")
                skipped_count += 1
                continue

            # Load file and upload to GridFS
            try:
                content_type, _ = mimetypes.guess_type(file_path)
                if not content_type:
                    content_type = "application/octet-stream"

                with open(file_path, "rb") as f:
                    file_data = f.read()

                fs.put(file_data, filename=filename, content_type=content_type)
                print(f"[UPLOAD] Uploaded to GridFS: {relative_path} -> {filename} ({content_type})")
                uploaded_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to upload {relative_path}: {e}")

    print("\n--- Migration Complete ---")
    print(f"Successful Uploads: {uploaded_count}")
    print(f"Skipped (Already in GridFS): {skipped_count}")

if __name__ == "__main__":
    migrate_local_files_to_gridfs()
