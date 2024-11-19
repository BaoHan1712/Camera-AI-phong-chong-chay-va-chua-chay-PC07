from flask import Flask, Response, render_template
import cv2
from ultralytics import YOLO
import threading
from queue import Queue

app = Flask(__name__)

class CameraThread:
    def __init__(self, camera_id, width=640, height=640):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.frame_queue = Queue(maxsize=2)
        self.stopped = False
        self.lock = threading.Lock()
        
    def start(self):
        thread = threading.Thread(target=self.update, args=())
        thread.daemon = True
        thread.start()
        return self
        
    def update(self):
        if isinstance(self.camera_id, str):
            cap = cv2.VideoCapture(self.camera_id)
        else:
            cap = cv2.VideoCapture(self.camera_id)
        
        if not cap.isOpened():
            print(f"Không thể mở camera: {self.camera_id}")
            return
            
        while not self.stopped:
            ret, frame = cap.read()
            if not ret:
                if isinstance(self.camera_id, str):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    break
                
            frame = cv2.resize(frame, (self.width, self.height))
            
            with self.lock:
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)
                    
        cap.release()
        
    def read(self):
        with self.lock:
            return self.frame_queue.get() if not self.frame_queue.empty() else None
            
    def stop(self):
        self.stopped = True

class CameraManager:
    def __init__(self):
        self.cameras = {}
        self.model = YOLO("model\smoke_fire.onnx")
        
    def add_camera(self, camera_id, source):
        if camera_id not in self.cameras:
            camera = CameraThread(source)
            camera.start()
            self.cameras[camera_id] = camera
            
    def get_camera(self, camera_id):
        return self.cameras.get(camera_id)
        
    def remove_camera(self, camera_id):
        if camera_id in self.cameras:
            self.cameras[camera_id].stop()
            del self.cameras[camera_id]

camera_manager = CameraManager()

def generate_frames(camera_id):
    camera = camera_manager.get_camera(camera_id)
    if not camera:
        return
        
    while True:
        frame = camera.read()
        if frame is None:
            continue
            
        # Thực hiện YOLO detection
        results = camera_manager.model.predict(frame, imgsz=320, conf=0.55)
        
        for r in results:
            frame = r.plot()
            
        # Chuyển frame thành JPEG để stream
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    return Response(generate_frames(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/add_camera/<camera_id>/<source>')
def add_camera(camera_id, source):
    try:
        source = int(source)  
    except ValueError:
        pass  
    
    camera_manager.add_camera(camera_id, source)
    return f"Camera {camera_id} đã được thêm"

@app.route('/remove_camera/<camera_id>')
def remove_camera(camera_id):
    camera_manager.remove_camera(camera_id)
    return f"Camera {camera_id} đã được xóa"

if __name__ == '__main__':
    # Thêm camera mặc định
    default_cameras = {
        'cam0': 0,  # Camera USB/Webcam
        'cam1': 'runs\demo.avi',  # Video file
    }
    
    for cam_id, source in default_cameras.items():
        camera_manager.add_camera(cam_id, source)
        
    app.run(host='0.0.0.0', port=5000, threaded=True) 