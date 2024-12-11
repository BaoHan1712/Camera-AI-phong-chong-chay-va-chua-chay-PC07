from ultralytics import YOLO

# Load a model
model = YOLO("model/ver2.engine")  
print(model.names) 
    