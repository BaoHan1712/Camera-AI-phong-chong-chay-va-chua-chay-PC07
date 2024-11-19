from ultralytics import YOLO

model = YOLO('model\smoke_fire.onnx')

results = model.predict(source='data\demo.mp4', save=True, conf=0.55, imgsz=320, show=True)

