package com.hps.configmaster_backend.entity;

import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;


public class Limit {
	
	@Column(name="BANK_CODE")
    private String codeBank;
	@Id
	@Column(name="LIMITS_INDEXES")
    private String limitIndex;
	
	 @OneToMany(mappedBy = "limitIndex", cascade = CascadeType.ALL, orphanRemoval = true)
	    private List<LimitSetup> limits = new ArrayList<>();
	  
	 @ManyToOne
	 @JoinColumn(name = "limitIndex") // le nom de la colonne FK dans LIMIT qui référence CARD_PRODUCT
	 private CardProduct cardProduct;


	public String getCodeBank() {
		return codeBank;
	}

	public void setCodeBank(String codeBank) {
		this.codeBank = codeBank;
	}

	public String getLimitIndex() {
		return limitIndex;
	}

	public void setLimitIndex(String limitIndex) {
		this.limitIndex = limitIndex;
	}

	public List<LimitSetup> getLimits() {
		return limits;
	}

	public void setLimits(List<LimitSetup> limits) {
		this.limits = limits;
	}

	public CardProduct getCardProduct() {
		return cardProduct;
	}

	public void setCardProduct(CardProduct cardProduct) {
		this.cardProduct = cardProduct;
	}

	
	
	

}
