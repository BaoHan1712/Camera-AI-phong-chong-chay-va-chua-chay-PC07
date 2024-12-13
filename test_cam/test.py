import cv2
import time

# Đọc danh sách camera từ file txt
with open('rtsp_urls.txt', 'r') as file:
    camera_ids = [int(line.strip()) for line in file.readlines() if line.strip()]

# Khởi tạo dictionary để lưu các camera capture
cameras = {}
for cam_id in camera_ids:
    try:
        cap = cv2.VideoCapture(cam_id)
        if cap.isOpened():
            cameras[f'cam{cam_id}'] = cap
            print(f"✅ Đã kết nối camera {cam_id}")
        else:
            print(f"❌ Không thể kết nối camera {cam_id}")
    except Exception as e:
        print(f"❌ Lỗi khi kết nối camera {cam_id}: {str(e)}")

# Kiểm tra nếu không có camera nào được kết nối
if not cameras:
    print("Không có camera nào được kết nối thành công!")
    exit()

# Hiển thị video từ tất cả camera
while True:
    for cam_id, cap in cameras.items():
        ret, frame = cap.read()
        if ret:
            cv2.imshow(f'Camera {cam_id}', frame)
        else:
            print(f"❌ Lỗi đọc frame từ {cam_id}")
            
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng tài nguyên
for cap in cameras.values():
    cap.release()
cv2.destroyAllWindows()
# def check_camera(cam_id):
#     try:
#         with open('rtsp_urls.txt', 'r') as file:
#             existing_urls = file.readlines()
#             existing_urls = [url.strip() for url in existing_urls]
#             if str(cam_id) in existing_urls:
#                 print("❌ Camera này đã tồn tại trong file")
#                 return True
#             else:
#                 print("✅ Camera chưa tồn tại trong file")
#                 return False
#     except FileNotFoundError:
#         print("❌ Không tìm thấy file rtsp_urls.txt")
#         return False

# def add_camera(cam_id):
#     if not check_camera(cam_id):
#         with open('rtsp_urls.txt', 'a') as file:
#             file.write(f"{cam_id}\n")
#             print("✅ Đã thêm camera thành công")

# add_camera("rtsp://admin:admin%40123@171.232.175.190:554/cam/realmonitor?channel=1&subtype=0")
