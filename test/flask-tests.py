import unittest
from io import BytesIO
from app import app

class FlaskBackendTests(unittest.TestCase):
    def setUp(self):
        # Set up the Flask test client
        self.app = app.test_client()
        self.app.testing = True

    def test_test_connection_endpoint(self):
        """Test the /test endpoint for connectivity"""
        response = self.app.get('/test')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Flask API is reachable!', response.get_json().get('message', ''))

    def test_predict_endpoint_no_file(self):
        """Test the /predict endpoint with no file uploaded"""
        response = self.app.post('/predict')
        self.assertEqual(response.status_code, 400)
        self.assertIn('No file uploaded', response.get_json().get('error', ''))

    def test_predict_endpoint_invalid_file(self):
        """Test the /predict endpoint with an invalid file type"""
        data = {
            'file': (BytesIO(b"Not an image"), 'test.txt')
        }
        response = self.app.post('/predict', content_type='multipart/form-data', data=data)
        self.assertEqual(response.status_code, 500)
        self.assertIn('Prediction failed', response.get_json().get('error', ''))

    def test_predict_endpoint_valid_image(self):
        """Test the /predict endpoint with a valid image file"""
        # Create a dummy image file
        dummy_image = BytesIO()
        from PIL import Image
        image = Image.new('RGB', (256, 256), color='white')
        image.save(dummy_image, format='JPEG')
        dummy_image.seek(0)

        data = {
            'file': (dummy_image, 'test.jpg')
        }
        response = self.app.post('/predict', content_type='multipart/form-data', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('predictions', response.get_json())

if __name__ == '__main__':
    unittest.main()
