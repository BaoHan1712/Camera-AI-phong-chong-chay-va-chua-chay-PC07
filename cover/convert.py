from ultralytics import YOLO

model = YOLO("model/ver3m.pt")
model.export(format="engine", imgsz=640, simplify=True, half=True)

