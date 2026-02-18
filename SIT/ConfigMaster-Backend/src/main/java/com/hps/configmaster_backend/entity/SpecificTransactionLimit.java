package com.hps.configmaster_backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.IdClass;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;

@Entity
@IdClass(SpecificTransactionLimitId.class) 
@Table(name="P7_SPEC_TRANS_LIMITS")

public class SpecificTransactionLimit {
	
	@Column(name="SEQ_NUMBER")
	private Integer id;
	@Id
	@Column(name="LIMIT_INDEX")
    private String limitIndex;
	@Id
	@Column(name="BANK_CODE")
	private String bankCode;
	@Id
	@Column(name="LIMITS_ID")
	private Integer limitId;

	
	@Column(name="MIN_AMOUNT_PER_TRANSACTION")
    private String minAmountPerTransaction;
	
	@Column(name="MAX_AMOUNT_PER_TRANSACTION")
    private String maxAmountPerTransaction;

	@OneToOne(mappedBy = "specificTransactionLimit")
	private LimitSetup limitSetup;
	
	
	public String getMinAmountPerTransaction() {
		return minAmountPerTransaction;
	}

	
	public void setMinAmountPerTransaction(String minAmountPerTransaction) {
		this.minAmountPerTransaction = minAmountPerTransaction;
	}

	public String getMaxAmountPerTransaction() {
		return maxAmountPerTransaction;
	}

	public void setMaxAmountPerTransaction(String maxAmountPerTransaction) {
		this.maxAmountPerTransaction = maxAmountPerTransaction;
	}


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
	
	
	
	
	
	
	
	

}
