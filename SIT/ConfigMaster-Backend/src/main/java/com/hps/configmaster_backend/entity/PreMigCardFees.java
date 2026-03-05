package com.hps.configmaster_backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.math.BigDecimal;

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
    private BigDecimal cardFeesGracePeriod;

    @Column(name = "card_fees_billing_period")
    private String cardFeesBillingPeriod;

    @Column(name = "subscription_amount")
    private BigDecimal subscriptionAmount;

    @Column(name = "fees_amount_first")
    private BigDecimal feesAmountFirst;

    @Column(name = "damaged_replacement_fees")
    private BigDecimal damagedReplacementFees;

    @Column(name = "pin_replacement_fees")
    private BigDecimal pinReplacementFees;

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

    public BigDecimal getCardFeesGracePeriod() {
        return cardFeesGracePeriod;
    }

    public void setCardFeesGracePeriod(BigDecimal cardFeesGracePeriod) {
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
