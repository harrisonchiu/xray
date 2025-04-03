from flask import Flask, request, jsonify
from flask_cors import CORS  
from io import BytesIO
from PIL import Image
import torch
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2
import torch.nn as nn
import torchvision.models as models

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173", "supports_credentials": True}})

class OptimizedChestXRayResNet(nn.Module):
    def __init__(self, num_classes=14):  
        super(OptimizedChestXRayResNet, self).__init__()
        self.model = models.resnet50(pretrained=False)
        in_features = self.model.fc.in_features
        self.model.fc = nn.Sequential(
            nn.Linear(in_features, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        return self.model(x)

def load_model(model_path, device):
    torch.serialization.add_safe_globals([OptimizedChestXRayResNet])  
    model = torch.load(model_path, map_location=device, weights_only=False)  
    model.to(device)
    model.eval()  
    return model

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = load_model("resnet50model.pth", device)

class_labels = [
    "Atelectasis", "Cardiomegaly", "Consolidation", "Edema", "Effusion",
    "Emphysema", "Fibrosis", "Hernia", "Infiltration", "Mass",
    "Nodule", "Pleural_Thickening", "Pneumonia", "Pneumothorax"
]

transform = A.Compose([
    A.Resize(height=256, width=256, interpolation=cv2.INTER_LINEAR),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2(),
])

def predict(image_bytes):
    """Process image and return predictions"""
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        image = np.array(image)
        augmented = transform(image=image)
        input_tensor = augmented["image"].unsqueeze(0).to(device) 

        with torch.no_grad():
            output = model(input_tensor)
            probs = torch.sigmoid(output).cpu().numpy()[0]  

        # Store class probabilities in a dictionary
        class_probs = {class_labels[i]: float(probs[i]) for i in range(len(probs))}
        preds = [class_labels[i] for i, prob in enumerate(probs) if prob > 0.5]
        if not preds:
            preds = ["No Finding"]

        return preds, class_probs
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

@app.route('/test', methods=['GET'])
def test_connection():
    return jsonify({'message': 'Flask API is reachable!'})

@app.route('/predict', methods=['POST'])
def predict_api():
    """Receive image, run model, return predictions"""
    print("Received request:", request.method)  

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    try:
        image = request.files['file'].read()
        predictions = predict(image)

        if isinstance(predictions, dict) and "error" in predictions:
            return jsonify(predictions), 500  # Return error if prediction fails

        print("Predictions:", predictions)  

        return jsonify({'predictions': predictions})
    except Exception as e:
        return jsonify({'error': f"Server error: {str(e)}"}), 500  

if __name__ == '__main__':
    print("loading model and starting Flask API...")
    app.run(host="0.0.0.0", port=5001, debug=True)  
