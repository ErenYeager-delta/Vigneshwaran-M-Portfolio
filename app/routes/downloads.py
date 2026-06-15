"""
Download / Preview routes for resumes and certificates.
Files served securely from GridFS or local directory fallback.
"""

import os
from flask import Blueprint, send_from_directory, abort, redirect, current_app, request, Response
from app.models import Resume, Certificate, AppointmentLetter, Incentive, OfferLetter, PaySlip

downloads_bp = Blueprint("downloads", __name__)

def serve_gridfs_file_response(filename, as_attachment=False, download_name=None):
    """
    Helper to fetch a file from GridFS and compile a Flask Response.
    Returns None if the file is not in GridFS.
    """
    from app.storage import get_file
    grid_out = get_file(filename)
    if not grid_out:
        return None
        
    response = Response(grid_out.read(), mimetype=grid_out.content_type)
    
    # Configure Content-Disposition header
    disposition = "attachment" if as_attachment else "inline"
    if download_name:
        # Wrap filename in quotes to handle spaces/special characters safely
        response.headers["Content-Disposition"] = f'{disposition}; filename="{download_name}"'
    else:
        response.headers["Content-Disposition"] = f'{disposition}; filename="{filename}"'
        
    response.headers["Content-Length"] = grid_out.length
    return response


@downloads_bp.route("/resume/download")
def download_resume():
    """Download the active resume as an attachment."""
    resume_type = request.args.get("type")
    resume = Resume.find_active(resume_type)
    if not resume:
        abort(404)
        
    # 1. Try GridFS
    response = serve_gridfs_file_response(resume["filename"], as_attachment=True, download_name=resume["original_name"])
    if response:
        return response
        
    # 2. Fallback to Disk
    directory = os.path.join(current_app.config["UPLOAD_FOLDER"], "resumes")
    return send_from_directory(
        directory,
        resume["filename"],
        as_attachment=True,
        download_name=resume["original_name"],
    )


@downloads_bp.route("/resume/preview")
def preview_resume():
    """Preview the active resume in the browser."""
    resume_type = request.args.get("type")
    resume = Resume.find_active(resume_type)
    if not resume:
        abort(404)
        
    # 1. Try GridFS
    response = serve_gridfs_file_response(resume["filename"], as_attachment=False, download_name=resume["original_name"])
    if response:
        return response
        
    # 2. Fallback to Disk
    directory = os.path.join(current_app.config["UPLOAD_FOLDER"], "resumes")
    return send_from_directory(
        directory,
        resume["filename"],
        as_attachment=False,
    )


@downloads_bp.route("/certificate/<string:cert_id>/preview")
def preview_certificate(cert_id):
    """Preview a specific certificate file in the browser (for modal)."""
    cert = Certificate.find_by_id(cert_id)
    if not cert or not cert.get("filename"):
        abort(404)

    # 1. Try GridFS
    response = serve_gridfs_file_response(cert["filename"], as_attachment=False)
    if response:
        return response

    # 2. Fallback to Disk
    directory = os.path.join(current_app.config["UPLOAD_FOLDER"], "certificates")
    return send_from_directory(
        directory,
        cert["filename"],
        as_attachment=False,
    )


@downloads_bp.route("/certificate/<string:cert_id>/preview-image")
def preview_certificate_image(cert_id):
    """Preview a specific certificate's preview image in the browser (for modal)."""
    cert = Certificate.find_by_id(cert_id)
    if not cert or not cert.get("preview_image"):
        abort(404)

    preview = cert["preview_image"]

    # If it is an external URL, redirect the browser directly to it
    if preview.startswith(("http://", "https://")):
        return redirect(preview)

    # 1. Try GridFS
    response = serve_gridfs_file_response(preview, as_attachment=False)
    if response:
        return response

    # 2. Fallback to Disk
    directory = os.path.join(current_app.config["UPLOAD_FOLDER"], "certificates")
    return send_from_directory(
        directory,
        preview,
        as_attachment=False,
    )


@downloads_bp.route("/certificate/<string:cert_id>/download")
def download_certificate(cert_id):
    """Download a specific certificate file."""
    cert = Certificate.find_by_id(cert_id)
    if not cert or not cert.get("filename"):
        abort(404)

    download_name = f"{cert['title']}.{cert['filename'].rsplit('.', 1)[-1]}"

    # 1. Try GridFS
    response = serve_gridfs_file_response(cert["filename"], as_attachment=True, download_name=download_name)
    if response:
        return response

    # 2. Fallback to Disk
    directory = os.path.join(current_app.config["UPLOAD_FOLDER"], "certificates")
    return send_from_directory(
        directory,
        cert["filename"],
        as_attachment=True,
        download_name=download_name,
    )


