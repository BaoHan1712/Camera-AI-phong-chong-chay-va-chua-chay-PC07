import time
from cover.library import *

# Biến lưu trữ trạng thái cảnh báo
frist_fire = False 
frist_smoke = False
frist_behavior = False

# Thêm các biến theo dõi thời gian phát hiện
last_fire_time = 0
last_smoke_time = 0  
last_behavior_time = 0

# Thêm biến đếm thời gian phát hiện liên tục
fire_detection_start = 0
smoke_detection_start = 0
behavior_detection_start = 0

# Thêm hàm kiểm tra và reset
def check_and_reset_detections():
    global frist_fire, frist_smoke, frist_behavior
    global last_fire_time, last_smoke_time, last_behavior_time
    global fire_detection_start, smoke_detection_start, behavior_detection_start
    
    current_time = time.time()
    
    # Reset fire detection sau 30s
    if current_time - last_fire_time > 30 and frist_fire:
        frist_fire = False
        fire_detection_start = 0
        
    # Reset smoke detection sau 30s  
    if current_time - last_smoke_time > 30 and frist_smoke:
        frist_smoke = False
        smoke_detection_start = 0
        
    # Reset behavior detection sau 30s
    if current_time - last_behavior_time > 30 and frist_behavior:
        frist_behavior = False
        behavior_detection_start = 0

# Thêm import
import os
from datetime import datetime

# Thêm hàm lưu ảnh
def save_detection_image(frame, detection_type):

    base_dir = 'detections'
    if detection_type in ['fire']:
        save_dir = os.path.join(base_dir, 'alert')
    else:
        save_dir = os.path.join(base_dir, 'warning')
        
    os.makedirs(save_dir, exist_ok=True)
    
    # Tạo tên file với timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{detection_type}_{timestamp}.jpg'
    filepath = os.path.join(save_dir, filename)
    
    # Lưu ảnh
    cv2.imwrite(filepath, frame)
    print(f"✅ Đã lưu ảnh {detection_type} tại: {filepath}")
