package com.ace.backend.api.CXRBackendApi.service;

import com.ace.backend.api.CXRBackendApi.payload.LoginDto;
import com.ace.backend.api.CXRBackendApi.payload.RegisterDto;

public interface AuthService {
    String login(LoginDto loginDto);
    String register(RegisterDto registerDto);
}
