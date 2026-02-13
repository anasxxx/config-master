package com.hps.configmaster_backend.models;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public class MigServiceProdModule {

    @NotNull(message = "Bank code cannot be null")
    @Size(max = 20, message = "Bank code cannot exceed 20 characters")
    private String bankCode;

    @NotNull(message = "Product code cannot be null")
    @Size(min = 3, max = 3, message = "Product code must be 3 characters")
    private String productCode;

    @NotNull(message = "Retrait cannot be null")
    @Size(min = 1, max = 1, message = "Retrait must be 1 character")
    private String retrait;

    @NotNull(message = "Achat cannot be null")
    @Size(min = 1, max = 1, message = "Achat must be 1 character")
    private String achat;

    @NotNull(message = "Advance cannot be null")
    @Size(min = 1, max = 1, message = "Advance must be 1 character")
    private String advance;

    @NotNull(message = "Ecommerce cannot be null")
    @Size(min = 1, max = 1, message = "Ecommerce must be 1 character")
    private String ecommerce;

    @NotNull(message = "Transfert cannot be null")
    @Size(min = 1, max = 1, message = "Transfert must be 1 character")
    private String transfert;

    @NotNull(message = "Quasicash cannot be null")
    @Size(min = 1, max = 1, message = "Quasicash must be 1 character")
    private String quasicash;

    @NotNull(message = "Solde cannot be null")
    @Size(min = 1, max = 1, message = "Solde must be 1 character")
    private String solde;

    @NotNull(message = "Releve cannot be null")
    @Size(min = 1, max = 1, message = "Releve must be 1 character")
    private String releve;

    @NotNull(message = "Pinchange cannot be null")
    @Size(min = 1, max = 1, message = "Pinchange must be 1 character")
    private String pinchange;

    @NotNull(message = "Refund cannot be null")
    @Size(min = 1, max = 1, message = "Refund must be 1 character")
    private String refund;

    @NotNull(message = "Moneysend cannot be null")
    @Size(min = 1, max = 1, message = "Moneysend must be 1 character")
    private String moneysend;

    @NotNull(message = "Billpayment cannot be null")
    @Size(min = 1, max = 1, message = "Billpayment must be 1 character")
    private String billpayment;

    @NotNull(message = "Original cannot be null")
    @Size(min = 1, max = 1, message = "Original must be 1 character")
    private String original;

    @NotNull(message = "Authentication cannot be null")
    @Size(min = 1, max = 1, message = "Authentication must be 1 character")
    private String authentication;

    @NotNull(message = "Cashback cannot be null")
    @Size(min = 1, max = 1, message = "Cashback must be 1 character")
    private String cashback;

    // Getters and Setters
    public String getBankCode() {
        return bankCode;
    }

    public void setBankCode(String bankCode) {
        this.bankCode = bankCode;
    }

    public String getProductCode() {
        return productCode;
    }

    public void setProductCode(String productCode) {
        this.productCode = productCode;
    }

    public String getRetrait() {
        return retrait;
    }

    public void setRetrait(String retrait) {
        this.retrait = retrait;
    }

    public String getAchat() {
        return achat;
    }

    public void setAchat(String achat) {
        this.achat = achat;
    }

    public String getAdvance() {
        return advance;
    }

    public void setAdvance(String advance) {
        this.advance = advance;
    }

    public String getEcommerce() {
        return ecommerce;
    }

    public void setEcommerce(String ecommerce) {
        this.ecommerce = ecommerce;
    }

    public String getTransfert() {
        return transfert;
    }

    public void setTransfert(String transfert) {
        this.transfert = transfert;
    }

    public String getQuasicash() {
        return quasicash;
    }

    public void setQuasicash(String quasicash) {
        this.quasicash = quasicash;
    }

    public String getSolde() {
        return solde;
    }

    public void setSolde(String solde) {
        this.solde = solde;
    }

    public String getReleve() {
        return releve;
    }

    public void setReleve(String releve) {
        this.releve = releve;
    }

    public String getPinchange() {
        return pinchange;
    }

    public void setPinchange(String pinchange) {
        this.pinchange = pinchange;
    }

    public String getRefund() {
        return refund;
    }

    public void setRefund(String refund) {
        this.refund = refund;
    }

    public String getMoneysend() {
        return moneysend;
    }

    public void setMoneysend(String moneysend) {
        this.moneysend = moneysend;
    }

    public String getBillpayment() {
        return billpayment;
    }

    public void setBillpayment(String billpayment) {
        this.billpayment = billpayment;
    }

    public String getOriginal() {
        return original;
    }

    public void setOriginal(String original) {
        this.original = original;
    }

    public String getAuthentication() {
        return authentication;
    }

    public void setAuthentication(String authentication) {
        this.authentication = authentication;
    }

    public String getCashback() {
        return cashback;
    }

    public void setCashback(String cashback) {
        this.cashback = cashback;
    }
}
