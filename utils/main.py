from cover.library import *
from utils.oop import CameraManager
from utils.utils import check_and_reset_detections,capture_and_upload_image
from send_be.send_comunitication import send_alert_fire, send_alert_smoke

alerts = {}
warnings = {}

# Biến lưu trữ trạng thái cảnh báo
frist_fire = False 
frist_smoke = False
frist_behavior = False
camera_manager = CameraManager()

# Thêm các biến theo dõi thời gian phát hiện
fire_detection_start = 0
smoke_detection_start = 0
behavior_detection_start = 0
last_fire_time = 0
last_smoke_time = 0
last_behavior_time = 0

# Khởi động mô hình YOLO và thêm camera ngay khi ứng dụng bắt đầu
def start_yolo_and_cameras():
    try:
        # Đọc danh sách camera từ file txt
        with open('rtsp_urls.txt', 'r') as file:
            rtsp_urls = []
            for line in file:
                url = line.strip()
                if url:  # Kiểm tra url không rỗng
                    rtsp_urls.append(url)
        
        # Thêm từng camera vào camera manager
        for rtsp_url in rtsp_urls:
            camera_manager.add_camera(rtsp_url, rtsp_url)
            print(f"✅ Đã thêm camera với URL/ID: {rtsp_url}")
            
    except FileNotFoundError:
        print("❌ Không tìm thấy file rtsp_urls.txt")
        # Tạo file mới nếu chưa tồn tại
        with open('rtsp_urls.txt', 'w') as file:
            pass
    except Exception as e:
        print(f"❌ Lỗi khi khởi tạo camera: {str(e)}")

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
            
        results = camera_manager.model.predict(frame, imgsz=640, conf=0.7,verbose=False)
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
                        send_alert_smoke(camera.rtsp_url, "hanh_vi")
                        file_path = capture_and_upload_image(frame, "hanh_vi")
                        frist_behavior = True
                        last_behavior_time = current_time
        
                # class lửa
                elif c == 1:    
                    fire_detected = True
                    if fire_detection_start == 0:
                        fire_detection_start = current_time
                    elif not frist_fire and (current_time - fire_detection_start) >= 0.8:
                        file_path = capture_and_upload_image(frame, "lua")
                        send_alert_fire(camera.rtsp_url, "lua")
                        frist_fire = True
                        last_fire_time = current_time

                # class khói
                elif c == 2:  
                    smoke_detected = True
                    if smoke_detection_start == 0:
                        smoke_detection_start = current_time
                    elif not frist_smoke and (current_time - smoke_detection_start) >= 0.8:
                        file_path = capture_and_upload_image(frame, "khoi")
                        send_alert_smoke(camera.rtsp_url, "khoi")
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
        check_and_reset_detections(camera.rtsp_url)
            
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