package com.ace.backend.api.CXRBackendApi.entity;

import jakarta.persistence.*;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Entity // maps our JPA Entity to our MySql Table
@Table(name = "modelResults")
public class ModelResult {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Lob  // Large Object (for storing binary data)
    @Column(name = "image", columnDefinition = "LONGBLOB") // MySQL LONGBLOB for large binary data
    private byte[] imageData;

    @Column(name = "model_result")
    private String result;
}