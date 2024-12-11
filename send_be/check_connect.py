import requests

def send_alert_fire(rtsp_url, alert_type):
    api_url = "http://198.13.55.162:2412/api/devices/alert-to-device"
    response = requests.post(api_url, params={"rtspUrl": rtsp_url}  ,data={"files": "rtsp_url", "note": alert_type})    
    print("connect ok")
    


send_alert_fire("rtsp://admin:admin%40123@192.168.1.252:554/cam/realmonitor?channel=1&subtype=0", "có lửa")