@downloads_bp.route("/experience/appointment-letter/<string:letter_id>/preview")
def preview_appointment_letter(letter_id):
    """Preview a specific appointment letter PDF in the browser."""
    letter = AppointmentLetter.find_by_id(letter_id)
    if not letter:
        abort(404)
        
    # 1. Try GridFS
    response = serve_gridfs_file_response(letter["filename"], as_attachment=False, download_name=letter["original_name"])
    if response:
        return response

    # 2. Fallback to Disk
    directory = os.path.join(current_app.config["UPLOAD_FOLDER"], "appointment_letters")
    return send_from_directory(
        directory,
        letter["filename"],
        as_attachment=False,
    )


@downloads_bp.route("/experience/appointment-letter/<string:letter_id>/download")
def download_appointment_letter(letter_id):
    """Download a specific appointment letter PDF."""
    letter = AppointmentLetter.find_by_id(letter_id)
    if not letter:
        abort(404)
        
    # 1. Try GridFS
    response = serve_gridfs_file_response(letter["filename"], as_attachment=True, download_name=letter["original_name"])
    if response:
        return response

    # 2. Fallback to Disk
    directory = os.path.join(current_app.config["UPLOAD_FOLDER"], "appointment_letters")
    return send_from_directory(
        directory,
        letter["filename"],
        as_attachment=True,
        download_name=letter["original_name"],
    )


@downloads_bp.route("/experience/incentive/<string:inc_id>/preview")
def preview_incentive(inc_id):
    """Preview a specific incentive image in the browser."""
    incentive = Incentive.find_by_id(inc_id)
    if not incentive:
        abort(404)
        
    # 1. Try GridFS
    response = serve_gridfs_file_response(incentive["filename"], as_attachment=False, download_name=incentive["original_name"])
    if response:
        return response

    # 2. Fallback to Disk
    directory = os.path.join(current_app.config["UPLOAD_FOLDER"], "incentives")
    return send_from_directory(
        directory,
        incentive["filename"],
        as_attachment=False,
    )


@downloads_bp.route("/experience/incentive/<string:inc_id>/download")
def download_incentive(inc_id):
    """Download a specific incentive image file."""
    incentive = Incentive.find_by_id(inc_id)
    if not incentive:
        abort(404)
        
    # 1. Try GridFS
    response = serve_gridfs_file_response(incentive["filename"], as_attachment=True, download_name=incentive["original_name"])
    if response:
        return response

    # 2. Fallback to Disk
    directory = os.path.join(current_app.config["UPLOAD_FOLDER"], "incentives")
    return send_from_directory(
        directory,
        incentive["filename"],
        as_attachment=True,
        download_name=incentive["original_name"],
    )


@downloads_bp.route("/experience/offer-letter/<string:letter_id>/preview")
def preview_offer_letter(letter_id):
    """Preview a specific offer letter PDF in the browser."""
    letter = OfferLetter.find_by_id(letter_id)
    if not letter:
        abort(404)
        
    # 1. Try GridFS
    response = serve_gridfs_file_response(letter["filename"], as_attachment=False, download_name=letter["original_name"])
    if response:
        return response

    # 2. Fallback to Disk
    directory = os.path.join(current_app.config["UPLOAD_FOLDER"], "offer_letters")
    return send_from_directory(
        directory,
        letter["filename"],
        as_attachment=False,
    )


@downloads_bp.route("/experience/offer-letter/<string:letter_id>/download")
def download_offer_letter(letter_id):
    """Download a specific offer letter PDF."""
    letter = OfferLetter.find_by_id(letter_id)
    if not letter:
        abort(404)
        
    # 1. Try GridFS
    response = serve_gridfs_file_response(letter["filename"], as_attachment=True, download_name=letter["original_name"])
    if response:
        return response

    # 2. Fallback to Disk
    directory = os.path.join(current_app.config["UPLOAD_FOLDER"], "offer_letters")
    return send_from_directory(
        directory,
        letter["filename"],
        as_attachment=True,
        download_name=letter["original_name"],
    )


@downloads_bp.route("/experience/pay-slip/<string:slip_id>/preview")
def preview_pay_slip(slip_id):
    """Preview a specific pay slip PDF in the browser."""
    slip = PaySlip.find_by_id(slip_id)
    if not slip:
        abort(404)
        
    # 1. Try GridFS
    response = serve_gridfs_file_response(slip["filename"], as_attachment=False, download_name=slip["original_name"])
    if response:
        return response

    # 2. Fallback to Disk
    directory = os.path.join(current_app.config["UPLOAD_FOLDER"], "pay_slips")
    return send_from_directory(
        directory,
        slip["filename"],
        as_attachment=False,
    )


@downloads_bp.route("/experience/pay-slip/<string:slip_id>/download")
def download_pay_slip(slip_id):
    """Download a specific pay slip PDF."""
    slip = PaySlip.find_by_id(slip_id)
    if not slip:
        abort(404)
        
    # 1. Try GridFS
    response = serve_gridfs_file_response(slip["filename"], as_attachment=True, download_name=slip["original_name"])
    if response:
        return response

    # 2. Fallback to Disk
    directory = os.path.join(current_app.config["UPLOAD_FOLDER"], "pay_slips")
    return send_from_directory(
        directory,
        slip["filename"],
        as_attachment=True,
        download_name=slip["original_name"],
    )
