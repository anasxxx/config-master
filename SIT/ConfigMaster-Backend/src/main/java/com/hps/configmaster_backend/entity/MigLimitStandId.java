package com.hps.configmaster_backend.entity;

import java.io.Serializable;
import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;



@Embeddable
public class MigLimitStandId implements Serializable {

    @Column(name = "product_code", nullable = false, length = 20)
    private String productCode;

    @Column(name = "LIMITS_ID", nullable = false, length = 3)
    private String limitsId;

    // Constructeurs
 
    // Getters / Setters / equals() / hashCode()

    // Important : equals() et hashCode() doivent être bien générés pour que JPA fonctionne
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof MigLimitStandId)) return false;
        MigLimitStandId that = (MigLimitStandId) o;
        return productCode.equals(that.productCode) &&
               limitsId.equals(that.limitsId);
    }

    @Override
    public int hashCode() {
        return productCode.hashCode() + limitsId.hashCode();
    }

    // Getters and Setters
    public String getProductCode() {
        return productCode;
    }

    public void setProductCode(String productCode) {
        this.productCode = productCode;
    }

    // Backward-compatible aliases used by existing service code
    public String getBankCode() {
        return getProductCode();
    }

    public void setBankCode(String bankCode) {
        setProductCode(bankCode);
    }

    public String getLimitsId() {
        return limitsId;
    }

    public void setLimitsId(String limitsId) {
        this.limitsId = limitsId;
    }
}
