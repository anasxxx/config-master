package com.hps.configmaster_backend.entity;




import java.io.Serializable;
import java.util.Objects;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;
@Embeddable

public class BranchId implements Serializable {
	

    private String bankCode;
    private String branchCode;
    
    
    public BranchId() {}
    
    public BranchId(String branchCode, String bankCode) {
        this.branchCode = branchCode;
        this.bankCode = bankCode;
    }
    
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
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof BranchId)) return false;
        BranchId that = (BranchId) o;
        return Objects.equals(branchCode, that.branchCode) &&
               Objects.equals(bankCode, that.bankCode);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(branchCode, bankCode);
    }
}