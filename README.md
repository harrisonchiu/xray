# Scanalyse AI

Developer Names: Hamza Issa, Jared Paul, Ahmad Hamadi, Gurnoor Bal

Date of project start: 21 September 2024

This project is develop a convolutional neural network to identify lung and cardiac conditions in chest X-ray images.


## Project Overview

The Scanalyse AI project is designed to assist radiologists and healthcare professionals by automating the detection of lung and cardiac conditions in chest X-rays. The system leverages deep learning techniques to provide accurate and interpretable predictions for multiple diseases. The project includes the following components:

### 1. **Machine Learning Model**
- A custom MobileNetV2 CNN model trained on the NIH chest X-ray dataset which has over 100,000+ images.
- Supports multi-disease classification for 13 conditions, including:
  - Atelectasis, Cardiomegaly, Consolidation, Edema, Effusion, Emphysema, Fibrosis, Infiltration, Mass, Nodule, Pleural Thickening, Pneumonia, and Pneumothorax.
- Custom training
  - Data augmentation
  - Class balancing with weighted loss functions.
  - Sparsity and margin loss regularization for improved generalization.

### 2. **Backend API**
- Built using Flask to serve predictions and handle requests.
- Key routes:
  - `/test`: Verifies API connectivity.
  - `/predict`: Accepts an X-ray image and returns disease predictions along with probabilities.
- Integrates with the trained PyTorch model for real-time inference.

### 3. **Frontend User Interface**
- Developed using React for a modern and responsive design.
- Features:
  - Drag-and-drop upload area for chest X-ray images.
  - Displays predictions and probabilities in a user-friendly format.
  - Styled with Tailwind CSS.

### Prerequisites
- Python 3.8 or higher
- Node.js and npm
- PyTorch, Pillow, Albumentation Python libraries

### The folders and files for this project are as follows:

docs - Documentation for the project

refs - did not use

src - Source code

test - Test cases

etc.


### Style

Branch names must only be lower case letters, numbers, and hyphens. 

Code style to be determined later.
