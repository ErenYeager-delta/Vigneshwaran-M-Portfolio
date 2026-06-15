"""
🗄️ Database Models Module — Data Access Layer (ORM/abstractions)
Purpose:
  Abstrates all database operations, providing simple query methods for dynamic collections:
  Resumes, Certificates, Platforms, Projects, AdminLoginAttempts, VerifiedUsers, ProjectBriefs,
  AppointmentLetters, Incentives, OfferLetters, PaySlips, and CompanyExperiences.
Connections:
  - app/extensions.py: Imports get_mongo_db() to target collections dynamically in portfolioDB or otpDB.
  - app/routes/*.py: Fetches active resume files, visible certificates, and projects to show on the public homepage.
  - app/admin/*.py: Updates or deletes models during dashboard management actions.
"""
import json
import hashlib
from datetime import datetime, timezone
from bson import ObjectId
from app.extensions import get_mongo_db

class MongoModel:
    """Base class for MongoDB-backed models."""
    database_name = "portfolioDB"
    collection_name = None

    @classmethod
    def get_collection(cls):
        db = get_mongo_db(cls.database_name)
        if db is None:
            return None
        return db[cls.collection_name]

    @classmethod
    def find_all(cls, sort_key="uploaded_at", descending=True):
        col = cls.get_collection()
        if col is None: return []
        sort_dir = -1 if descending else 1
        return list(col.find().sort(sort_key, sort_dir))

    @classmethod
    def find_by_id(cls, oid):
        col = cls.get_collection()
        if col is None: return None
        return col.find_one({"_id": ObjectId(oid)})

    @classmethod
    def delete_by_id(cls, oid):
        col = cls.get_collection()
        if col is None: return False
        col.delete_one({"_id": ObjectId(oid)})
        return True


class Resume(MongoModel):
    collection_name = "resumes"

    @classmethod
    def find_active(cls, resume_type=None):
        col = cls.get_collection()
        if col is None: return None
        query = {"is_active": True}
        if resume_type:
            query["resume_type"] = resume_type
        return col.find_one(query)

    @classmethod
    def deactivate_all(cls, resume_type=None):
        col = cls.get_collection()
        if col is not None:
            query = {}
            if resume_type:
                query["resume_type"] = resume_type
            col.update_many(query, {"$set": {"is_active": False}})

    @classmethod
    def add(cls, filename, original_name, file_hash, resume_type="it"):
        cls.deactivate_all(resume_type)
        col = cls.get_collection()
        if col is not None:
            col.insert_one({
                "filename": filename,
                "original_name": original_name,
                "file_hash": file_hash,
                "resume_type": resume_type,
                "is_active": True,
                "uploaded_at": datetime.now(timezone.utc)
            })

    @staticmethod
    def compute_hash(file_data: bytes) -> str:
        return hashlib.sha256(file_data).hexdigest()


class Certificate(MongoModel):
    collection_name = "certificates"

    @classmethod
    def find_active(cls):
        col = cls.get_collection()
        if col is None: return []
        return list(col.find({"is_active": True}).sort("uploaded_at", -1))

    @classmethod
    def add(cls, title, issuer, date_issued, description, link, filename, tags, preview_image=None):
        col = cls.get_collection()
        if col is not None:
            col.insert_one({
                "title": title,
                "issuer": issuer,
                "date_issued": date_issued,
                "description": description,
                "link": link,
                "filename": filename,
                "preview_image": preview_image,
                "tags": tags,
                "is_active": True,
                "uploaded_at": datetime.now(timezone.utc)
            })


class Platform(MongoModel):
    collection_name = "platforms"

    @classmethod
    def find_visible(cls):
        col = cls.get_collection()
        if col is None: return []
        return list(col.find({"visible": {"$in": [True, 1, "1"]}}).sort("name", 1))

    @classmethod
    def add(cls, name, url, icon_class):
        col = cls.get_collection()
        if col is not None:
            col.insert_one({
                "name": name,
                "url": url,
                "icon_class": icon_class,
                "visible": True,
                "created_at": datetime.now(timezone.utc)
            })


class Project(MongoModel):
    collection_name = "projects"

    @classmethod
    def find_all(cls, sort_key="created_at", descending=True):
        col = cls.get_collection()
        if col is None: return []
        sort_dir = -1 if descending else 1
        return list(col.find().sort(sort_key, sort_dir))

    @classmethod
    def find_visible(cls):
        col = cls.get_collection()
        if col is None: return []
        return list(col.find({"visible": {"$in": [True, 1, "1"]}}).sort("created_at", -1))

    @classmethod
    def add(cls, title, category, project_type, date_completed, image_url, source_code_link,
            deployment_link, description, problem_statement, solution_approach, key_metrics,
            tags, colab_link=None, ds_metrics=None, notebook_url=None, highlight_tag=None):
        col = cls.get_collection()
        if col is not None:
            col.insert_one({
                "title": title,
                "category": category,
                "project_type": project_type,
                "date_completed": date_completed,
                "image_url": image_url,
                "source_code_link": source_code_link,
                "deployment_link": deployment_link,
                "colab_link": colab_link,
                "description": description,
                "problem_statement": problem_statement,
                "solution_approach": solution_approach,
                "key_metrics": key_metrics,
                "tags": tags,
                "highlight_tag": highlight_tag or "",
                # Data Science specific fields
                "ds_metrics": ds_metrics or {},   # e.g. {"accuracy": "94.5%", "f1_score": "0.92"}
                "notebook_url": notebook_url or "",  # nbviewer or direct Colab share URL
                "visible": True,
                "created_at": datetime.now(timezone.utc)
            })


