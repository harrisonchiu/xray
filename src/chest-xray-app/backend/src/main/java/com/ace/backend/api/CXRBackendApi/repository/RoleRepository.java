package com.ace.backend.api.CXRBackendApi.repository;

import com.ace.backend.api.CXRBackendApi.entity.Role;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface RoleRepository extends JpaRepository<Role, Long> {
    Optional<Role> findByName(String name);
}
