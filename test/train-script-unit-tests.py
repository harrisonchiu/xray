import unittest
import os
import pandas as pd
import numpy as np
from train import prepare_data, ChestXrayDataset, MultiDiseaseModel, calculate_multilabel_accuracy
import torch
from torchvision.transforms import Compose, ToTensor, Normalize, Resize

class TestTrainScript(unittest.TestCase):
    def test_prepare_data(self):
        """Test if the prepare_data function creates the required directories."""
        prepare_data()
        self.assertTrue(os.path.exists("./downloads"))
        self.assertTrue(os.path.exists("./data"))
        self.assertTrue(os.path.exists("./data/images"))

    def test_dataset_initialization(self):
        """Test if the ChestXrayDataset initializes correctly."""
        # Create a mock DataFrame
        data = {
            'Image Index': ['image1.png', 'image2.png'],
            'Atelectasis': [1, 0],
            'Cardiomegaly': [0, 1]
        }
        df = pd.DataFrame(data)
        images_dir = "./data/images"

        # Create a mock dataset
        transform = Compose([
            Resize((128, 128)),
            ToTensor(),
            Normalize(mean=[0.5], std=[0.5])
        ])
        dataset = ChestXrayDataset(df, images_dir, transform=transform)

        self.assertEqual(len(dataset), 2)
        image, labels = dataset[0]
        self.assertEqual(labels.shape[0], 2)  # Two labels in the mock data

    def test_model_initialization(self):
        """Test if the MultiDiseaseModel initializes correctly."""
        num_classes = 14
        model = MultiDiseaseModel(num_classes)
        self.assertEqual(model.fc2.out_features, num_classes)

    def test_multilabel_accuracy(self):
        """Test the calculate_multilabel_accuracy function."""
        outputs = torch.tensor([[0.8, 0.2], [0.4, 0.9]])
        labels = torch.tensor([[1, 0], [0, 1]])
        accuracy = calculate_multilabel_accuracy(outputs, labels, threshold=0.5)
        self.assertAlmostEqual(accuracy, 1.0)  # All predictions are correct

    def test_data_split(self):
        """Test if the train-test split maintains stratification."""
        data = {
            'Finding Labels': ['Atelectasis', 'Cardiomegaly', 'Atelectasis', 'Cardiomegaly'],
            'Image Index': ['00000032_036.png', '00000096_001.png', '00000096_005.png', '00000099_011.png']
        }
        df = pd.DataFrame(data)
        train_df, valid_df = train_test_split(
            df, test_size=0.5, random_state=42, stratify=df['Finding Labels']
        )
        self.assertEqual(len(train_df), 2)
        self.assertEqual(len(valid_df), 2)
        self.assertEqual(train_df['Finding Labels'].nunique(), valid_df['Finding Labels'].nunique())

if __name__ == '__main__':
    unittest.main()
