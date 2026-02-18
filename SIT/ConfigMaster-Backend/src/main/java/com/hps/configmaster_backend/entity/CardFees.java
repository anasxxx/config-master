package com.hps.configmaster_backend.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;

import com.fasterxml.jackson.annotation.JsonIgnore;

@Entity
@IdClass(CardFeesId.class)
@Table(name="CARD_FEES")
public class CardFees {

    @Id
    @Column(name = "CARD_FEES_CODE")
    private String cardFeesCode;
    @Id
    @Column(name = "BANK_CODE")
    private String bankCode;

   

    @Column(name = "DESCRIPTION")
    private String description;

    @Column(name = "CARD_FEES_BILLING_EVT")
    private String cardFeesBillingEvt;

    @Column(name = "CARD_FEES_GRACE_PERIOD")
    private Integer cardFeesGracePeriod;

    @Column(name = "CARD_FEES_BILLING_PERIOD")
    private String cardFeesBillingPeriod;

    @Column(name = "SUBSCRIPTION_AMOUNT")
    private BigDecimal subscriptionAmount;

    @Column(name = "FEES_AMOUNT_FIRST")
    private BigDecimal feesAmountFirst;

    @Column(name = "DAMAGED_REPLACEMENT_FEES")
    private BigDecimal damagedReplacementFees;

    @Column(name = "PIN_REPLACEMENT_FEES")
    private BigDecimal pinReplacementFees;
    
    


	public String getCardFeesCode() {
		return cardFeesCode;
	}

	public void setCardFeesCode(String cardFeesCode) {
		this.cardFeesCode = cardFeesCode;
	}

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

	
    
 



   
}
