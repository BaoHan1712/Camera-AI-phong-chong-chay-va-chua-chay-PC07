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
# import boto3

# Thêm hàm lưu ảnh
def save_detection_image(frame, detection_type):

    base_dir = '/home/pccc/2411_be_canh-bao-chay-pccc/uploads'
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
    if detection_type in ['fire']:
        file_path = 'http://api.vinafire.cloud/images/alert/' + filepath
    else:
        file_path = 'http://api.vinafire.cloud/images/warning/' + filepath
    print(f"✅ Đã lưu ảnh {detection_type} tại: {filepath}")
    return file_path

# def upload_image_to_s3(filepath):
#     # Cấu hình thông tin S3
#     endpoint_url = 'https://atm263555-s3user.vcos.cloudstorage.com.vn'
#     aws_access_key_id = 'atm263555-s3user'
#     aws_secret_access_key = 'n70e2lqZaCmci3BkvSwYqP1OZtthkIJ8ZvDwCO1y'
#     bucket_name = "atm263555-s3bucket"


#     try:
#         s3 = boto3.resource('s3',

#             endpoint_url = endpoint_url,

#             aws_access_key_id=aws_access_key_id,

#             aws_secret_access_key=aws_secret_access_key)

#         print('Connected')
#         s3.create_bucket(Bucket = bucket_name) 

#         print('CREEATE BUCKET ')

#         # Upload file
#         if os.path.isfile(filepath):
#             # Lấy tên file từ đường dẫn
#             filename = os.path.basename(filepath)
#             # Lấy thư mục chứa file (alert hoặc warning)
#             folder = os.path.basename(os.path.dirname(filepath))
            
#             # Tạo key cho file trên S3 (folder/filename)
#             s3_key = f"{folder}/{filename}"
            
#             # Upload file lên S3
#             s3.Bucket(bucket_name).upload_file(filepath, s3_key)
#             print(f"✅ Đã upload file {filename} lên S3 bucket trong thư mục {folder}")
#             return True
            
#         else:
#             print(f"❌ Không tìm thấy file: {filepath}")
#             return False
            
#     except Exception as e:
#         print(f"❌ Lỗi khi upload lên S3: {str(e)}")
#         return False

 
        

        

