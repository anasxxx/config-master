package com.hps.configmaster_backend.models;

import java.math.BigDecimal;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Digits;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public class FeesRes {

	
	 private String bankCode; // Code de la banque
	 
	    private String description; // Description du frais

	    
	    private String cardFeesCode; // Code frais (clé primaire)

	   
	    
	    private String cardFeesBillingEvt; // Événement de facturation

	   
	    private Integer cardFeesGracePeriod; // Période de grâce en jours

	   
	    private String cardFeesBillingPeriod; // Période de facturation

	    
	    private BigDecimal subscriptionAmount; // Montant d'abonnement

	   
	    private BigDecimal feesAmountFirst; // Montant du premier frais

	   
	    private BigDecimal damagedReplacementFees; // Frais de remplacement carte endommagée

	    
	    private BigDecimal pinReplacementFees; // Frais de remplacement du code PIN


		public String getBankCode() {
			return bankCode;
		}


		public void setBankCode(String bankCode) {
			this.bankCode = bankCode;
		}


		public String getDescription() {
			return description;
		}


		public void setDescription(String description) {
			this.description = description;
		}


		public String getCardFeesCode() {
			return cardFeesCode;
		}


		public void setCardFeesCode(String cardFeesCode) {
			this.cardFeesCode = cardFeesCode;
		}


		public String getCardFeesBillingEvt() {
			return cardFeesBillingEvt;
		}


		public void setCardFeesBillingEvt(String cardFeesBillingEvt) {
			this.cardFeesBillingEvt = cardFeesBillingEvt;
		}


		public Integer getCardFeesGracePeriod() {
			return cardFeesGracePeriod;
		}


		public void setCardFeesGracePeriod(Integer cardFeesGracePeriod) {
			this.cardFeesGracePeriod = cardFeesGracePeriod;
		}


		public String getCardFeesBillingPeriod() {
			return cardFeesBillingPeriod;
		}


		public void setCardFeesBillingPeriod(String cardFeesBillingPeriod) {
			this.cardFeesBillingPeriod = cardFeesBillingPeriod;
		}


		public BigDecimal getSubscriptionAmount() {
			return subscriptionAmount;
		}


		public void setSubscriptionAmount(BigDecimal subscriptionAmount) {
			this.subscriptionAmount = subscriptionAmount;
		}


		public BigDecimal getFeesAmountFirst() {
			return feesAmountFirst;
		}


		public void setFeesAmountFirst(BigDecimal feesAmountFirst) {
			this.feesAmountFirst = feesAmountFirst;
		}


		public BigDecimal getDamagedReplacementFees() {
			return damagedReplacementFees;
		}


		public void setDamagedReplacementFees(BigDecimal damagedReplacementFees) {
			this.damagedReplacementFees = damagedReplacementFees;
		}


		public BigDecimal getPinReplacementFees() {
			return pinReplacementFees;
		}


		public void setPinReplacementFees(BigDecimal pinReplacementFees) {
			this.pinReplacementFees = pinReplacementFees;
		}

	    // Getters et setters

	
	
	
	
	
	
}
