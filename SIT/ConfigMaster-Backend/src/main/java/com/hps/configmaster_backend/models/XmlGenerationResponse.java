package com.hps.configmaster_backend.models;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class XmlGenerationResponse {
    private boolean success;
    
    @JsonProperty("xml_content")
    private String xmlContent;
    
    private String error;
    private String timestamp;
    
    @JsonProperty("bank_code")
    private String bankCode;
    
    @JsonProperty("xml_size")
    private Integer xmlSize;
    
    private String message;
}
