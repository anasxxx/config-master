package com.hps.configmaster_backend.entity;

import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;


public class Region {

	@Id
	@Column(name="REGION_CODE")
	private String regionCode;
	
	@Column(name="REGION_NAME")
	private String regionName;
	
	
	 


	public String getRegionName() {
		return regionName;
	}

	public void setRegionName(String regionName) {
		this.regionName = regionName;
	}

	  

}
