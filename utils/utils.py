import time
from cover.library import *
import sys
import os
import uuid
# Thêm đường dẫn tới thư mục cha chứa send_be
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



    
def upload_image_to_s3(filepath, detection_type):
    # Cấu hình thông tin S3
    endpoint_url = 'https://atm263555-s3user.vcos.cloudstorage.com.vn'
    aws_access_key_id = 'atm263555-s3user'
    aws_secret_access_key = 'n70e2lqZaCmci3BkvSwYqP1OZtthkIJ8ZvDwCO1y'
    bucket_name = "atm263555-s3bucket"

    try:
        s3 = boto3.resource('s3',
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key)

        print('🤑 Connected 🤑')

        # Kiểm tra và tạo bucket nếu chưa tồn tại
        if not s3.Bucket(bucket_name) in s3.buckets.all():
            s3.create_bucket(Bucket=bucket_name)
            print('Bucket created')

        # Upload file
        if os.path.isfile(filepath):
            # Lấy tên file từ đường dẫn
            filename = os.path.basename(filepath)
            # Lấy thư mục chứa file (alert hoặc warning)
            folder = 'alert' if detection_type == 'fire' else 'warning'
            
            # Tạo key cho file trên S3 (folder/filename)
            s3_key = f"{folder}/{filename}"
            
            # Upload file lên S3
            s3.Bucket(bucket_name).upload_file(filepath, s3_key)
            print(f"✅ Đã upload file {filename} lên S3 bucket trong thư mục {folder}")
            
            # Tạo đường dẫn file trên S3
            file_path = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
            print(f"✅ Đã upload file {filename} lên S3 bucket trong thư mục {folder}")
            return file_path
            
    except Exception as e:
        print(f"❌ Lỗi khi upload lên S3: {str(e)}")
        return False

def capture_and_upload_image(frame, detection_type):
    temp_dir = 'temp'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Tạo tên file duy nhất với uuid
    unique_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{detection_type}_{timestamp}_{unique_id}.jpg'
    temp_filepath = os.path.join(temp_dir, filename)
    
    try:
        frame_copy = frame.copy()
        cv2.imwrite(temp_filepath, frame_copy)
        file_path = upload_image_to_s3(temp_filepath, detection_type)
        
        # Xóa file tạm sau khi upload
        try:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
        except Exception as e:
            print(f"❌ Lỗi khi xóa file tạm: {str(e)}")
            
        return file_path
        
    except Exception as e:
        print(f"❌ Lỗi khi xử lý ảnh: {str(e)}")
        # Đảm bảo xóa file tạm nếu có lỗi
        try:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
        except:
            pass
        return None

# Hàm check camera có tồn tại trong file rtsp_urls.txt hay không
def check_camera_exists(cam_id):
    try:
        with open('rtsp_urls.txt', 'r') as file:
            existing_urls = file.readlines()
            existing_urls = [url.strip() for url in existing_urls]
            if str(cam_id) in existing_urls:
                print("❌ Camera này đã tồn tại trong file")
                return True
            else:
                print("✅ Camera chưa tồn tại trong file")
                return False
    except FileNotFoundError:
        print("❌ Không tìm thấy file rtsp_urls.txt")
        return False
        



