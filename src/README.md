# Source Code Overview

This folder contains the source code for the Chest X-ray project. The code is organized into subdirectories based on functionality, including the backend, frontend, and machine learning components.

## Folder Structure
- **chest-xray-app**: Contains the main application code for the project.
  - **backend**: Implements the Flask-based API for serving predictions and handling requests.
  - **frontend**: Implements the React-based user interface for uploading X-ray images and displaying results.
- **train.py**: Script for training the convolutional neural network model on chest X-ray datasets.
- **chest_xray_*.ipynb**: Jupyter notebooks for training the CNN model on the NIH chest x-ray dataset. There are different revisions because different teams have made slight changes based on how they want to run and train the model. All versions are included for transparency.
- **run.py**: Utility scripts for sanity runs on the model to verify its accuracy and actual usage.

## Key Features
1. **Backend**:
   - Flask API for handling image uploads and running predictions.
   - Integration with a PyTorch-based CNN model for multi-disease classification.
   - Routes:
     - `/test`: Verifies API connectivity.
     - `/predict`: Accepts an X-ray image and returns disease predictions.

2. **Frontend**:
   - React-based interface for uploading chest X-ray images.
   - Displays predictions and probabilities for detected conditions.
   - Styled using Tailwind CSS for a clean and responsive design.

3. **Machine Learning**:
   - A custom MobileNetV2 CNN model for multi-disease classification that classifies 13 different disease labels
   - Training script (`train.py`) with support for data augmentation, class balancing, and loss regularization.
   - Uses PyTorch for model training and preprocessing.
