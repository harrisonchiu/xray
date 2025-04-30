package com.ace.backend.api.CXRBackendApi.exception;

import org.springframework.http.HttpStatus;

public class APIException extends RuntimeException {
    private final HttpStatus status;

    public APIException(String message, HttpStatus status) {
        super(message);
        this.status = status;
    }

    public HttpStatus getStatus() {
        return status;
    }

    @Override
    public String getMessage(){
        return super.getMessage();
    }
}
