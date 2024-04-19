import cv2
import numpy as np
import time
import datetime
from picamera2 import Picamera2
from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from home.models import Alerts

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (320, 180)}))


def video_feed():
    #time.sleep(5)
    prev_frame = None
    picam2.start()

    last_motion_time = time.time() - 10
    motion_started = False
    alert_saved = False
    alert_instance = None

    while True:
        frame = picam2.capture_array()

        current_time = time.time()
        current_time_str = datetime.datetime.fromtimestamp(current_time).strftime('%H:%M:%S')

        if prev_frame is not None:
            motion_detected = detect_motion(frame, prev_frame)

            if motion_detected and not motion_started and not alert_saved:
                print("Motion!")
                motion_started = True
                alert_instance = Alerts.objects.create(alertDate=datetime.date.today(), alertStartTime=current_time_str)                
                last_motion_time = current_time
                alert_saved = True
            
            if motion_detected and motion_started:
                last_motion_time = current_time

            if not motion_detected and motion_started:
                if current_time - last_motion_time >= 5:
                    print("Motion Ended!")
                    alert_instance.alertEndTime = current_time_str
                    alert_instance.save()
                    motion_started = False
                    alert_saved = False

        prev_frame = frame

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        _, jpeg = cv2.imencode('.jpg', frame_rgb)
        frame_bytes = jpeg.tobytes()
        yield(b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n') 


def detect_motion(frame, prev_frame):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

    # Compute absolute difference between frames
    frame_diff = cv2.absdiff(gray_frame, gray_prev_frame)

    # Apply threshold to the difference image
    _, thresholded_diff = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)

    # Calculate the percentage of non-zero pixels
    non_zero_ratio = np.count_nonzero(thresholded_diff) / (thresholded_diff.shape[0] * thresholded_diff.shape[1])

    # Set a threshold for the non-zero ratio to determine motion
    sensitivity_threshold = 0.02  # Adjust this threshold as needed

    motion_detected = non_zero_ratio > sensitivity_threshold

    return motion_detected


@gzip.gzip_page
def stream_video(request):
    return StreamingHttpResponse(video_feed(), content_type='multipart/x-mixed-replace; boundary=frame')


def home(request):
    alerts = Alerts.objects.all()
    context = {'alerts': alerts}
    return render(request, 'home.html', context)