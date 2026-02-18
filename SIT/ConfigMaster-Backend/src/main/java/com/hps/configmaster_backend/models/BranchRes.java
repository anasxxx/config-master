
package com.hps.configmaster_backend.models;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public class BranchRes {

    

    @NotNull(message = "Branch code cannot be null")
    @Size(max = 20, message = "Branch code cannot exceed 20 characters")
    private String branchCode;

    @NotNull(message = "Branch wording cannot be null")
    @Size(max = 20, message = "Branch wording cannot exceed 20 characters")
    private String branchWording;

    @NotNull(message = "Region code cannot be null")
    @Size(max = 20, message = "Region code cannot exceed 20 characters")
    private String regionCode;

    @NotNull(message = "Region wording cannot be null")
    @Size(max = 20, message = "Region wording cannot exceed 20 characters")
    private String regionWording;

    @NotNull(message = "City code cannot be null")
    @Size(max = 20, message = "City code cannot exceed 20 characters")
    private String cityCode;

    @NotNull(message = "City wording cannot be null")
    @Size(max = 20, message = "City wording cannot exceed 20 characters")
    private String cityWording;

   

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
}
