package com.ace.backend.api.CXRBackendApi.repository;

import com.ace.backend.api.CXRBackendApi.entity.ModelResult;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ModelResultRepository extends JpaRepository<ModelResult, Long> {
    // JpaRepository already implements all methods needed to communicate with the database internally
}
