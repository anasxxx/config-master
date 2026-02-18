package com.hps.configmaster_backend.models;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import jakarta.validation.constraints.*;

public class MigBinRangePlasticProdModule {

    @NotBlank(message = "Bank code is required")
    @Size(max = 20, message = "Bank code must be at most 20 characters")
    private String bankCode;

    @Size(max = 50, message = "Description must be at most 50 characters")
    private String description;

    @Size(max = 20, message = "BIN must be at most 20 characters")
    private String bin;

    @Size(max = 20, message = "Plastic type must be at most 20 characters")
    private String plasticType;

    @Size(max = 20, message = "Product type must be at most 20 characters")
    private String productType;

    @NotBlank(message = "Product code is required")
    @Size(max = 20, message = "Product code must be at most 20 characters")
    private String productCode;

    @Size(max = 20, message = "Tranche min must be at most 20 characters")
    private String trancheMin;

    @Size(max = 20, message = "Tranche max must be at most 20 characters")
    private String trancheMax;

    @Size(max = 20, message = "Index PVK must be at most 20 characters")
    private String indexPvk;

    @Size(max = 20, message = "Service code must be at most 20 characters")
    private String serviceCode;

    @Size(max = 20, message = "Network must be at most 20 characters")
    private String network;

    @Size(max = 2, message = "Expiration must be at most 2 characters")
    private String expiration;

    @Size(max = 1, message = "Renew must be at most 1 character")
    private String renew;

    @Size(max = 1, message = "Prior Exp must be at most 1 character")
    private String priorExp;

	public String getBankCode() {
		return bankCode;
	}

	public void setBankCode(String bankCode) {
		this.bankCode = bankCode;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}

	public String getBin() {
		return bin;
	}

	public void setBin(String bin) {
		this.bin = bin;
	}

	public String getPlasticType() {
		return plasticType;
	}

	public void setPlasticType(String plasticType) {
		this.plasticType = plasticType;
	}

	public String getProductType() {
		return productType;
	}

	public void setProductType(String productType) {
		this.productType = productType;
	}

	public String getProductCode() {
		return productCode;
	}

	public void setProductCode(String productCode) {
		this.productCode = productCode;
	}

	public String getTrancheMin() {
		return trancheMin;
	}

	public void setTrancheMin(String trancheMin) {
		this.trancheMin = trancheMin;
	}

	public String getTrancheMax() {
		return trancheMax;
	}

	public void setTrancheMax(String trancheMax) {
		this.trancheMax = trancheMax;
	}

	public String getIndexPvk() {
		return indexPvk;
	}

	public void setIndexPvk(String indexPvk) {
		this.indexPvk = indexPvk;
	}

	public String getServiceCode() {
		return serviceCode;
	}

	public void setServiceCode(String serviceCode) {
		this.serviceCode = serviceCode;
	}

	public String getNetwork() {
		return network;
	}

	public void setNetwork(String network) {
		this.network = network;
	}

	public String getExpiration() {
		return expiration;
	}

	public void setExpiration(String expiration) {
		this.expiration = expiration;
	}

	public String getRenew() {
		return renew;
	}

	public void setRenew(String renew) {
		this.renew = renew;
	}

	public String getPriorExp() {
		return priorExp;
	}

	public void setPriorExp(String priorExp) {
		this.priorExp = priorExp;
	}
    
    
    
}
