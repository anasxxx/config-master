package com.hps.configmaster_backend.models;

import java.util.List;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public class CardProductodule {
    
	private MigBinRangePlasticProdModule info;
	
    private PreMigCardFeesModule fees;
    
    private MigServiceProdModule services;
    
    private List<MigLimitStandModule> limits;


	public PreMigCardFeesModule getFees() {
		return fees;
	}

	public void setFees(PreMigCardFeesModule fees) {
		this.fees = fees;
	}

	public MigServiceProdModule getServices() {
		return services;
	}

	public void setServices(MigServiceProdModule services) {
		this.services = services;
	}

	public List<MigLimitStandModule> getLimits() {
		return limits;
	}

	public void setLimits(List<MigLimitStandModule> limits) {
		this.limits = limits;
	}

	public MigBinRangePlasticProdModule getInfo() {
		return info;
	}

	public void setInfo(MigBinRangePlasticProdModule info) {
		this.info = info;
	}
     
   
    
    
}