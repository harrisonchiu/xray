package com.ace.backend.api.CXRBackendApi.payload;

import lombok.Data;

@Data
public class ModelResultDto {
    private String prediction;
    private byte[] imageData;
}
