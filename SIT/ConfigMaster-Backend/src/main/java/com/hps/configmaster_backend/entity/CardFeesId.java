package com.hps.configmaster_backend.entity;


import java.io.Serializable;
import java.util.Objects;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;

@Embeddable
public class CardFeesId implements Serializable {

    private String cardFeesCode;

    private String bankCode;

    // Constructeurs
    public CardFeesId() {}

    public CardFeesId(String cardFeesCode, String bankCode) {
        this.cardFeesCode = cardFeesCode;
        this.bankCode = bankCode;
    }

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

    // equals et hashCode
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof CardFeesId)) return false;
        CardFeesId that = (CardFeesId) o;
        return Objects.equals(cardFeesCode, that.cardFeesCode) &&
               Objects.equals(bankCode, that.bankCode);
    }

    @Override
    public int hashCode() {
        return Objects.hash(cardFeesCode, bankCode);
    }
}
