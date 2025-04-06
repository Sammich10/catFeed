from flask import(
    Blueprint, Flask, render_template, Response, request, jsonify, redirect, url_for, session
)
from functools import wraps
from app import get_db, get_camera, get_motor, get_distance_sensor
from .auth import login_required
from app.models import Feeding, FeedTime
import time, threading, cv2

from hardware import DCMotor, distanceSensor

bp = Blueprint('api', __name__, url_prefix='/api')
camera_mode = 0

@bp.route("/getFeedingTimes", methods=['GET'])
@login_required
def getFeedingTimes():
    """
    API endpoint to get all feeding times recorded in the database.
    
    Parameters:
        None
    
    Returns:
        A JSON object containing all feeding times recorded in the database.
    """
    # Get all recorded  from the database, order by date first then time.
    feeding_times = Feeding.query.order_by(Feeding.date, Feeding.time).all()
    feeding_times_list = []
    # Convert the feeding times to a list of tuples
    for feeding_time in feeding_times:
        feeding_times_list.append((feeding_time.date, feeding_time.time, feeding_time.type, feeding_time.size)) 
    # Return a JSON object containing the list of feeding times
    return jsonify({'feeding_times': feeding_times_list})

@bp.route("/getFeedTimes", methods=['GET'])
@login_required
def getFeedTimes():
    """
    API endpoint to get all scheduled feed times that currently exist in the database.
    
    Parameters:
        None
        
    Returns:
        A JSON object containing all scheduled feed times that currently exist in the database
    """
    feed_times = FeedTime.query.all()
    feed_times_list = []
    for feed_time in feed_times:
        feed_times_list.append((feed_time.time, feed_time.type, feed_time.size))
    print(feed_times_list)
    return jsonify({'feed_times': feed_times_list})

@bp.route("/videoFeed")
@login_required
def videoFeed():
    """
    API endpoint to start the live video feed.
    
    Parameters:
        None
    
    Returns:
        A response object containing the live video feed.
    """
    if get_camera() is None:
        # Return an error message
        return Response("Camera not found", status=500)
    print("Starting live video feed")
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Initialize camera using libcamera (OpenCV interface)

def processFrame(frame_raw, setting):
    """
    Processes the raw frame and returns the processed frame.
    
    Parameters:
        frame_raw: the raw frame
        setting: the processing setting
        
    Returns:
        the processed frame
    """
    if setting == 0:
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2GRAY)
        return gray 
    if setting == 1:
        # Convert the frame to YUV
        frame_yuv = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2YUV)
        frame_y = frame_yuv[:, :, 0]
        frame_y_bilateral = cv2.bilateralFilter(frame_y, 5, 150, 150)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        frame_processed = clahe.apply(frame_y_bilateral)
        return frame_processed
    if setting == 2:
        # Convert the frame to RGB
        rgb = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2RGB)
        return rgb

def gen_frames():
    """
    Generates frames for the live video feed.
    
    Parameters:
        None
    
    Returns:
        A response object containing the live video feed.
    """
    global camera_mode
    print("Generating frames. Camera mode: " + str(camera_mode))
    try:
        cam = get_camera()
        # Start the camera feed
        while True:
            # Capture the raw frame from the Pi Camera
            frame_raw = cam.camera.capture_array()
            # TODO: Configurable rotation
            frame_raw = cv2.flip(frame_raw, 0)
            # Perform processing
            frame_processed = processFrame(frame_raw, camera_mode)
            # Convert the processed and rotated frame to a JPEG image
            _, jpeg = cv2.imencode('.jpg', frame_processed)
            # Convert the JPEG image to bytes
            frame = jpeg.tobytes()
            # Yield the frame in MJPEG format
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except Exception as e:
        print(e)

