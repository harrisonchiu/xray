#!/usr/bin/env python
"""
train.py

This script downloads the NIH Chest X-ray data files,
decompresses/extracts them, preprocesses the CSV and images, and trains a
multi-label chest x-ray classifier using a CNN PyTorch model.
"""

import argparse
import datetime
import os
import urllib.request
import tarfile

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

import torchvision.transforms as transforms
import torchvision.models as models

# List of disease labels (adjust as needed)
all_labels = ['Atelectasis', 'Cardiomegaly', 'Consolidation', 'Edema',
              'Effusion', 'Emphysema', 'Fibrosis', 'Infiltration',
              'Mass', 'Nodule', 'Pleural_Thickening', 'Pneumonia', 'Pneumothorax']

# Data Download and Extraction Functions
def prepare_data():
    """
    Downloads and extracts the data files.
    Does not download CSV file Data_Entry_2017.csv. Needs to be in the folder!
      - An images folder containing the chest x-ray images ( in data/images/)
    """
    links = [
        'https://nihcc.box.com/shared/static/vfk49d74nhbxq3nqjg0900w5nvkorp5c.gz',
        'https://nihcc.box.com/shared/static/i28rlmbvmfjbl8p2n3ril0pptcmcu9d1.gz',
        'https://nihcc.box.com/shared/static/f1t00wrtdk94satdfb9olcolqx20z2jp.gz',
        'https://nihcc.box.com/shared/static/0aowwzs5lhjrceb3qp67ahp0rd1l1etg.gz',
        'https://nihcc.box.com/shared/static/v5e3goj22zr6h8tzualxfsqlqaygfbsn.gz',
        'https://nihcc.box.com/shared/static/asi7ikud9jwnkrnkj99jnpfkjdes7l6l.gz',
        'https://nihcc.box.com/shared/static/jn1b4mw4n6lnh74ovmcjb8y48h8xj07n.gz',
        'https://nihcc.box.com/shared/static/tvpxmn7qyrgl0w8wfh9kqfjskv6nmm1j.gz',
        'https://nihcc.box.com/shared/static/upyy3ml7qdumlgk2rfcvlb9k6gvqq2pj.gz',
        'https://nihcc.box.com/shared/static/l6nilvfa9cg3s28tqv1qc1olm3gnz54p.gz',
        'https://nihcc.box.com/shared/static/hhq8fkdgvcari67vfhs7ppg2w6ni4jze.gz',
        'https://nihcc.box.com/shared/static/ioqwiy20ihqwyr8pf4c24eazhh281pbu.gz'
    ]

    download_dir = "./downloads"
    data_dir = "./data"
    images_dir = "./data/images"
    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    for index, link in enumerate(links):
        tar = "images_%02d.tar.gz" % (index + 1)
        tar_path = os.path.join(download_dir, tar)
        if os.path.exists(tar_path):
            continue

        urllib.request.urlretrieve(link, tar_path)
        print(f"Downloaded {tar}")

        with tarfile.open(tar_path, "r") as tar_obj:
            for member in tar_obj.getmembers():
                if member.isfile() and member.name.lower().endswith(".png"):
                    member.name = os.path.basename(member.name)
                    tar_obj.extract(member, path=images_dir)
        print(f"Extracted {tar}")

    print("Finished downloading and extracting tars")
    print("Data download and extraction complete.")

# Dataset and Model Definitions
class ChestXrayDataset(Dataset):
    def __init__(self, df, images_dir, transform=None):
        self.df = df.reset_index(drop=True)
        self.images_dir = images_dir
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = os.path.join(self.images_dir, row['Image Index'])
        image = Image.open(img_path).convert("L")
        if self.transform:
            image = self.transform(image)
        labels = row[all_labels].values.astype(np.float32)
        return image, torch.tensor(labels)

class MultiDiseaseModel(nn.Module):
    def __init__(self, num_classes):
        super(MultiDiseaseModel, self).__init__()
        self.base = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V2)
        for param in self.base.parameters():
            param.requires_grad = False
        for layer in self.base.features[-3:]:
            for param in layer.parameters():
                param.requires_grad = True

        # Change input conv to accept 1-channel input
        self.base.features[0][0] = nn.Conv2d(1, 32, kernel_size=3, stride=2, padding=1, bias=False)
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

