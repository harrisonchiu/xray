package com.ace.backend.api.CXRBackendApi.service.impl;

import com.ace.backend.api.CXRBackendApi.entity.ModelInput;
import com.ace.backend.api.CXRBackendApi.entity.ModelResult;
import com.ace.backend.api.CXRBackendApi.payload.ModelInputDto;
import com.ace.backend.api.CXRBackendApi.payload.ModelResultDto;
import com.ace.backend.api.CXRBackendApi.service.ModelService;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import org.modelmapper.ModelMapper;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.Resource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;

@Service
public class ModelServiceImpl implements ModelService {

    private final ModelMapper mapper;
    private final RestTemplate restTemplate;

    public ModelServiceImpl(ModelMapper mapper, RestTemplate restTemplate) {
        this.mapper = mapper;
        this.restTemplate = restTemplate;
    }



    @Override
    public ModelResultDto executeModel(ModelInputDto modelInputDto) {
        try {
            // Extract image bytes from DTO
            byte[] imageData = modelInputDto.getImageData();  // ✅ Image as byte[]

            // Flask API URL
            String flaskApiUrl = "http://127.0.0.1:5001/predict";


            // Create HTTP headers for multipart request
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            // Convert byte[] to ByteArrayResource
            Resource imageResource = new ByteArrayResource(imageData) {
                @Override
                public String getFilename() {
                    return "input_image.png"; // ✅ Flask expects a filename
                }
            };

            // Create form-data request body
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", imageResource);

            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

            // Send POST request to Flask API
            ResponseEntity<String> response = restTemplate.exchange(
                    flaskApiUrl, HttpMethod.POST, requestEntity, String.class
            );

            // Convert JSON response to ModelResultDto
            ModelResult modelResult = convertAPIResponseToModelResult(response.getBody());
            ModelResultDto modelResultDto = mapModelResultToDTO(modelResult);
            return modelResultDto;

        } catch (Exception e) {
            e.printStackTrace();
            return null; // Handle errors gracefully
        }
    }

//    @Override
//    public ModelResultDto executeModel(ModelInputDto modelInputDto) {
//        // 1. convert ModelInputDTO to ModelInput Entity
//        // 2. call HuggingFace API Models given imageData input from ModelInput entity
//        // 3. convert return JSON String to ModelResultEntity
//        // 4. if successful, save ModelInput & ModelResult entities
//        // 5. convert ModelResult entity to ModelResultDTO
//        // 6. return ModelResultDTO
//        return null;
//    }

    private ModelResult convertAPIResponseToModelResult(String modelJsonResult) {
        try {
            // ✅ Parse JSON response using Jackson
            ObjectMapper objectMapper = new ObjectMapper();
            Map<String, Object> responseMap = objectMapper.readValue(modelJsonResult, Map.class);

            // ✅ Extract predictions from JSON
            List<String> predictions = (List<String>) responseMap.get("predictions");
            String resultString = String.join(", ", predictions); // Convert list to comma-separated string

            // ✅ Create and return a ModelResult object
            ModelResult modelResult = new ModelResult();
            modelResult.setResult(resultString);
            return modelResult;

        } catch (Exception e) {
            e.printStackTrace();
            return null; // Handle error gracefully
        }
    }

    @PostConstruct
    public void testFlaskConnection() {
        try {
            String flaskApiUrl = "http://127.0.0.1:5001/predict";
            RestTemplate restTemplate = new RestTemplate();
            ResponseEntity<String> response = restTemplate.exchange(flaskApiUrl, HttpMethod.GET, null, String.class);
            System.out.println("✅ Successfully connected to Flask: " + response.getBody());
        } catch (Exception e) {
            System.out.println("❌ Java cannot reach Flask API.");
            e.printStackTrace();
        }
    }


    private ModelInput mapModelInputDToToEntity(ModelInputDto modelInputDto){
        return mapper.map(modelInputDto, ModelInput.class);
    }

    private ModelResultDto mapModelResultToDTO(ModelResult modelResult){
        return mapper.map(modelResult, ModelResultDto.class);
    }
}
