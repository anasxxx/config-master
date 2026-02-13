package com.hps.configmaster_backend.models;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import jakarta.validation.constraints.Pattern;
import java.util.Date;
import java.util.List;
import java.util.Set;

import com.fasterxml.jackson.annotation.JsonFormat;
public class BankRes {

	
	    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")

	    private Date pBusinessDate;         // Date de l'opération

	    @NotNull(message = "Le code de la banque est obligatoire")
	    @Size(min = 1, max = 10, message = "Le code de la banque doit avoir entre 1 et 10 caractères")
	    private String pBankCode;           // Code de la banque

	    @NotNull(message = "Le libellé de la banque est obligatoire")
	    @Size(min = 1, max = 100, message = "Le libellé de la banque doit avoir entre 1 et 100 caractères")
	    private String pBankWording;        // Libellé de la banque

	    @NotNull(message = "Le code de la devise est obligatoire")
	    @Size(min = 3, max = 3, message = "Le code de la devise doit être composé de 3 caractères")
	    private String pCurrencyCode;       // Code de la devise

	    @NotNull(message = "Le code du pays est obligatoire")
	    @Size(min = 2, max = 2, message = "Le code du pays doit être composé de 2 caractères")
	    private String pCountryCode;        // Code du pays

	    
	    private Set<CardProductRes> cardProducts;
	    private Set<BranchRes> branches;
	     private Set<MigResourcesModule> Ressources;
	    
	    // Getters et Setters
	    public Date getpBusinessDate() {
	        return pBusinessDate;
	    }

	    public void setpBusinessDate(Date pBusinessDate) {
	        this.pBusinessDate = pBusinessDate;
	    }

	    public String getpBankCode() {
	        return pBankCode;
	    }

	    public void setpBankCode(String pBankCode) {
	        this.pBankCode = pBankCode;
	    }

	    public String getpBankWording() {
	        return pBankWording;
	    }

	    public void setpBankWording(String pBankWording) {
	        this.pBankWording = pBankWording;
	    }

	    public String getpCurrencyCode() {
	        return pCurrencyCode;
	    }

	    public void setpCurrencyCode(String pCurrencyCode) {
	        this.pCurrencyCode = pCurrencyCode;
	    }

	    public String getpCountryCode() {
	        return pCountryCode;
	    }

	    public void setpCountryCode(String pCountryCode) {
	        this.pCountryCode = pCountryCode;
	    }


	  

	   

		
		public Set<MigResourcesModule> getRessources() {
			return Ressources;
		}

		public void setRessources(Set<MigResourcesModule> ressources) {
			Ressources = ressources;
		}

		public Set<CardProductRes> getCardProducts() {
			return cardProducts;
		}

		public void setCardProducts(Set<CardProductRes> cardProducts) {
			this.cardProducts = cardProducts;
		}

		public Set<BranchRes> getBranches() {
			return branches;
		}

		public void setBranches(Set<BranchRes> branches) {
			this.branches = branches;
		}

		
	    
	    
	}

	

