import cv2
import time

# URL RTSP cho camera KBVision
rtsp_url = "rtsp://admin:admin%40123@171.239.175.190:554/cam/realmonitor?channel=1&subtype=0"

def connect_camera():
    print(f"Đang kết nối tới camera: {rtsp_url}")
    
    # Tạo đối tượng VideoCapture với các tham số RTSP
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    
    # Thiết lập các tham số cho RTSP
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
    
    if not cap.isOpened():
        print("Không thể kết nối tới camera!")
        return None
        
    print("Kết nối thành công!")
    return cap

def main():
    cap = connect_camera()
    if cap is None:
        return
        
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Lỗi đọc frame")
                time.sleep(1)
                continue
                
            # Resize frame
            frame = cv2.resize(frame, (640, 480))
            
            # Hiển thị frame
            cv2.imshow('KBVision Camera', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 