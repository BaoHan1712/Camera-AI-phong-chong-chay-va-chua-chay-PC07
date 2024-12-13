from cover.library import *
from utils.oop import CameraManager
from utils.utils import check_and_reset_detections,capture_and_upload_image
from send_be.send_comunitication import send_alert_fire, send_alert_smoke

alerts = {}
warnings = {}

# Hằng số cho delay giữa các lần gửi và thời gian phát hiện
SEND_DELAY = 25  # 25 giây
DETECTION_THRESHOLD = 1  # 1 giây

# Thời điểm gửi cảnh báo cuối cùng
last_fire_send = 0
last_smoke_send = 0 
last_behavior_send = 0

# Thời điểm bắt đầu phát hiện
fire_start_time = 0
smoke_start_time = 0
behavior_start_time = 0

camera_manager = CameraManager()

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
        with open('rtsp_urls.txt', 'w') as file:
            pass
    except Exception as e:
        print(f"❌ Lỗi khi khởi tạo camera: {str(e)}")

# Luồng chạy camera chính
def generate_frames(camera_id):
    global last_fire_send, last_smoke_send, last_behavior_send
    global fire_start_time, smoke_start_time, behavior_start_time
    
    camera = camera_manager.get_camera(camera_id)
    if not camera:
        return
        
    while True:
        frame = camera.read()
        if frame is None:
            continue
            
        results = camera_manager.model.predict(frame, imgsz=640, conf=0.6, verbose=False)
        current_time = time.time()
        
        fire_detected = False
        smoke_detected = False
        behavior_detected = False
        
        for r in results:
            boxes = r.boxes
  
            for box in boxes:
                c = box.cls
                
                # Phát hiện hành vi hút thuốc
                if c == 0:
                    behavior_detected = True
                    if behavior_start_time == 0:
                        behavior_start_time = current_time
                    elif (current_time - behavior_start_time >= DETECTION_THRESHOLD and 
                          current_time - last_behavior_send >= SEND_DELAY):
                        file_path = capture_and_upload_image(frame, "hanh_vi")
                        send_alert_smoke(camera.rtsp_url, "hanh_vi")
                        last_behavior_send = current_time
                
                # Phát hiện lửa        
                elif c == 1:
                    fire_detected = True
                    if fire_start_time == 0:
                        fire_start_time = current_time
                    elif (current_time - fire_start_time >= DETECTION_THRESHOLD and 
                          current_time - last_fire_send >= SEND_DELAY):
                        file_path = capture_and_upload_image(frame, "lua")
                        send_alert_fire(camera.rtsp_url, "lua") 
                        last_fire_send = current_time
                
                # Phát hiện khói
                elif c == 2:
                    smoke_detected = True
                    if smoke_start_time == 0:
                        smoke_start_time = current_time
                    elif (current_time - smoke_start_time >= DETECTION_THRESHOLD and 
                          current_time - last_smoke_send >= SEND_DELAY):
                        file_path = capture_and_upload_image(frame, "khoi")
                        send_alert_smoke(camera.rtsp_url, "khoi")
                        last_smoke_send = current_time

            frame = r.plot()
            
        # Reset thời gian bắt đầu nếu không phát hiện
        if not behavior_detected:
            behavior_start_time = 0
        if not fire_detected:
            fire_start_time = 0
        if not smoke_detected:
            smoke_start_time = 0
            
        # Cập nhật trạng thái cảnh báo
        alerts[camera_id] = {
            'rtsp_url': camera.rtsp_url,
            'has_fire': fire_detected,
        }
        warnings[camera_id] = {
            'rtsp_url': camera.rtsp_url,
            'has_smoke': smoke_detected,
            'has_behavior': behavior_detected
        }
            
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

