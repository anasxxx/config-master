package com.hps.configmaster_backend.models;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import jakarta.validation.constraints.Pattern;
import java.util.Date;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonFormat;

public class BankReq {
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")

    private Date pBusinessDate;         // Date de l'opération

    @NotNull(message = "Le code de la banque est obligatoire")
    @Size(min = 1, max = 6, message = "Le code de la banque doit avoir entre 1 et 6 caractères (BANK.BANK_CODE=CHAR(6))")
    private String pBankCode;           // Code de la banque

    @NotNull(message = "Le libellé de la banque est obligatoire")
    @Size(min = 1, max = 40, message = "Le libellé de la banque doit avoir entre 1 et 40 caractères (BANK.BANK_NAME=VARCHAR2(40))")
    private String pBankWording;        // Libellé de la banque

    @NotNull(message = "Le code de la devise est obligatoire")
    @Size(min = 3, max = 3, message = "Le code de la devise doit être composé de 3 caractères")
    private String pCurrencyCode;       // Code de la devise

    @NotNull(message = "Le code du pays est obligatoire")
    @Size(min = 2, max = 3, message = "Le code du pays doit être composé de 2 ou 3 caractères")
    private String pCountryCode;        // Code du pays (alpha-2 e.g. MA or numeric e.g. 504)

    @NotNull(message = "Le flag pour première opération est obligatoire")
    private String p_action_flag;          // Flag pour première opération ('Y' ou 'N')
            // Flag pour ATM ('Y' ou 'N')

    
    private List<CardProductodule> cardProducts;
    private List<NewBranchModule> branches;
    private List<MigResourcesModule> ressources;
    
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


  

   

	public String getP_action_flag() {
		return p_action_flag;
	}

	public void setP_action_flag(String p_action_flag) {
		this.p_action_flag = p_action_flag;
	}

	public List<CardProductodule> getCardProducts() {
		return cardProducts;
	}

	public void setCardProducts(List<CardProductodule> cardProduct) {
		this.cardProducts = cardProduct;
	}

	public List<NewBranchModule> getBranches() {
		return branches;
	}

	public void setBranches(List<NewBranchModule> branches) {
		this.branches = branches;
	}

	public List<MigResourcesModule> getRessources() {
		return ressources;
	}

	public void setRessources(List<MigResourcesModule> ressources) {
		this.ressources = ressources;
	}

	@Override
	public String toString() {
		return "BankReq [pBusinessDate=" + pBusinessDate + ", pBankCode=" + pBankCode + ", pBankWording=" + pBankWording
				+ ", pCurrencyCode=" + pCurrencyCode + ", pCountryCode=" + pCountryCode + ", p_action_flag="
				+ p_action_flag + ", cardProduct=" + cardProducts + ", branches=" + branches + ", ressources="
				+ ressources + "]";
	}
    
    
}
