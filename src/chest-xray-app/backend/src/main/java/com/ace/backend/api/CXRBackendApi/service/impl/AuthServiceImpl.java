package com.ace.backend.api.CXRBackendApi.service.impl;

import com.ace.backend.api.CXRBackendApi.entity.Role;
import com.ace.backend.api.CXRBackendApi.entity.User;
import com.ace.backend.api.CXRBackendApi.exception.APIException;
import com.ace.backend.api.CXRBackendApi.payload.LoginDto;
import com.ace.backend.api.CXRBackendApi.payload.RegisterDto;
import com.ace.backend.api.CXRBackendApi.repository.RoleRepository;
import com.ace.backend.api.CXRBackendApi.repository.UserRepository;
import com.ace.backend.api.CXRBackendApi.security.JwtTokenProvider;
import com.ace.backend.api.CXRBackendApi.service.AuthService;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.Optional;
import java.util.Set;

@Service
public class AuthServiceImpl implements AuthService {
    private final AuthenticationManager authenticationManager;
    private PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;

    private UserRepository userRepository;
    private RoleRepository roleRepository;

    public AuthServiceImpl(AuthenticationManager authenticationManager,
                           PasswordEncoder passwordEncoder,
                           JwtTokenProvider jwtTokenProvider,
                           UserRepository userRepository,
                           RoleRepository roleRepository) {
        this.authenticationManager = authenticationManager;
        this.passwordEncoder = passwordEncoder;
        this.jwtTokenProvider = jwtTokenProvider;
        this.userRepository = userRepository;
        this.roleRepository = roleRepository;
    }


    @Override
    public String login(LoginDto loginDto) {
        Authentication authentication = authenticationManager.authenticate(new UsernamePasswordAuthenticationToken(
                loginDto.getUsernameOrEmail(),
                loginDto.getPassword()
        ));

        SecurityContextHolder.getContext().setAuthentication(authentication);

        return jwtTokenProvider.generateToken(authentication);
    }

    @Override
    public String register(RegisterDto registerDto) {
        // check that username doesnt already exist in the database
        if(userRepository.existsByUsername(registerDto.getUsername())){
            throw new APIException("Username already exists", HttpStatus.BAD_REQUEST);
        }
        if(userRepository.existsByEmail(registerDto.getEmail())){
            throw new APIException("Email already in use", HttpStatus.BAD_REQUEST);
        }

        User user = new User();
        user.setName(registerDto.getName());
        user.setUsername(registerDto.getUsername());
        user.setEmail(registerDto.getEmail());
        user.setPassword(passwordEncoder.encode(registerDto.getPassword()));

        Set<Role> roles = new HashSet<>();
        Optional<Role> role = roleRepository.findByName("ROLE_USER");
        role.ifPresent(roles::add);
        user.setRoles(roles);

        userRepository.save(user);
        return "User successfully registered";
    }
}
