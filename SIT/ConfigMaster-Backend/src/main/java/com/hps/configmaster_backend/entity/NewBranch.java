package com.hps.configmaster_backend.entity;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;



@Entity
@Table(name = "st_pre_branch")

public class NewBranch {
    @Id
    @Column(name = "branch_code", length = 20)
    private String branchCode;
    
    @Column(name = "bank_code", length = 20)
    private String bankCode;
    
    @Column(name = "branch_wording", length = 20)
    private String branchWording;
    
    @Column(name = "region_code", length = 20)
    private String regionCode;
    
    @Column(name = "region_wording", length = 20)
    private String regionWording;
    
    @Column(name = "city_code", length = 20)
    private String cityCode;
    
    @Column(name = "city_wording", length = 20)
    private String cityWording;

	public String getBranchCode() {
		return branchCode;
	}

	public void setBranchCode(String branchCode) {
		this.branchCode = branchCode;
	}

	public String getBankCode() {
		return bankCode;
	}

	public void setBankCode(String bankCode) {
		this.bankCode = bankCode;
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
    
    
}