class AdminLoginAttempt(MongoModel):
    collection_name = "admin_login_attempts"

    @classmethod
    def record(cls, ip, success):
        col = cls.get_collection()
        if col is not None:
            col.insert_one({
                "ip_address": ip,
                "success": success,
                "attempted_at": datetime.now(timezone.utc)
            })


class VerifiedUser(MongoModel):
    database_name = "otpDB"
    collection_name = "verified_users"

    @classmethod
    def find_by_mobile(cls, mobile):
        col = cls.get_collection()
        if col is None: return None
        return col.find_one({"mobile": mobile})

    @classmethod
    def find_by_email(cls, email):
        col = cls.get_collection()
        if col is None: return None
        return col.find_one({"email": email})

    @classmethod
    def add(cls, name, email, mobile):
        col = cls.get_collection()
        if col is not None:
            col.insert_one({
                "name": name,
                "email": email,
                "mobile": mobile,
                "verified_at": datetime.now(timezone.utc).isoformat(),
            })


class ProjectBrief(MongoModel):
    database_name = "otpDB"
    collection_name = "verified_users"

    @classmethod
    def find_brief_by_email(cls, email):
        col = cls.get_collection()
        if col is None: return None
        return col.find_one({"email": email, "type": "direct_message"})

    @classmethod
    def add_brief(cls, name, email, message):
        col = cls.get_collection()
        if col is not None:
            col.insert_one({
                "type": "direct_message",
                "name": name,
                "email": email,
                "message": message,
                "sent_at": datetime.now(timezone.utc).isoformat()
            })


class AppointmentLetter(MongoModel):
    collection_name = "appointment_letters"

    @classmethod
    def find_all(cls):
        col = cls.get_collection()
        if col is None: return []
        return list(col.find().sort("uploaded_at", -1))

    @classmethod
    def find_by_company(cls, company):
        col = cls.get_collection()
        if col is None: return None
        return col.find_one({"company": company, "is_active": True})

    @classmethod
    def add(cls, filename, original_name, company):
        col = cls.get_collection()
        if col is not None:
            # Deactivate previous active letters for this company
            col.update_many({"company": company}, {"$set": {"is_active": False}})
            col.insert_one({
                "filename": filename,
                "original_name": original_name,
                "company": company,
                "is_active": True,
                "uploaded_at": datetime.now(timezone.utc)
            })


class Incentive(MongoModel):
    collection_name = "incentives"

    @classmethod
    def find_all(cls):
        col = cls.get_collection()
        if col is None: return []
        return list(col.find().sort("uploaded_at", -1))

    @classmethod
    def find_active_by_company(cls, company):
        col = cls.get_collection()
        if col is None: return []
        return list(col.find({"company": company, "is_active": True}).sort("order", 1))

    @classmethod
    def add(cls, filename, original_name, company, order=0):
        col = cls.get_collection()
        if col is not None:
            col.insert_one({
                "filename": filename,
                "original_name": original_name,
                "company": company,
                "order": int(order),
                "is_active": True,
                "uploaded_at": datetime.now(timezone.utc)
            })


class OfferLetter(MongoModel):
    collection_name = "offer_letters"

    @classmethod
    def find_all(cls):
        col = cls.get_collection()
        if col is None: return []
        return list(col.find().sort("uploaded_at", -1))

    @classmethod
    def find_by_company(cls, company):
        col = cls.get_collection()
        if col is None: return None
        return col.find_one({"company": company, "is_active": True})

    @classmethod
    def add(cls, filename, original_name, company):
        col = cls.get_collection()
        if col is not None:
            # Deactivate previous active letters for this company
            col.update_many({"company": company}, {"$set": {"is_active": False}})
            col.insert_one({
                "filename": filename,
                "original_name": original_name,
                "company": company,
                "is_active": True,
                "uploaded_at": datetime.now(timezone.utc)
            })


class PaySlip(MongoModel):
    collection_name = "pay_slips"

    @classmethod
    def find_all(cls):
        col = cls.get_collection()
        if col is None: return []
        return list(col.find().sort("uploaded_at", -1))

    @classmethod
    def find_by_company(cls, company):
        col = cls.get_collection()
        if col is None: return None
        return col.find_one({"company": company, "is_active": True})

    @classmethod
    def add(cls, filename, original_name, company):
        col = cls.get_collection()
        if col is not None:
            # Deactivate previous active slips for this company
            col.update_many({"company": company}, {"$set": {"is_active": False}})
            col.insert_one({
                "filename": filename,
                "original_name": original_name,
                "company": company,
                "is_active": True,
                "uploaded_at": datetime.now(timezone.utc)
            })


class CompanyExperience(MongoModel):
    collection_name = "company_experiences"

    @classmethod
    def find_all_ordered(cls):
        col = cls.get_collection()
        if col is None: return []
        return list(col.find().sort("sort_order", 1))

    @classmethod
    def find_by_slug(cls, slug):
        col = cls.get_collection()
        if col is None: return None
        return col.find_one({"slug": slug})

    @classmethod
    def add(cls, name, slug, metric_type, sort_order=1,
            role_title="", duration="", location="",
            description="", bullets=None, skills=None):
        col = cls.get_collection()
        if col is not None:
            if col.find_one({"slug": slug}):
                return None
            doc = {
                "name": name,
                "slug": slug,
                "role_title": role_title,
                "duration": duration,
                "location": location,
                "description": description,
                "bullets": bullets or [],
                "skills": skills or [],
                "metric_type": metric_type,
                "sort_order": int(sort_order),
                "months": [],
                "products": [],
                "created_at": datetime.now(timezone.utc)
            }
            res = col.insert_one(doc)
            doc["_id"] = res.inserted_id
            return doc
        return None

    @classmethod
    def update_by_id(cls, oid, data):
        col = cls.get_collection()
        if col is not None:
            col.update_one({"_id": ObjectId(oid)}, {"$set": data})
            return True
        return False
