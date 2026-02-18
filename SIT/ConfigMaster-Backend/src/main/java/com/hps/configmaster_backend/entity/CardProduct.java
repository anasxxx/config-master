package com.hps.configmaster_backend.entity;

import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.*;

@Entity
@IdClass(CardProductId.class)
@Table(name="CARD_PRODUCT")
public class CardProduct {
    	
    @Id
    @Column(name="PRODUCT_CODE")
    private String productCode;
       
    @Column(name="WORDING")
    private String description;
    
    @Column(name="PRODUCT_TYPE")
    private String productType;
    
    @Column(name="NETWORK_CODE")
    private String network;
    
    @Column(name="SERVICE_CODE")
    private String serviceCode;
    
    @Column(name="PLASTIC_TYPE")
    private String plasticType;
    
    @Column(name="VALIDITY_CODE_FIRST")
    private String expiration;
    
    @Column(name="RENEWAL_OPTION")
    private String renew;
    @Column(name="PRIOR_EXPIRY_DATE")
    private String priorExp;
    
    
    @Id
    @ManyToOne
    @JoinColumn(name = "BANK_CODE", referencedColumnName = "BANK_CODE")
    @JsonIgnore
    private Bank bank;
    
    @OneToMany(mappedBy = "cardProduct", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<LimitSetup> limits = new ArrayList<>();
    @Column(name="LIMITS_INDEXES")
    private String LIMITS_INDEXES;
    
    @Column(name="SERVICES_SETUP_INDEX")
    private String SERVICES_SETUP_INDEX;
    

    @OneToOne
    @JoinColumns({
        @JoinColumn(name = "BANK_CODE", referencedColumnName = "BANK_CODE"),
        @JoinColumn(name = "PRODUCT_CODE", referencedColumnName = "CARD_FEES_CODE")
    })
    private CardFees cardFees;
    
    @OneToOne
    @JoinColumns({
        @JoinColumn(name = "BANK_CODE", referencedColumnName = "ISSUING_BANK_CODE"),
        @JoinColumn(name = "PRODUCT_CODE", referencedColumnName = "PRODUCT_CODE")
    })
    private CardRange cardRange;
    



    
    
    // Relation One-to-Many vers P7ServicesSetup
    @OneToMany(mappedBy = "cardProduct", cascade = CascadeType.ALL)
    private List<ServiceSetup> p7ServicesSetup = new ArrayList<>();

   

    // Getters et setters

    public String getProductCode() {
        return productCode;
    }

    public void setProductCode(String productCode) {
        this.productCode = productCode;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getProductType() {
        return productType;
    }

    public void setProductType(String productType) {
        this.productType = productType;
    }

    public String getNetwork() {
        return network;
    }

    public void setNetwork(String network) {
        this.network = network;
    }
    

    public String getPriorExp() {
		return priorExp;
	}

	public void setPriorExp(String priorExp) {
		this.priorExp = priorExp;
	}

	public String getServiceCode() {
        return serviceCode;
    }

    public void setServiceCode(String serviceCode) {
        this.serviceCode = serviceCode;
    }

    public String getPlasticType() {
        return plasticType;
    }

    public void setPlasticType(String plasticType) {
        this.plasticType = plasticType;
    }

    public String getExpiration() {
        return expiration;
    }

    public void setExpiration(String expiration) {
        this.expiration = expiration;
    }

    

    
/*
    public List<CardFees> getCardFees() {
        return cardFees;
    }

    public void setCardFees(List<CardFees> cardFees) {
        this.cardFees = cardFees;
    }

    */

   
    public List<ServiceSetup> getP7ServicesSetup() {
        return p7ServicesSetup;
    }

    public void setP7ServicesSetup(List<ServiceSetup> p7ServicesSetup) {
        this.p7ServicesSetup = p7ServicesSetup;
    }

   

	public CardRange getCardRange() {
		return cardRange;
	}

	public void setCardRange(CardRange cardRanges) {
		this.cardRange = cardRanges;
	}

	public List<LimitSetup> getLimits() {
		return limits;
	}

	public void setLimits(List<LimitSetup> limits) {
		this.limits = limits;
	}

	public String getLIMITS_INDEXES() {
		return LIMITS_INDEXES;
	}

	public void setLIMITS_INDEXES(String lIMITS_INDEXES) {
		LIMITS_INDEXES = lIMITS_INDEXES;
	}
	

	

	

	public Bank getBank() {
		return bank;
	}

	public void setBank(Bank bank) {
		this.bank = bank;
	}

	public CardFees getCardFees() {
		return cardFees;
	}

	public void setCardFees(CardFees cardFees) {
		this.cardFees = cardFees;
	}

	public String getSERVICES_SETUP_INDEX() {
		return SERVICES_SETUP_INDEX;
	}

	public void setSERVICES_SETUP_INDEX(String sERVICES_SETUP_INDEX) {
		SERVICES_SETUP_INDEX = sERVICES_SETUP_INDEX;
	}

	public String getRenew() {
		return renew;
	}

	public void setRenew(String renew) {
		this.renew = renew;
	}
	
	
    
}
