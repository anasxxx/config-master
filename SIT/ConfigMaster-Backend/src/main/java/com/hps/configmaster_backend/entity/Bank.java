package com.hps.configmaster_backend.entity;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Set;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonManagedReference;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;

@Entity
@Table(name="BANK")
public class Bank {
	 @Id
	 @Column(name = "BANK_CODE", length = 6)
	    private String  bankCode; 
	 @Column(name = "BANK_NAME", length = 40)
	    private String bankName;                 
	 @Column(name = "COUNTRY_CODE", length = 3)
	    private String countryCode;              
	 @Column(name = "BANK_CURRENCY_CODE", length = 3)

	 
	    private String currencyCode; 
	 @Column(name="CATEGORY")
	 private String category;
	 @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")

     @Column(name = "DATE_CREATE")
        private Date businessDate; 
     
    @OneToMany(mappedBy = "bank", cascade = CascadeType.ALL, orphanRemoval = true)
      private Set<Branch> branches ;
     
     
	@OneToMany(mappedBy = "bank", cascade = CascadeType.ALL, orphanRemoval = true)
	  
	private Set<CardProduct> prodcuts;
	  
	@OneToMany(mappedBy = "bank", cascade = CascadeType.ALL, orphanRemoval = true)
	  
	private Set<RessourceParam> Ressources;
    
    
    public Set<Branch> getBranches() {
		return branches;
	}

	public void setBranches(Set<Branch> branches) {
		this.branches = branches;
	}

	public Set<CardProduct> getProdcuts() {
		return prodcuts;
	}

	public void setProduts(Set<CardProduct> produts) {
		this.prodcuts = produts;
	}

	public Bank() {
    }

     public String getBankCode() {
        return bankCode;
    }

    public void setBankCode(String bankCode) {
        this.bankCode = bankCode;
    }

    public String getBankName() {
        return bankName;
    }

    public void setBankName(String bankName) {
        this.bankName = bankName;
    }

    public String getCurrencyCode() {
        return currencyCode;
    }

    public void setCurrencyCode(String currencyCode) {
        this.currencyCode = currencyCode;
    }

    public String getCountryCode() {
        return countryCode;
    }

    public void setCountryCode(String countryCode) {
        this.countryCode = countryCode;
    }

    public Date getBusinessDate() {
        return businessDate;
    }

    public void setBusinessDate(Date businessDate) {
        this.businessDate = businessDate;
    }

    

  

    public Set<RessourceParam> getRessources() {
		return Ressources;
	}

	public void setRessources(Set<RessourceParam> ressources) {
		Ressources = ressources;
	}

	
	public String getCategory() {
		return category;
	}

	public void setCategory(String category) {
		this.category = category;
	}

	@Override
    public String toString() {
        return "Bank{" +
                "bankCode=" + bankCode +
                ", bankName='" + bankName + '\'' +
                ", currencyCode='" + currencyCode + '\'' +
                ", countryCode='" + countryCode + '\'' +
                ", businessDate=" + businessDate +
               
                '}';
    }
}
