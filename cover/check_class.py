from ultralytics import YOLO

# Load a model
model = YOLO("model\smoke_fire.onnx")  
print(model.names) 
    