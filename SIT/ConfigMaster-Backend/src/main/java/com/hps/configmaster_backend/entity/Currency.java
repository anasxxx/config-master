package com.hps.configmaster_backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "Currency_TABLE")
public class Currency {

    @Id
    @Column(name = "CURRENCY_CODE", length = 3)
    private String currencyCode;

    @Column(name = "CURRENCY_CODE_ALPHA", length = 3)
    private String currencyAlpha;

    @Column(name = "CURRENCY_NAME", length = 28)
    private String currencyName;

    // Getters and setters (optionnel selon ton usage)

    public String getCurrencyCode() {
        return currencyCode;
    }

    public void setCurrencyCode(String currencyCode) {
        this.currencyCode = currencyCode;
    }

    public String getCurrencyAlpha() {
        return currencyAlpha;
    }

    public void setCurrencyAlpha(String currencyAlpha) {
        this.currencyAlpha = currencyAlpha;
    }

    public String getCurrencyName() {
        return currencyName;
    }

    public void setCurrencyName(String currencyName) {
        this.currencyName = currencyName;
    }
}
