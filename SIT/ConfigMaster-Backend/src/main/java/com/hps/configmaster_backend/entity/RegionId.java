package com.hps.configmaster_backend.entity;

import java.io.Serializable;
import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
import java.util.Objects;

@Embeddable
public class RegionId implements Serializable {

    @Column(name = "REGION_CODE")
    private String regionCode;

    @Column(name = "COUNTRY_CODE")
    private String countryCode;

    public RegionId() {}

    public RegionId(String regionCode, String countryCode) {
        this.regionCode = regionCode;
        this.countryCode = countryCode;
    }

    public String getRegionCode() {
        return regionCode;
    }

    public void setRegionCode(String regionCode) {
        this.regionCode = regionCode;
    }

    public String getCountryCode() {
        return countryCode;
    }

    public void setCountryCode(String countryCode) {
        this.countryCode = countryCode;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof RegionId)) return false;
        RegionId that = (RegionId) o;
        return Objects.equals(regionCode, that.regionCode) &&
               Objects.equals(countryCode, that.countryCode);
    }

    @Override
    public int hashCode() {
        return Objects.hash(regionCode, countryCode);
    }
}
