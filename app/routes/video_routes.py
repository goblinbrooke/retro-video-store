from flask import Blueprint, jsonify, request, abort, make_response
from app.models.video import Video
from app.models.customer import Customer
from app.models.rental import Rental
from app import db
from datetime import date

video_bp = Blueprint("video", __name__, url_prefix="/videos")

# Helper Function to validate videos
def validate_video(request_body):
    '''Helper Function to validate video request_body'''
    if "title" not in request_body or "release_date" not in request_body or "total_inventory" not in request_body:
        return jsonify({"details": "Request body must include title, release_date, and total_inventory."}), 400

# Get all Videos
@video_bp.route("", methods=["GET"])
def get_videos():
    videos = Video.query.all()
    videos_response = []
    for video in videos:
        videos_response.append(video.to_dict())
    return jsonify(videos_response), 200

# Post a Video
@video_bp.route("", methods=["POST"])
def create_video():
    request_body = request.get_json()

    if "title" not in request_body: 
        return jsonify({"details": "Request body must include title."}), 400
    elif "release_date" not in request_body:
        return jsonify({"details": "Request body must include release_date."}), 400
    elif "total_inventory" not in request_body:   
        return jsonify({"details": "Request body must include total_inventory."}), 400
    
    new_video = Video(
        title=request_body["title"],
        release_date=request_body["release_date"],
        total_inventory=request_body["total_inventory"]
    )

    db.session.add(new_video)
    db.session.commit()
    return jsonify(new_video.to_dict()), 201

# Get Video by ID
@video_bp.route("/<video_id>", methods=["GET"])
def get_video(video_id):
    try:
        video_id = int(video_id)
    except ValueError:
        return jsonify({"Error": "Video ID must be an integer."}), 400

    video = Video.query.get(video_id)
    if video is None:
        return jsonify({"message": f"Video {video_id} was not found"}), 404
    return jsonify(video.to_dict()), 200

# Update Video by ID
@video_bp.route("/<video_id>", methods=["PUT"])
def update_video(video_id):
    video_id = int(video_id)
    video = Video.query.get(video_id)
    if video is None:
        return jsonify({"message": f"Video {video_id} was not found"}), 404

    request_body = request.get_json()
    validated_video = validate_video(request_body)
    if validated_video is None:
        video.title = request_body["title"]
        video.release_date = request_body["release_date"]
        video.total_inventory = request_body["total_inventory"]
    else: 
        return validated_video #Rename
    db.session.commit()
    return jsonify(video.to_dict()), 200

# Delete Video by ID
@video_bp.route("/<video_id>", methods=["DELETE"])
def delete_video(video_id):
    video_id = int(video_id)
    video = Video.query.get(video_id)
    if video is None:
        return jsonify({"message": f"Video {video_id} was not found"}), 404
    
    if video.rentals:
        for rental in video.rentals:
            db.session.delete(rental)

    db.session.delete(video)
    db.session.commit()
    return jsonify({"id": video.video_id}), 200

# Get rentals for a video
@video_bp.route("/<vid_id>/rentals", methods=["GET"])
def get_video_rentals(vid_id):
    try:
        int(vid_id)
    except ValueError:
        return jsonify({"Error": "Video ID must be an integer."}), 400

    video = Video.query.get(vid_id)
    if video is None:
        return jsonify({"message": f"Video {vid_id} was not found"}), 404

    rentals = Rental.query.filter_by(video_id=vid_id).all()

    rentals_response = []
    for rental in rentals:
        customer = Customer.query.get(rental.customer_id)
        rentals_response.append({"name": customer.name})
    return jsonify(rentals_response), 200