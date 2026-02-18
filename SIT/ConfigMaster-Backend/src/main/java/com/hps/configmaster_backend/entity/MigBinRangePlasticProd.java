package com.hps.configmaster_backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;



@Entity
@Table(name = "st_pre_bin_range_plastic_prod")

public class MigBinRangePlasticProd {
    
    @Column(name = "bank_code", length = 20)
    private String bankCode;
    
    @Column(name = "description", length = 50)
    private String description;
    
    @Column(name = "bin", length = 20)
    private String bin;
    
    @Column(name = "plastic_type", length = 20)
    private String plasticType;
    
    @Column(name = "product_type", length = 20)
    private String productType;
    @Id
    @Column(name = "product_code", length = 3)
    private String productCode;
    
    @Column(name = "tranche_min", length = 20)
    private String trancheMin;
    
    @Column(name = "tranche_max", length = 20)
    private String trancheMax;
    
    @Column(name = "index_pvk", length = 20)
    private String indexPvk;
    
    @Column(name = "service_code", length = 20)
    private String serviceCode;
    
    @Column(name = "network", length = 20)
    private String network;
    
    @Column(name = "expiration", length = 2)
    private String expiration;
    
    @Column(name = "renew", length = 1)
    private String renew;
    
    @Column(name = "prior_exp", length = 1)
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