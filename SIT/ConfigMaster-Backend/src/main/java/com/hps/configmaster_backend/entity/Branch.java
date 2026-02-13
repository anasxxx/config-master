package com.hps.configmaster_backend.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;

@Entity
@Table(name = "BRANCH")
public class Branch {

    @Id
    @Column(name = "BRANCH_CODE")
    private String branchCode;

    @Column(name = "BRANCH_NAME")
    private String branchWording;
    @Column(name = "REGION_CODE")

    private String regionCode;

    @Column(name = "REGION_NAME")

    private String regionWording;
    
    @Column(name = "CITY_CODE")
    private String cityCode;
    @Column(name = "CITY_NAME")
    private String cityWording;


    @ManyToOne
    @JoinColumn(name = "BANK_CODE", referencedColumnName = "BANK_CODE") // BANK_CODE is the foreign key here
    @JsonIgnore  // Ignore la sérialisation de cette propriété

    private Bank bank;


	public String getBranchCode() {
		return branchCode;
	}


	public void setBranchCode(String branchCode) {
		this.branchCode = branchCode;
	}


	public String getBranchWording() {
		return branchWording;
	}


	public void setBranchWording(String branchWording) {
		this.branchWording = branchWording;
	}


	public String getRegionCode() {
		return regionCode;
	}


	public void setRegionCode(String regionCode) {
		this.regionCode = regionCode;
	}


	public String getRegionWording() {
		return regionWording;
	}


	public void setRegionWording(String regionWording) {
		this.regionWording = regionWording;
	}


	public String getCityCode() {
		return cityCode;
	}


	public void setCityCode(String cityCode) {
		this.cityCode = cityCode;
	}


	public String getCityWording() {
		return cityWording;
	}


	public void setCityWording(String cityWording) {
		this.cityWording = cityWording;
	}


	public Bank getBank() {
		return bank;
	}


	public void setBank(Bank bank) {
		this.bank = bank;
	}


	    
}
