package com.hps.configmaster_backend.entity;

import java.io.Serializable;
import java.util.Objects;

public class CardProductId implements Serializable {
	
    private String productCode;
    private String bank;

    // constructeurs
    public CardProductId() {}

    public CardProductId(String productCode, String bank) {
        this.productCode = productCode;
        this.bank = bank;
    }

    // equals et hashCode
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof CardProductId)) return false;
        CardProductId that = (CardProductId) o;
        return Objects.equals(productCode, that.productCode) &&
               Objects.equals(bank, that.bank);
    }

    @Override
    public int hashCode() {
        return Objects.hash(productCode, bank);
    }
}
