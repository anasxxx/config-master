package com.hps.configmaster_backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "st_pre_resources")
public class MigResources {
    @Column(name = "bank_code", length = 20)
    private String bankCode;
    @Id
    @Column(name = "resource_wording", length = 20)
    private String resourceWording;

	public String getBankCode() {
		return bankCode;
	}

	public void setBankCode(String bankCode) {
		this.bankCode = bankCode;
	}

	public String getResourceWording() {
		return resourceWording;
	}

	public void setResourceWording(String resourceWording) {
		this.resourceWording = resourceWording;
	}
    
    
}