import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ModelPage } from '../src/pages/ModelPage';
import ApiService from '../src/services/api';

// Mock the ApiService
jest.mock('../src/services/api', () => ({
  analyzeImage: jest.fn(),
}));

describe('ModelPage Component', () => {
  test('renders upload area when no file is selected', () => {
    render(<ModelPage />);
    expect(screen.getByText(/Upload Medical Image/i)).toBeInTheDocument();
    expect(screen.getByText(/Drag and drop your image here/i)).toBeInTheDocument();
  });

  test('displays error message for invalid file type', () => {
    render(<ModelPage />);
    const fileInput = screen.getByRole('textbox', { hidden: true });
    const invalidFile = new File(['dummy content'], 'example.txt', { type: 'text/plain' });

    fireEvent.change(fileInput, { target: { files: [invalidFile] } });
    expect(screen.getByText(/Please select a valid image file/i)).toBeInTheDocument();
  });

  test('calls ApiService.analyzeImage when processing an image', async () => {
    const mockResponse = {
      predictions: [['Pneumonia'], { Pneumonia: 0.95 }],
    };
    ApiService.analyzeImage.mockResolvedValueOnce(mockResponse);

    render(<ModelPage />);
    const fileInput = screen.getByRole('textbox', { hidden: true });
    const validFile = new File(['dummy content'], 'example.jpg', { type: 'image/jpeg' });

    fireEvent.change(fileInput, { target: { files: [validFile] } });
    const analyzeButton = screen.getByText(/Analyze Image/i);

    fireEvent.click(analyzeButton);
    expect(ApiService.analyzeImage).toHaveBeenCalled();
  });

  test('renders analysis results after processing', async () => {
    const mockResponse = {
      predictions: [['Pneumonia'], { Pneumonia: 0.95 }],
    };
    ApiService.analyzeImage.mockResolvedValueOnce(mockResponse);

    render(<ModelPage />);
    const fileInput = screen.getByRole('textbox', { hidden: true });
    const validFile = new File(['dummy content'], 'example.jpg', { type: 'image/jpeg' });

    fireEvent.change(fileInput, { target: { files: [validFile] } });
    const analyzeButton = screen.getByText(/Analyze Image/i);

    fireEvent.click(analyzeButton);
    expect(await screen.findByText(/Analysis Complete/i)).toBeInTheDocument();
    expect(screen.getByText(/Pneumonia/i)).toBeInTheDocument();
  });
});