def calculate_multilabel_accuracy(outputs, labels, threshold=0.5):
    """
    Calculate micro-averaged accuracy for multilabel classification.
    """
    preds = (torch.sigmoid(outputs) >= threshold).int()
    labels = labels.int()
    correct = (preds == labels).sum().item()
    total = labels.numel()
    return correct / total

def calculate_subset_accuracy(outputs, labels, threshold=0.5):
    """
    Calculate subset (exact match) accuracy for multilabel classification.
    A sample is counted as correct only if every label is correctly predicted.
    """
    preds = (torch.sigmoid(outputs) >= threshold).int()
    labels = labels.int()
    correct_samples = (preds == labels).all(dim=1).sum().item()
    total_samples = labels.shape[0]
    return correct_samples / total_samples

def calculate_margin_loss(outputs, labels, pos_target=0.9, neg_target=0.1):
    """
    Computes an extra loss term that encourages:
      - For pos labels, sigmoid(output) to be at least pos_target,
      - For neg labels, sigmoid(output) to be at most neg_target.
    This loss will penalize predictions that are not confidently correct,
    and thus can help the model focus on complete correctness.
    """
    probs = torch.sigmoid(outputs)
    # For pos labels, penalize if below pos_target.
    loss_pos = torch.clamp(pos_target - probs, min=0) * labels
    # For neg labels, penalize if above neg_target.
    loss_neg = torch.clamp(probs - neg_target, min=0) * (1 - labels)
    # Average the margin loss over all elements.
    return (loss_pos + loss_neg).mean()

