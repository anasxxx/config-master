package com.hps.configmaster_backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "st_pre_mig_CARD_FEES")
public class PreMigCardFees {

    @Column(name = "bank_code")
    private String bankCode;
    @Column(name = "description")
    private String description;

    @Id
    @Column(name = "card_fees_code")
    private String cardFeesCode;

    
    @Column(name = "card_fees_billing_evt")
    private String cardFeesBillingEvt;

    @Column(name = "card_fees_grace_period")
    private Integer cardFeesGracePeriod;

    @Column(name = "card_fees_billing_period")
    private String cardFeesBillingPeriod;

    @Column(name = "subscription_amount")
    private String subscriptionAmount;

    @Column(name = "fees_amount_first")
    private String feesAmountFirst;

    @Column(name = "damaged_replacement_fees")
    private String damagedReplacementFees;

    @Column(name = "pin_replacement_fees")
    private String pinReplacementFees;

    // Getters and Setters

    public String getBankCode() {
        return bankCode;
    }

    public void setBankCode(String bankCode) {
        this.bankCode = bankCode;
    }

    public String getCardFeesCode() {
        return cardFeesCode;
    }

    public void setCardFeesCode(String cardFeesCode) {
        this.cardFeesCode = cardFeesCode;
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

	public String getSubscriptionAmount() {
		return subscriptionAmount;
	}

	public void setSubscriptionAmount(String subscriptionAmount) {
		this.subscriptionAmount = subscriptionAmount;
	}

	public String getFeesAmountFirst() {
		return feesAmountFirst;
	}

	public void setFeesAmountFirst(String feesAmountFirst) {
		this.feesAmountFirst = feesAmountFirst;
	}

	public String getDamagedReplacementFees() {
		return damagedReplacementFees;
	}

	public void setDamagedReplacementFees(String damagedReplacementFees) {
		this.damagedReplacementFees = damagedReplacementFees;
	}

	public String getPinReplacementFees() {
		return pinReplacementFees;
	}

	public void setPinReplacementFees(String pinReplacementFees) {
		this.pinReplacementFees = pinReplacementFees;
	}

    
}
