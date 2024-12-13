import requests
import time

# Gửi cảnh báo cháy tới BE
def send_alert_fire(rtsp_url, alert_type):
    try:
        api_url = "https://api.vinafire.cloud/api/devices/alert-to-device"
        response = requests.post(
            api_url, 
            params={"rtspUrl": rtsp_url},
            data={"files": 'string', "note": alert_type},
        )
        print(f"✅ Gửi cảnh báo cháy thành công")   
    except requests.exceptions.ConnectionError:
        print("❌ Không thể kết nối tới server API cảnh báo cháy")
    except Exception as e:
        print(f"❌ Lỗi khi gửi cảnh báo cháy: {str(e)}")


# Gửi cảnh báo khói, hành vi thuốc lá tới BE
def send_alert_smoke(rtsp_url, warning_type):
    try:
        api_url = "https://api.vinafire.cloud/api/devices/warning-to-device"
        response = requests.post(
            api_url,
            params={"rtspUrl": rtsp_url},
            data={"files": 'string', "note": warning_type},
        )
        print(f"✅ Gửi cảnh báo {warning_type} thành công")
    except requests.exceptions.ConnectionError:
        print(f"❌ Không thể kết nối tới server API cảnh báo {warning_type}")
    except Exception as e:
        print(f"❌ Lỗi khi gửi cảnh báo {warning_type}: {str(e)}")


# Gửi trạng thái bình thường tới BE
def normal_to_device(rtsp_url, detection_type):
    try:
        api_url = "https://api.vinafire.cloud/api/devices/normal-to-device"
        response = requests.post(api_url,params={"rtspUrl": rtsp_url})
        print(f"✅ trạng thái {detection_type} bình thường")
    except Exception as e:
        print(f"❌ Lỗi trạng thái {detection_type} bình thường: {str(e)}")


      

