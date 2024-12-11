from cover.library import *
from utils.utils import check_and_reset_detections, save_detection_image
from send_be.send_comunitication import *
from utils.oop import  CameraManager, RTSPCameraThread


app = Flask(__name__)

alerts = {}
warnings = {}

# Biến lưu trữ trạng thái cảnh báo
frist_fire = False 
frist_smoke = False
frist_behavior = False

camera_manager = CameraManager()

# Luồng chạy camera chính
def generate_frames(camera_id):
    global frist_fire, frist_smoke, frist_behavior
    global last_fire_time, last_smoke_time, last_behavior_time
    global fire_detection_start, smoke_detection_start, behavior_detection_start

    camera = camera_manager.get_camera(camera_id)
    if not camera:
        return

    while True:
        frame = camera.read()
        if frame is None:
            continue
            
        results = camera_manager.model.predict(frame, imgsz=640, conf=0.55, verbose=False)
        current_time = time.time()
        
        # Kiểm tra phát hiện lửa và khói
        fire_detected = False
        smoke_detected = False
        bahavior_detected = False
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                c = box.cls
                # class hành vi thuốc lá
                if c == 0:  
                    bahavior_detected = True
                    if behavior_detection_start == 0:
                        behavior_detection_start = current_time
                    elif not frist_behavior and (current_time - behavior_detection_start) >= 0.8:
                        send_alert_smoke(camera.rtsp_url, "behavior")
                        save_detection_image(frame, "behavior")
                        frist_behavior = True
                        last_behavior_time = current_time
        
                # class lửa
                elif c == 1:    
                    fire_detected = True
                    if fire_detection_start == 0:
                        fire_detection_start = current_time
                    elif not frist_fire and (current_time - fire_detection_start) >= 0.8:
                        file_path = save_detection_image(frame, "fire")
                        send_alert_fire(camera.rtsp_url, "fire", file_path)
                        frist_fire = True
                        last_fire_time = current_time

                # class khói
                elif c == 2:  
                    smoke_detected = True
                    if smoke_detection_start == 0:
                        smoke_detection_start = current_time
                    elif not frist_smoke and (current_time - smoke_detection_start) >= 0.8:
                        file_path = save_detection_image(frame, "smoke")
                        send_alert_smoke(camera.rtsp_url, "smoke", file_path)
                        frist_smoke = True
                        last_smoke_time = current_time

            frame = r.plot()
            
        # Reset thời gian bắt đầu nếu không phát hiện
        if not bahavior_detected:
            behavior_detection_start = 0
        if not fire_detected:
            fire_detection_start = 0
        if not smoke_detected:
            smoke_detection_start = 0
            
        # Kiểm tra và reset các phát hiện
        check_and_reset_detections()
            
        # Cập nhật trạng thái cảnh báo
        alerts[camera_id] = {
            'rtsp_url': camera.rtsp_url,
            'has_fire': fire_detected,
        }
        warnings[camera_id] = {
            'rtsp_url': camera.rtsp_url,
            'has_smoke': smoke_detected,
            'has_behavior': bahavior_detected
        }
            
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    return Response(generate_frames(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')

# Gửi cảnh báo cháy 
@app.route('/check_alert/<camera_id>')
def check_alerts_fire(camera_id):
    alert_info = alerts.get(camera_id, {
        'rtsp_url': '',
        'has_fire': False,
    })

    note = []
    if alert_info['has_fire']:
        note.append("Phát hiện lửa")

    response = {
        "rtsp_url": alert_info['rtsp_url'],
        "note": ", ".join(note) if note else "none"
    }
    return jsonify(response)


# Gửi thông báo khói và hành vi thuốc lá
@app.route('/check_warning/<camera_id>')
def check_warning(camera_id):
    warning_info = warnings.get(camera_id, {
        'rtsp_url': '',
        'has_smoke': False,
        'has_behavior': False
    })
    note_smoke_behavior = []
    if warning_info['has_smoke']:
        note_smoke_behavior.append("Phát hiện khói")
    if warning_info['has_behavior']:
        note_smoke_behavior.append("Phát hiện hút thuốc lá")

    response = {
        "rtsp_url": warning_info['rtsp_url'],
        "note": ", ".join(note_smoke_behavior) if note_smoke_behavior else "none"
    }
    
    return jsonify(response)

@app.route('/')
def index():
    return render_template('index.html')

# Thêm route mới để nhận RTSP URL
@app.route('/api/update-rtsp/<url>', methods=['POST'])
def update_rtsp(url):
    try:
        # Lấy thông tin camera từ request
        data = request.get_json()
        camera_id = data.get('camera_id')
        rtsp_url = data.get('rtsp_url')
        
            
        # Thêm camera mới vào camera manager
        camera_manager.add_camera(camera_id, rtsp_url)
        print(f"✅ Đã thêm camera {camera_id} thành công")

    except Exception as e:
        print(f"❌ Lỗi khi cập nhật camera: {str(e)}")

# Xóa camera
@app.route('/api/delete-camera/<url_rtsp>', methods=['DELETE'])
def delete_camera(url_rtsp):
    try:
        # Lấy thông tin camera từ request
        data = request.get_json()
        url_rtsp = data.get('url_rtsp')

        # Kiểm tra camera có tồn tại không
        if url_rtsp in camera_manager.cameras:
            camera_manager.cameras[url_rtsp].stop()
            del camera_manager.cameras[url_rtsp]

            if url_rtsp in alerts:
                del alerts[url_rtsp]
            if url_rtsp in warnings:
                del warnings[url_rtsp]
                
            print(f"✅ Đã xóa camera {url_rtsp} thành công")
    except Exception as e:
        print(f"❌ Lỗi khi xóa camera: {str(e)}")

if __name__ == '__main__':
    # Thêm các camera RTSP
    rtsp_cameras = {
        'cam0': 'rtsp://admin:admin%40123@192.168.1.252:554/cam/realmonitor?channel=1&subtype=0',
        # 'cam1': 'rtsp://admin:password123@192.168.1.101:554/stream1',
        # 'cam2': 'rtsp://admin:password123@192.168.1.102:554/stream1'
    }
    
    for cam_id, rtsp_url in rtsp_cameras.items():
        camera_manager.add_camera(cam_id, rtsp_url)
        
    app.run(host='0.0.0.0', port=8000, threaded=True)