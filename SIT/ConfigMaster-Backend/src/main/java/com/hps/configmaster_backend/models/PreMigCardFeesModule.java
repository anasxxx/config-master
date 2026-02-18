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
    private Integer cardFeesGracePeriod; // Période de grâce en jours

    @NotNull
    @Size(min = 1, max = 1)
    private String cardFeesBillingPeriod; // Période de facturation

    @NotNull
    @DecimalMin(value = "0.0", inclusive = false)
    @Digits(integer = 18, fraction = 3)
    private String subscriptionAmount; // Montant d'abonnement

    @NotNull
    @DecimalMin(value = "0.0", inclusive = false)
    @Digits(integer = 18, fraction = 3)
    private String feesAmountFirst; // Montant du premier frais

    @DecimalMin(value = "0.0", inclusive = false)
    @Digits(integer = 18, fraction = 3)
    private String damagedReplacementFees; // Frais de remplacement carte endommagée

    @DecimalMin(value = "0.0", inclusive = false)
    @Digits(integer = 18, fraction = 3)
    private String pinReplacementFees; // Frais de remplacement du code PIN

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
