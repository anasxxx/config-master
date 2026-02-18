package com.hps.configmaster_backend.models;



public class CurrencyModule {
	    private String currencyCode;
	    private String currencyAlpha;
	    private String currencyName;

	    // Constructeurs
	    

	    // Getters et Setters
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

	    // Optionnel : toString
	    @Override
	    public String toString() {
	        return "CurrencyM{" +
	                "currencyCode='" + currencyCode + '\'' +
	                ", currencyAlpha='" + currencyAlpha + '\'' +
	                ", currencyName='" + currencyName + '\'' +
	                '}';
	    }
	


}
