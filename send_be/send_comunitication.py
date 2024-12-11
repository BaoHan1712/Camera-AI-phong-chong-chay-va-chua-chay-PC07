import requests
import time

# Gửi cảnh báo cháy tới BE
def send_alert_fire(rtsp_url, alert_type,file_path):
    try:
        api_url = "https://api.vinafire.cloud/api/devices/alert-to-device"
        response = requests.post(
            api_url, 
            params={"rtspUrl": rtsp_url},
            data={"files": file_path, "note": alert_type},
            timeout=3
        )
        print(f"✅ Gửi cảnh báo cháy thành công")
    except requests.exceptions.ConnectionError:
        print("❌ Không thể kết nối tới server API cảnh báo cháy")
    except Exception as e:
        print(f"❌ Lỗi khi gửi cảnh báo cháy: {str(e)}")
    time.sleep(0.5)  # Tránh gửi quá nhiều request

# Gửi cảnh báo khói, hành vi thuốc lá tới BE
def send_alert_smoke(rtsp_url, warning_type, file_path):
    try:
        api_url = "https://api.vinafire.cloud/api/devices/warning-to-device"
        response = requests.post(
            api_url,
            params={"rtspUrl": rtsp_url},
            data={"files": file_path, "note": warning_type},
            timeout=3
        )
        print(f"✅ Gửi cảnh báo {warning_type} thành công")
    except requests.exceptions.ConnectionError:
        print(f"❌ Không thể kết nối tới server API cảnh báo {warning_type}")
    except Exception as e:
        print(f"❌ Lỗi khi gửi cảnh báo {warning_type}: {str(e)}")
    time.sleep(0.5)  # Tránh gửi quá nhiều request



    