# Main Training Function
def main():
    parser = argparse.ArgumentParser(description="X-ray Image Prediction")
    parser.add_argument(
        '--weights', type=str, required=False,
        help='Path to the trained model weights file (e.g., model_2021-05-15T14:30:00.pth)'
    )
    parser.add_argument('--trim', action='store_true',
        help='Whether to use all labels (including No Findings) or trim classes with extreme sample sizes')
    args = parser.parse_args()

    prepare_data()

    csv_path = "Data_Entry_2017.csv"
    if not os.path.exists(csv_path):
        csv_path = os.path.join("data", "Data_Entry_2017.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError("CSV file Data_Entry_2017.csv not found.")

    data = pd.read_csv(csv_path)

    if args and args.trim:
        # Remove rows with "No Finding" or "Hernia"
        data = data[~data['Finding Labels'].str.contains('No Finding', na=False)]
        data = data[~data['Finding Labels'].str.contains('Hernia', na=False)]
    else:
        data['Finding Labels'] = data['Finding Labels'].str.replace('No Finding', '')

    from itertools import chain
    all_diseases = np.unique(list(chain(*data['Finding Labels'].map(lambda x: x.split('|')).tolist())))
    all_diseases = [d for d in all_diseases if len(d) > 0]
    for disease_name in all_diseases:
        data[disease_name] = data['Finding Labels'].map(lambda txt: 1.0 if disease_name in txt else 0.0)

    train_df, valid_df = train_test_split(
        data, test_size=0.2, random_state=2018,
        stratify=data['Finding Labels'].apply(lambda x: x[:4])
    )

    # Compute avg num of positives per sample and class counts for loss balancing
    num_examples = train_df.shape[0]
    class_counts = train_df[all_labels].sum()  # pandas Series of counts
    prevalence = class_counts / num_examples
    num_negatives = num_examples - class_counts
    pos_weight = num_negatives / class_counts
    avg_positive = train_df[all_labels].sum(axis=1).mean()  # Expected positive count per sample

    train_transform = transforms.Compose([
        transforms.Resize((128, 128)),
        # transforms.RandomHorizontalFlip(p=0.5),
        # transforms.RandomApply([
        #     transforms.RandomAffine(
        #         degrees=(-5, 5),
        #         translate=(0.02, 0.02),
        #         scale=(0.98, 1.02)
        #     )
        # ], p=0.3),
        # transforms.RandomApply([
        #     transforms.ColorJitter(
        #         brightness=0.2,  # brightness factor: [0.8, 1.2]
        #         contrast=0.2     # contrast factor: [0.8, 1.2]
        #     )
        # ], p=0.5),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])
    ])


    valid_transform = transforms.Compose([
        transforms.Resize((128,128)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])
    ])

    images_dir = os.path.join("data", "images")
    if not os.path.exists(images_dir):
        raise FileNotFoundError("Images directory not found. Please check extraction.")

    train_dataset = ChestXrayDataset(train_df, images_dir=images_dir, transform=train_transform)
    valid_dataset = ChestXrayDataset(valid_df, images_dir=images_dir, transform=valid_transform)

    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True, num_workers=4)
    valid_loader = DataLoader(valid_dataset, batch_size=512, shuffle=False, num_workers=4)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    num_classes = len(all_labels)
    model = MultiDiseaseModel(num_classes=num_classes).to(device)

    if args and args.weights and os.path.exists(args.weights):
        print("Loading pretrained model from", args.weights)
        model = torch.load(args.weights, map_location=device)

    # Initialize final layer bias with log odds of class prevalence
    with torch.no_grad():
        bias_init = torch.log((torch.tensor(prevalence.values, dtype=torch.float32) + 1e-7) /
                              (1 - torch.tensor(prevalence.values, dtype=torch.float32) + 1e-7))
        model.fc2.bias.copy_(bias_init.to(device))

    # Use class-balanced loss via pos_weight
    pos_weight_tensor = torch.tensor(pos_weight.values, dtype=torch.float32).to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight_tensor)

    optimizer = optim.Adam(model.parameters(), lr=0.0005)

    # Sparsity regularization hyperparameter
    lambda_reg = 0.01
    # Margin loss hyperparameter
    lambda_margin = 20.0

    print("Starting Training Now")
    best_val_loss = float("inf")
    patience = 10
    no_improve_count = 0
    max_epochs = 50
    for epoch in range(max_epochs):
        model.train()
        running_loss = 0.0
        train_running_accuracy = 0.0
        total_train_batches = 0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)

            # Compute sparsity regularization
            predicted_probabilities = torch.sigmoid(outputs)
            predicted_count = predicted_probabilities.sum(dim=1)
            expected_count = torch.tensor(avg_positive, dtype=torch.float32, device=device)
            sparsity_loss = torch.mean((predicted_count - expected_count) ** 2)
            
            # Compute margin loss
            margin_loss = calculate_margin_loss(outputs, labels, pos_target=0.6, neg_target=0.4)
            
            loss_total = loss + lambda_reg * sparsity_loss + lambda_margin * margin_loss

            loss_total.backward()
            optimizer.step()

            running_loss += loss_total.item() * images.size(0)
            # Using subset accuracy
            train_batch_accuracy = calculate_subset_accuracy(outputs, labels)
            train_running_accuracy += train_batch_accuracy
            total_train_batches += 1

        epoch_train_loss = running_loss / len(train_loader.dataset)
        epoch_train_accuracy = train_running_accuracy / total_train_batches

        model.eval()
        val_running_loss = 0.0
        val_running_accuracy = 0.0
        total_val_batches = 0

        with torch.no_grad():
            for images, labels in valid_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_running_loss += loss.item() * images.size(0)
                val_batch_accuracy = calculate_subset_accuracy(outputs, labels)
                val_running_accuracy += val_batch_accuracy
                total_val_batches += 1

        epoch_val_loss = val_running_loss / len(valid_loader.dataset)
        epoch_val_accuracy = val_running_accuracy / total_val_batches

        print(f"Epoch [{epoch+1}/{max_epochs}] "
              f"Train Loss: {epoch_train_loss:.4f}, Val Loss: {epoch_val_loss:.4f} | "
              f"Train Subset Acc: {epoch_train_accuracy:.4f}, Val Subset Acc: {epoch_val_accuracy:.4f}")

        if epoch_val_loss < best_val_loss:
            best_val_loss = epoch_val_loss
            no_improve_count = 0
        else:
            no_improve_count += 1
            if no_improve_count >= patience:
                print("Early stopping triggered.")
                break

    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    model_filename = f"model_{timestamp}.pth"
    torch.save(model, model_filename)
    print(f"Model saved successfully as: {model_filename}")

if __name__ == "__main__":
    main()
