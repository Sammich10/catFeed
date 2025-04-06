# Import the flask app and associated libraries 
from flask import(
    Blueprint, Flask, render_template, Response, request, jsonify, redirect, url_for, session
)
from functools import wraps
from .auth import login_required

# Import database libraries
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Import system libraries
import os, hashlib, time, threading, cv2
from PIL import Image

# Database models
from app.models import Feeding, FeedTime

# Global app runtime variable(s)
camera_mode = 0

# Create a blueprint for the app routes
bp = Blueprint('catfeedapp', __name__, url_prefix='/catfeedapp')

@bp.route("/home", methods=['GET'])
@login_required
def home():
    """
    Renders the home page for the user.
    
    Parameters:
        None
    
    Returns:
        The rendered home page
    """
    return render_template('app/app.html', title="Feed my cat", username=session['username'], version="v2.2.1" )


