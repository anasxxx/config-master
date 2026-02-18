package com.hps.configmaster_backend.entity;

import java.io.Serializable;
import java.util.Objects;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;

@Embeddable
public class SpecificTransactionLimitId implements Serializable {

    @Column(name = "LIMIT_INDEX")
    private String limitIndex;

    @Column(name = "BANK_CODE")
    private String bankCode;

    @Column(name = "LIMITS_ID")
    private Integer limitId;

    // Constructeurs
    public SpecificTransactionLimitId() {}

    public SpecificTransactionLimitId(String limitIndex, String bankCode, Integer limitId) {
        this.limitIndex = limitIndex;
        this.bankCode = bankCode;
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

    // equals() et hashCode() obligatoires
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof SpecificTransactionLimitId)) return false;
        SpecificTransactionLimitId that = (SpecificTransactionLimitId) o;
        return Objects.equals(limitIndex, that.limitIndex) &&
               Objects.equals(bankCode, that.bankCode) &&
               Objects.equals(limitId, that.limitId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(limitIndex, bankCode, limitId);
    }
}
