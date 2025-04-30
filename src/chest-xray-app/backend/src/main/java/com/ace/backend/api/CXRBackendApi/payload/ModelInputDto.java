package com.ace.backend.api.CXRBackendApi.payload;

import lombok.Data;

@Data
public class ModelInputDto {
    private Long id;
    private byte[] imageData;
}
