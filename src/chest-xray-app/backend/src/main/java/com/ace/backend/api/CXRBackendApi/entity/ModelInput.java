package com.ace.backend.api.CXRBackendApi.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Entity // maps our JPA Entity to our MySql Table
@Table(name = "modelInputs")
public class ModelInput {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Lob  // Large Object (for storing binary data)
    @Column(columnDefinition = "LONGBLOB") // MySQL LONGBLOB for large binary data
    private byte[] imageData;
}
