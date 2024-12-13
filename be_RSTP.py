from cover.library import *
from utils.utils import *
from send_be.send_comunitication import *
from utils.main import *

app = Flask(__name__)

@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    return Response(generate_frames(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')

# Gửi cảnh báo cháy 
@app.route('/check_alert/<camera_id>')
def check_alerts_fire(camera_id):
    alert_info = alerts.get(camera_id, {
        'rtsp_url': '',
        'has_fire': False,
    })

    note = []
    if alert_info['has_fire']:
        note.append("Phát hiện lửa")

    response = {
        "rtsp_url": alert_info['rtsp_url'],
        "note": ", ".join(note) if note else "none"
    }
    return jsonify(response)


# Gửi thông báo khói và hành vi thuốc lá
@app.route('/check_warning/<camera_id>')
def check_warning(camera_id):
    warning_info = warnings.get(camera_id, {
        'rtsp_url': '',
        'has_smoke': False,
        'has_behavior': False
    })
    note_smoke_behavior = []
    if warning_info['has_smoke']:
        note_smoke_behavior.append("Phát hiện khói")
    if warning_info['has_behavior']:
        note_smoke_behavior.append("Phát hiện hút thuốc lá")

    response = {
        "rtsp_url": warning_info['rtsp_url'],
        "note": ", ".join(note_smoke_behavior) if note_smoke_behavior else "none"
    }
    
    return jsonify(response)

@app.route('/')
def index():
    return render_template('index.html')



# Xóa camera
@app.route('/api/delete-camera/<url_rtsp>', methods=['DELETE'])
def delete_camera(url_rtsp):
    try:
        # Lấy thông tin camera từ request
        data = request.get_json()
        url_rtsp = data.get('url_rtsp')

        # Kiểm tra camera có tồn tại không
        if url_rtsp in camera_manager.cameras:
            # Dừng và xóa camera khỏi camera manager
            camera_manager.cameras[url_rtsp].stop()
            del camera_manager.cameras[url_rtsp]

            # Xóa khỏi alerts và warnings
            if url_rtsp in alerts:
                del alerts[url_rtsp]
            if url_rtsp in warnings:
                del warnings[url_rtsp]

            # Đọc và cập nhật file rtsp_urls.txt
            urls = []
            with open('rtsp_urls.txt', 'r') as file:
                urls = [line.strip() for line in file.readlines()]

            # Xóa URL khỏi danh sách
            if url_rtsp in urls:
                urls.remove(url_rtsp)

            # Lọc bỏ các dòng trống
            urls = [url for url in urls if url.strip()]

            # Ghi lại file với danh sách URL đã cập nhật
            with open('rtsp_urls.txt', 'w') as file:
                for url in urls:
                    file.write(f"{url}\n")

            print(f"✅ Đã xóa camera {url_rtsp} thành công")
    except Exception as e:
        print(f"❌ Lỗi khi xóa camera: {str(e)}")

@app.route('/api/get-cameras')
def get_cameras():
    camera_list = [{'id': cam_id, 'name': f'Camera {cam_id}'} for cam_id in camera_manager.cameras.keys()]
    return jsonify({'cameras': camera_list})

# Nhận thông tin camera 
@app.route('/api/add-camera', methods=['POST'])
def receive_camera():
    try:
        # Lấy dữ liệu từ request
        data = request.get_json()
        # user_id = data.get('userId')
        # name = data.get('name')
        rtsp_url = data.get('rtspUrl')
        
        # Kiểm tra RTSP URL
        if not rtsp_url:
            print("❌ Không tìm thấy RTSP URL")
            return jsonify({
                'success': False,
                'message': 'Không tìm thấy RTSP URL'
            }), 400

        # Kiểm tra xem URL đã tồn tại chưa 
        check_camera_exists(rtsp_url)

        # Thêm camera mới vào file
        with open('rtsp_urls.txt', 'a') as file:
            file.write(f"{rtsp_url}\n")
            print("✅ Đã thêm camera thành công")

        # Thêm camera vào camera manager
        camera_manager.add_camera(rtsp_url, rtsp_url)
        
        return jsonify({
            'success': True,
            'message': 'Đã thêm camera thành công'
        })

    except Exception as e:
        print(f"❌ Lỗi khi thêm camera: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Lỗi khi thêm camera: {str(e)}'
        }), 500


if __name__ == '__main__':
    try:
        # Khởi động YOLO và thêm camera từ file txt
        start_yolo_and_cameras()
        print("✅ Đã khởi động hệ thống thành công")
        
        # Chạy Flask app
        app.run(host='0.0.0.0', port=8000, threaded=True)
    except Exception as e:
        print(f"❌ Lỗi khởi động hệ thống: {str(e)}")