package com.hps.configmaster_backend.models;

import java.util.List;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public class CardProductRes {

	 

	    private String description;

	    private String bin;

	    private String plasticType;

	    private String productType;

	    private String productCode;

	    private String trancheMin;

	    private String trancheMax;

	    private String indexPvk;

	    private String serviceCode;

	    private String network;

	    private String expiration;

	    private String renew;

	    private String priorExp;

		
        private FeesRes fees;
        
        private MigServiceProdModule services;
        
        private List<MigLimitStandModule> limits;
        
		

		public MigServiceProdModule getServices() {
			return services;
		}

		public void setServices(MigServiceProdModule services) {
			this.services = services;
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

		public FeesRes getFees() {
			return fees;
		}

		public void setFees(FeesRes fees) {
			this.fees = fees;
		}

		public List<MigLimitStandModule> getLimits() {
			return limits;
		}

		public void setLimits(List<MigLimitStandModule> limits) {
			this.limits = limits;
		}

		
		
	    
	    
	}
