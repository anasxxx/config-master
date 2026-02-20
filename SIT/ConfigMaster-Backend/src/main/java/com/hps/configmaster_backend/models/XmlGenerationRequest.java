package com.hps.configmaster_backend.models;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class XmlGenerationRequest {
    private String bank_code;
    private String product_code;
    private String request_id;
}
