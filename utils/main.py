from cover.library import *
from utils.oop import CameraManager
from utils.utils import capture_and_upload_image
from send_be.send_comunitication import send_alert_fire, send_alert_smoke

alerts = {}
warnings = {}

# Hằng số cho delay giữa các lần gửi và thời gian phát hiện
SEND_DELAY = 10  # 10 giây
DETECTION_THRESHOLD = 0.7  # 0.6 giây

# Dictionary lưu trữ thông tin cho từng camera
camera_states = {}

camera_manager = CameraManager()

def init_camera_state(camera_id):
    camera_states[camera_id] = {
        'last_fire_send': 0,
        'last_smoke_send': 0,
        'last_behavior_send': 0,
        'fire_start_time': 0,
        'smoke_start_time': 0,
        'behavior_start_time': 0
    }

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
    # Khởi tạo state cho camera nếu chưa có
    if camera_id not in camera_states:
        init_camera_state(camera_id)
    
    state = camera_states[camera_id]
    camera = camera_manager.get_camera(camera_id)
    if not camera:
        return
        
    while True:
        frame = camera.read()
        if frame is None:
            continue
            
        results = camera_manager.model.predict(frame, imgsz=640, conf=0.5, verbose=False)
        current_time = time.time()
        
        fire_detected = False
        smoke_detected = False
        behavior_detected = False
        
        frame_to_process = frame.copy()
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                c = box.cls
                
                # Phát hiện hành vi hút thuốc
                if c == 0:
                    behavior_detected = True
                    if state['behavior_start_time'] == 0:
                        state['behavior_start_time'] = current_time
                    elif (current_time - state['behavior_start_time'] >= DETECTION_THRESHOLD and 
                          current_time - state['last_behavior_send'] >= SEND_DELAY):
                        try:
                            file_path = capture_and_upload_image(frame_to_process, "hanh_vi")
                            if file_path:
                                send_alert_smoke(camera.rtsp_url, "hanh_vi")
                                state['last_behavior_send'] = current_time
                        except Exception as e:
                            print(f"Lỗi xử lý hành vi camera {camera_id}: {str(e)}")
                
                # Phát hiện lửa        
                elif c == 1:
                    fire_detected = True
                    if state['fire_start_time'] == 0:
                        state['fire_start_time'] = current_time
                    elif (current_time - state['fire_start_time'] >= DETECTION_THRESHOLD and 
                          current_time - state['last_fire_send'] >= SEND_DELAY):
                        try:
                            file_path = capture_and_upload_image(frame_to_process, "lua")
                            if file_path:
                                send_alert_fire(camera.rtsp_url, "lua")
                                state['last_fire_send'] = current_time
                        except Exception as e:
                            print(f"Lỗi xử lý lửa camera {camera_id}: {str(e)}")
                
                # Phát hiện khói
                elif c == 2:
                    smoke_detected = True
                    if state['smoke_start_time'] == 0:
                        state['smoke_start_time'] = current_time
                    elif (current_time - state['smoke_start_time'] >= DETECTION_THRESHOLD and 
                          current_time - state['last_smoke_send'] >= SEND_DELAY):
                        try:
                            file_path = capture_and_upload_image(frame_to_process, "khoi")
                            if file_path:
                                send_alert_smoke(camera.rtsp_url, "khoi")
                                state['last_smoke_send'] = current_time
                        except Exception as e:
                            print(f"Lỗi xử lý khói camera {camera_id}: {str(e)}")

            frame = r.plot()
            
        # Reset thời gian bắt đầu nếu không phát hiện
        if not behavior_detected:
            state['behavior_start_time'] = 0
        if not fire_detected:
            state['fire_start_time'] = 0
        if not smoke_detected:
            state['smoke_start_time'] = 0
            
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

