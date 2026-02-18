package com.hps.configmaster_backend.entity;

import java.io.Serializable;

public class CardRangeId implements Serializable {

    private String codeBank;
    private String codeProduct;

    // Constructeurs, getters et setters

    public CardRangeId() {}

    public CardRangeId(String codeBank, String codeProduct) {
        this.codeBank = codeBank;
        this.codeProduct = codeProduct;
    }

    // Getters et setters
    public String getCodeBank() {
        return codeBank;
    }

    public void setCodeBank(String codeBank) {
        this.codeBank = codeBank;
    }

    public String getCodeProduct() {
        return codeProduct;
    }

    public void setCodeProduct(String codeProduct) {
        this.codeProduct = codeProduct;
    }

    // equals et hashCode pour que les instances soient comparables
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        CardRangeId that = (CardRangeId) o;
        return codeBank.equals(that.codeBank) && codeProduct.equals(that.codeProduct);
    }

    @Override
    public int hashCode() {
        return 31 * codeBank.hashCode() + codeProduct.hashCode();
    }
}
