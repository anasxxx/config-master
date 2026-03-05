package com.hps.configmaster_backend.models;
import jakarta.validation.constraints.*;
import java.math.BigDecimal;

public class PreMigCardFeesModule {
	@NotNull
    @Size(min = 1, max = 20)
    private String bankCode; // Code de la banque
	 
    @Size(max = 30)
    private String description; // Description du frais

    @NotNull
    @Size(min = 3, max = 3)
    private String cardFeesCode; // Code frais (clé primaire)

   
    @NotNull
    @Size(min = 1, max = 1)
    private String cardFeesBillingEvt; // Événement de facturation

    @Min(0)
    @Max(365)
    private BigDecimal cardFeesGracePeriod; // Période de grâce en jours

    @NotNull
    @Size(min = 1, max = 1)
    private String cardFeesBillingPeriod; // Période de facturation

    @NotNull
    private BigDecimal subscriptionAmount; // Montant d'abonnement

    @NotNull
    private BigDecimal feesAmountFirst; // Montant du premier frais

    private BigDecimal damagedReplacementFees; // Frais de remplacement carte endommagée

    private BigDecimal pinReplacementFees; // Frais de remplacement du code PIN

    // Getters et setters

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