@bp.route("/manualFeed", methods=['POST'])
@login_required
def manualFeed():
    """
    API endpoint to manually trigger a feeding.
    
    Parameters:
        None
    
    Returns:
        A response object containing the result of the manual feed.
    """
    if request.method == 'POST':
        m = get_motor()
        db = get_db()
        if m is None:
            # Return an error message
            return Response("Motor not configured or not found", status=500)
        # Parse the JSON response
        data = request.get_json()
        print(data)
        # Get the time and type from the JSON response
        size = data['size']
        if size is None:
            return Response("error, no size parameter for manual feed", status=500)
        sizeInt = int(size)
        # Run the motor in a separate thread and return a success response immediately
        t1 = threading.Thread(target=m.forward, args=(sizeInt*3,)).start()
        # Add the feed record to the database
        new_feeding = Feeding(time = time.strftime("%H:%M"), type = 0, date = time.strftime("%Y-%m-%d"), size = sizeInt)
        db.session.add(new_feeding)
        db.session.commit()
        return Response("Success", status=200)
    else:
        return Response("Error", status=500)
    
@bp.route("/toggleCamera", methods=['POST'])
@login_required
def toggleCamera():
    """
    API endpoint to toggle the camera mode.
    
    Parameters:
        None
    
    Returns:
        A response object containing the result of the camera toggle.
    """
    if request.method == 'POST':
        cam = get_camera()
        if cam is None:
            # Return an error message
            return Response("Camera not found", status=500)
        global camera_mode
        if camera_mode + 1 > 2:
            camera_mode = 0
        else:
            camera_mode += 1
        print(camera_mode)
        return Response("Success", status=200)
    else:
        return Response("Error", status=500)

@bp.route("/addFeedTime", methods=['POST'])
@login_required
def addFeedTime():
    """
    API endpoint to add a feed time to the database.
    
    Parameters:
        None
    
    Returns:
        A response object containing the result of the feed time addition.
    """
    if request.method == 'POST':
        # Parse the JSON response
        data = request.get_json()
        print(data)
        # Get the time and type from the JSON response
        timeStr = data['time']
        if time is None:
            return Response("error, no time parameter", status=500)
        type = data['type']
        if type is None:
            return Response("error, no type parameter", status=500)
        typeInt = int(type)
        size = data['size']
        if size is None:
            return Response("error, no size parameter", status=500)
        sizeInt = int(size)
        # Add the feed time record to the database
        new_feedtime = FeedTime(time = timeStr, type = typeInt, size = sizeInt)
        db = get_db()
        db.session.add(new_feedtime)
        db.session.commit()
        return Response("Success", status=200)
    
@bp.route("/deleteFeedTime", methods=['POST'])
@login_required
def deleteFeedTime():
    """
    API endpoint to delete a feed time from the database.
    
    Parameters:
        None
    
    Returns:
        A response object containing the result of the feed time deletion.
    """
    if request.method == 'POST':
        # Parse the JSON response
        data = request.get_json()
        print(data)
        # Get the time and type from the JSON response
        timeStr = data['time']
        if time is None:
            return Response("Error", status=500)
        # Delete the feed time record from the database
        feedtime = FeedTime.query.filter_by(time = timeStr).first()
        db = get_db()
        db.session.delete(feedtime)
        db.session.commit()
        return Response("Success", status=200)
    
@bp.route("/getDistance", methods=['GET'])
@login_required
def getDistance():
    """
    Returns the distance reading from the food distance sensor. If the sensor is not
    initialized or enabled, an error message is returned.
    
    Parameters:
        None
    
    Returns:
        A JSON object containing the distance reading.
    """
    sens = get_distance_sensor()
    if sens is None:
        # Return an error message if the food distance sensor is not initialized or not enabled
        return jsonify({'distance': "Sensor not available"})
    distance_percent = sens.getReading_percent()
    # Round to the nearest 5%
    distance_percent = round(distance_percent/20)*20
    print(distance_percent)
    return jsonify({'distance': distance_percent})

@bp.route("/getLastFeed", methods=['GET'])
@login_required
def getLastFeed():
    """
    API endpoint to get the last feed recorded in the database.
    
    Parameters:
        None
    
    Returns:
        A JSON object containing the last feed recorded in the database.
    """
    last_feed = Feeding.query.order_by(Feeding.time.desc()).first()
    if last_feed == None:
        last_feed = ""
    else:
        last_feed = (last_feed.time, last_feed.date)
    print(last_feed)
    return jsonify({'last_feed': last_feed})

