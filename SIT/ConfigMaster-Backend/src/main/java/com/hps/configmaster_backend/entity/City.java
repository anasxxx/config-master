package com.hps.configmaster_backend.entity;

import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;


public class City {
	
	@Id
	@Column(name="CITY_CODE")
	private String cityCode;
	@Column(name="CITY_NAME")
	private String cityName;
	
	
	
	
	public String getCityName() {
		return cityName;
	}
	public void setCityName(String cityName) {
		this.cityName = cityName;
	}
	 


	

}
