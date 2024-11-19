import cv2
from ultralytics import YOLO
import threading
import time
from queue import Queue

class RTSPCameraThread:
    def __init__(self, rtsp_url, width=640, height=640):
        self.rtsp_url = rtsp_url
        self.width = width
        self.height = height
        self.frame_queue = Queue(maxsize=3)
        self.stopped = False
        self.fps = 0
        self.prev_time = time.time()
        
    def start(self):
        thread = threading.Thread(target=self.update, args=())
        thread.daemon = True
        thread.start()
        return self
    
    def update(self):
        # Thiết lập các tham số cho RTSP
        cap = cv2.VideoCapture(self.rtsp_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        
        # Kiểm tra kết nối
        if not cap.isOpened():
            print(f"Không thể kết nối tới camera RTSP: {self.rtsp_url}")
            self.stopped = True
            return
            
        while not self.stopped:
            ret, frame = cap.read()
            if not ret:
                print(f"Lỗi đọc frame từ camera: {self.rtsp_url}")
                time.sleep(1)  # Đợi 1 giây trước khi thử lại
                continue
                
            frame = cv2.resize(frame, (self.width, self.height))
            
            if not self.frame_queue.full():
                self.frame_queue.put(frame)
            
        cap.release()
    
    def read(self):
        return self.frame_queue.get() if not self.frame_queue.empty() else None
    
    def stop(self):
        self.stopped = True
        
    def calculate_fps(self):
        current_time = time.time()
        time_diff = current_time - self.prev_time
        self.fps = 1 / time_diff if time_diff > 0 else 0
        self.prev_time = current_time
        return self.fps

# Khởi tạo model YOLO
model = YOLO("model/yolo11n.onnx")

# Danh sách các camera RTSP
rtsp_cameras = [
    "rtsp://admin:password123@192.168.1.100:554/stream1",  # Camera 1
    "rtsp://admin:password123@192.168.1.101:554/stream1",  # Camera 2
    "rtsp://admin:password123@192.168.1.102:554/stream1"   # Camera 3
]

# Khởi tạo các camera threads
camera_threads = [RTSPCameraThread(url) for url in rtsp_cameras]

# Khởi động các camera threads
for thread in camera_threads:
    thread.start()

try:
    while True:
        frames = []
        
        # Đọc frame từ tất cả camera
        for thread in camera_threads:
            frame = thread.read()
            if frame is not None:
                fps = thread.calculate_fps()
                frames.append((frame, fps))
        
        # Xử lý các frame
        for i, (frame, fps) in enumerate(frames):
            results = model.predict(frame, imgsz=320, conf=0.4)
            
            # Vẽ kết quả detection lên frame
            for r in results:
                annotated_frame = r.plot()
                cv2.putText(annotated_frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow(f"Camera {i}", annotated_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    for thread in camera_threads:
        thread.stop()
    cv2.destroyAllWindows()
