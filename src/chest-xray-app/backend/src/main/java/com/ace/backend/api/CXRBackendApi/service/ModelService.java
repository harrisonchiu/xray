package com.ace.backend.api.CXRBackendApi.service;

import com.ace.backend.api.CXRBackendApi.payload.ModelInputDto;
import com.ace.backend.api.CXRBackendApi.payload.ModelResultDto;

public interface ModelService {

    ModelResultDto executeModel(ModelInputDto modelInputDto);
}
