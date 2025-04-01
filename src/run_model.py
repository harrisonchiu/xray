#!/usr/bin/env python
"""
Runs a custom-trained chest X-ray model with provided weights.
Picks random image from CSV file and runs inference on them.

Assumes images are available in ./data/images directory

Checks for accuracy from the CSV file (./data/Data_Entry_2017.csv)
"""

import os
import random
import argparse
import pandas as pd
import time

from PIL import Image

import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models


all_labels = [
    'Atelectasis', 'Cardiomegaly', 'Consolidation', 'Edema',
    'Effusion', 'Emphysema', 'Fibrosis', 'Infiltration',
    'Mass', 'Nodule', 'Pleural_Thickening', 'Pneumonia', 'Pneumothorax'
]

class MultiDiseaseModel(nn.Module):
    def __init__(self, num_classes):
        super(MultiDiseaseModel, self).__init__()
        self.base = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V2)
        
        self.base.features[0][0] = nn.Conv2d(
            1, 32, kernel_size=3, stride=2, padding=1, bias=False
        )
        self.base.classifier = nn.Identity()
        self.pool = nn.AdaptiveAvgPool2d((1,1))
        self.fc1 = nn.Linear(1280, 512)
        self.bn1 = nn.BatchNorm1d(512)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, num_classes)

    def forward(self, x):
        x = self.base.features(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc1(x)
        x = self.bn1(x)
        x = torch.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        return x

def main():
    parser = argparse.ArgumentParser(description="X-ray Image Prediction")
    parser.add_argument(
        '--weights', type=str, required=True,
        help='Path to the trained model weights file (e.g., model_2021-05-15T14:30:00.pth)'
    )
    parser.add_argument(
        '--runs', type=int, default=1,
        help='Number of times to run the model on random (unique) images. Must be >= 1.'
    )
    args = parser.parse_args()

    if args.runs < 1:
        print("Error: --runs must be >= 1.")
        return

    if not os.path.exists(args.weights):
        print(f"Model weights file not found: {args.weights}")
        return

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = torch.load(args.weights, map_location=device)
    model.eval()

    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])
    ])

    images_dir = "./data/images"
    if not os.path.isdir(images_dir):
        print("Images directory not found:", images_dir)
        return

    csv_paths = ["./data/Data_Entry_2017.csv", "Data_Entry_2017.csv"]
    csv_path = None
    for path in csv_paths:
        if os.path.exists(path):
            csv_path = path
            break
    if csv_path is None:
        print("CSV file Data_Entry_2017.csv not found in expected locations.")
        return

    df = pd.read_csv(csv_path, header=None)

    df = df[~df[1].str.contains('No Finding', na=False)]
    df = df[~df[1].str.contains('Hernia', na=False)]

    selected_rows = df.sample(n=min(args.runs, len(df)))

    for i, (_, row) in enumerate(selected_rows.iterrows(), start=1):
        image_file = row[0]  
        print(f"\n--- RUN {i} of {len(selected_rows)} ---")
        image_path = os.path.join(images_dir, image_file)
        print(f"Selected image: {image_path}")

        try:
            image = Image.open(image_path).convert("L")
        except Exception as e:
            print(f"Error opening image {image_path}: {e}")
            continue

        image_tensor = transform(image).unsqueeze(0)  

        start = time.perf_counter()
        with torch.no_grad():
            outputs = model(image_tensor.to(device))
            probabilities = torch.sigmoid(outputs).squeeze(0).cpu().numpy()
        end = time.perf_counter()
        print("TIME", end - start)

        print()
        predictions = {}
        for label, prob in zip(all_labels, probabilities):
            if prob >= 0.5:
                predictions[label] = float(f"{prob:.4f}")
        print(predictions)

        actual_labels = row[1]
        print(f"Actual labels: {actual_labels}")

if __name__ == "__main__":
    main()
