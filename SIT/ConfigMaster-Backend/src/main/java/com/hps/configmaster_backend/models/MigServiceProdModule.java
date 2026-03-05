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

    // Service flags: PL/SQL checks IS NOT NULL → null=disabled, "1"=enabled
    @Size(max = 1) private String retrait;
    @Size(max = 1) private String achat;
    @Size(max = 1) private String advance;
    @Size(max = 1) private String ecommerce;
    @Size(max = 1) private String transfert;
    @Size(max = 1) private String quasicash;
    @Size(max = 1) private String solde;
    @Size(max = 1) private String releve;
    @Size(max = 1) private String pinchange;
    @Size(max = 1) private String refund;
    @Size(max = 1) private String moneysend;
    @Size(max = 1) private String billpayment;
    @Size(max = 1) private String original;
    @Size(max = 1) private String authentication;
    @Size(max = 1) private String cashback;

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
