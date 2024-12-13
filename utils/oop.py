from cover.library import *
class RTSPCameraThread:
    def __init__(self, rtsp_url, camera_id, width=640, height=480):
        self.rtsp_url = rtsp_url
        self.camera_id = camera_id
        self.width = width 
        self.height = height
        self.frame_queue = Queue(maxsize=3)
        self.stopped = False
        self.lock = threading.Lock()
        
    def start(self):
        thread = threading.Thread(target=self.update, args=())
        thread.daemon = True
        thread.start()
        return self
        
    def update(self):
        try:
            # Xử lý camera local (số) hoặc RTSP URL
            if str(self.rtsp_url).isdigit():
                cap = cv2.VideoCapture(int(self.rtsp_url))
                print(f"✅ Kết nối camera local: {self.rtsp_url}")
            else:
                cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
                print(f"✅ Kết nối camera RTSP: {self.rtsp_url}")
            
            if not cap.isOpened():
                print(f"❌ Không thể kết nối tới camera: {self.rtsp_url}")
                self.stopped = True
                return
                
            while not self.stopped:
                ret, frame = cap.read()
                if not ret:
                    print(f"❌ Lỗi đọc frame từ camera: {self.rtsp_url}")
                    time.sleep(1)
                    continue
                    
                frame = cv2.resize(frame, (self.width, self.height))
                
                with self.lock:
                    if not self.frame_queue.full():
                        self.frame_queue.put(frame)
                        
        except Exception as e:
            print(f"❌ Lỗi camera {self.rtsp_url}: {str(e)}")
            self.stopped = True
        finally:
            if 'cap' in locals():
                cap.release()
        
    def read(self):
        with self.lock:
            return self.frame_queue.get() if not self.frame_queue.empty() else None
            
    def stop(self):
        self.stopped = True

class CameraManager:
    def __init__(self):
        self.cameras = {}
        self.model = YOLO("model/ver3m.engine", task="detect")
        
    def add_camera(self, camera_id, rtsp_url):
        if camera_id not in self.cameras:
            camera = RTSPCameraThread(rtsp_url, camera_id)
            camera.start()
            self.cameras[camera_id] = camera
            
    def get_camera(self, camera_id):
        return self.cameras.get(camera_id)