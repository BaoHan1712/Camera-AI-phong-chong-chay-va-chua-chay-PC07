from ultralytics import YOLO

model = YOLO("model/ver2.pt")
model.export(format="engine", imgsz=640, simplify=True, half=True)

