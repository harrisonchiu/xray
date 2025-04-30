package com.ace.backend.api.CXRBackendApi.controller;

import com.ace.backend.api.CXRBackendApi.payload.ModelInputDto;
import com.ace.backend.api.CXRBackendApi.payload.ModelResultDto;
import com.ace.backend.api.CXRBackendApi.service.ModelService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/api/model")
public class ModelController {

    private final ModelService modelService;
    private RestTemplate restTemplate;

    public ModelController(ModelService modelService, RestTemplate restTemplate) {
        this.modelService = modelService;
        this.restTemplate = restTemplate;
    }

    // submit ModelInput to ML Model
    @PostMapping()
    public ResponseEntity<ModelResultDto> executeModel(@RequestBody ModelInputDto modelInputDto){
        ModelResultDto modelResultDto = modelService.executeModel(modelInputDto);
        return new ResponseEntity<>(modelResultDto, HttpStatus.CREATED);
    }

    // ✅ New method: Test Flask connectivity via GET request
    @GetMapping("/test-flask")
    public ResponseEntity<String> testFlask() {
        try {
            String flaskApiUrl = "http://127.0.0.1:5001/test";
            ResponseEntity<String> response = restTemplate.getForEntity(flaskApiUrl, String.class);
            return ResponseEntity.ok("✅ Flask Response: " + response.getBody());
        } catch (Exception e) {
            e.printStackTrace();  // Logs the full error
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("❌ Failed to connect to Flask: " + e.getMessage());
        }
    }


}
