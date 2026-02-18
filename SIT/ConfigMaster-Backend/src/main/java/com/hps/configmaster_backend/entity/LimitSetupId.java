package com.hps.configmaster_backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;

import java.io.Serializable;
import java.util.Objects;

@Embeddable
public class LimitSetupId implements Serializable {

	 @Column(name = "BANK_CODE", insertable = false, updatable = false)
	    private String bankCode;
	@Column(name = "LIMIT_INDEX", insertable = false, updatable = false)
    private String limitIndex;

    @Column(name = "LIMITS_ID")
    private Integer limitId;

    public LimitSetupId() {}

    public LimitSetupId(String limitIndex, String bankCode, Integer limitId) {
    	this.bankCode = bankCode;
    	this.limitIndex = limitIndex;
        
        this.limitId = limitId;
    }

    // Getters & Setters

    public String getLimitIndex() {
        return limitIndex;
    }

    public void setLimitIndex(String limitIndex) {
        this.limitIndex = limitIndex;
    }

    public String getBankCode() {
        return bankCode;
    }

    public void setBankCode(String bankCode) {
        this.bankCode = bankCode;
    }

    public Integer getLimitId() {
        return limitId;
    }

    public void setLimitId(Integer limitId) {
        this.limitId = limitId;
    }

    // equals() and hashCode() using all three fields

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof LimitSetupId)) return false;
        LimitSetupId that = (LimitSetupId) o;
        return Objects.equals(limitIndex, that.limitIndex) &&
               Objects.equals(bankCode, that.bankCode) &&
               Objects.equals(limitId, that.limitId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(limitIndex, bankCode, limitId);
    }
}
