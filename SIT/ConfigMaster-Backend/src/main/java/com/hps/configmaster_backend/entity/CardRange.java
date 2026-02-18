package com.hps.configmaster_backend.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.IdClass;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.JoinColumns;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;
import jakarta.persistence.UniqueConstraint;
@Entity
@Table(name = "card_range", 
       uniqueConstraints = @UniqueConstraint(columnNames = {"MIN_CARD_RANGE", "MAX_CARD_RANGE"})) // Assure que la combinaison est unique
@IdClass(CardRangeId.class)  // Utilisation de la clé composite
public class CardRange {

    @Column(name = "MIN_CARD_RANGE")
    private String trancheMin;

    @Column(name = "MAX_CARD_RANGE")
    private String trancheMax;

    @Column(name = "ISSUER_BIN")
    private String bin;

    @Column(name = "PVKI")
    private String indexPvk;
    @Id
    @Column(name = "ISSUING_BANK_CODE")
    private String codeBank;
    @Id
    @Column(name = "PRODUCT_CODE")
    private String codeProduct;

    
    


    
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

	// Getters et setters
    public String getTrancheMin() {
        return trancheMin;
    }

    public void setTrancheMin(String trancheMin) {
        this.trancheMin = trancheMin;
    }

    public String getTrancheMax() {
        return trancheMax;
    }

    public void setTrancheMax(String trancheMax) {
        this.trancheMax = trancheMax;
    }

   

	public String getBin() {
        return bin;
    }

    public void setBin(String bin) {
        this.bin = bin;
    }

    public String getIndexPvk() {
        return indexPvk;
    }

    public void setIndexPvk(String indexPvk) {
        this.indexPvk = indexPvk;
    }


}
