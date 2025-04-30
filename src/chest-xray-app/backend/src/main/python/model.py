from io import BytesIO
from PIL import Image
import torch
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2



# ✅ Ensure the model is in evaluation mode
model.eval()

# ✅ Set the device (GPU or CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class_labels = ["Atelectasis", "Cardiomegaly", "Consolidation", "Edema", "Effusion",
                "Emphysema", "Fibrosis", "Hernia", "Infiltration", "Mass",
                "Nodule", "Pleural_Thickening", "Pneumonia", "Pneumothorax"]

# ✅ Define the same validation transformations used during training
transform = A.Compose([
    A.Resize(height=256, width=256, interpolation=cv2.INTER_LINEAR),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2(),
])

def predict_from_bytes(image_bytes: bytes):
    """Receives an image as a byte array, applies preprocessing, runs inference, and returns predicted labels."""

    # ✅ Convert byte array to PIL image
    image = Image.open(BytesIO(image_bytes)).convert("RGB")

    # ✅ Convert image to NumPy and apply transformations
    image = np.array(image)
    augmented = transform(image=image)
    input_tensor = augmented["image"].unsqueeze(0).to(device)  # ✅ Convert to batch format

    # ✅ Run inference
    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.sigmoid(output).cpu().numpy()[0]  # Convert logits to probabilities

    # ✅ Print probability scores for all classes (For debugging)
    print("🔎 Class Probabilities:")
    for i, prob in enumerate(probs):
        print(f"{class_labels[i]}: {prob:.4f}")

    # ✅ Apply thresholding for prediction
    threshold = 0.5  # Adjust if needed
    preds = [class_labels[i] for i in range(len(probs)) if probs[i] > threshold]

    # ✅ If no diseases are predicted, assign "No Finding"
    if not preds:
        preds = ["No Finding"]

    return preds
# ✅ Run inference using the saved image as a byte array
predicted_labels = predict_from_bytes(test_image_bytes)

# ✅ Print the final prediction
print(f"🤖 Predicted Labels: {predicted_labels}")


def load_model(model_path, device):
    model = torch.load(model_path, map_location=device, weights_only=False)  # Allow full model loading
    model.to(device)
    model.eval()  # Set to evaluation mode
    return model

# Load the model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = load_model("resnet50model_2025-02-05T13:22:57.pth", device)  # Replace with actual filename

print("✅ Model loaded successfully!")