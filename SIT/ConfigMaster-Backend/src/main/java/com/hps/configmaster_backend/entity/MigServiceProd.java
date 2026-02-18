package com.hps.configmaster_backend.entity;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.Column;

 
@Entity
@Table(name = "st_pre_service_PROD")
public class MigServiceProd {

    @Column(name = "bank_code")
    private String bankCode;

    @Id
    @Column(name = "product_code")
    private String productCode;

    @Column(name = "retrait")
    private String retrait;

    @Column(name = "achat")
    private String achat;

    @Column(name = "advance")
    private String advance;

    @Column(name = "ecommerce")
    private String ecommerce;

    @Column(name = "transfert")
    private String transfert;

    @Column(name = "quasicash")
    private String quasicash;

    @Column(name = "solde")
    private String solde;

    @Column(name = "releve")
    private String releve;

    @Column(name = "pinchange")
    private String pinchange;

    @Column(name = "refund")
    private String refund;

    @Column(name = "moneysend")
    private String moneysend;

    @Column(name = "billpayment")
    private String billpayment;

    @Column(name = "original")
    private String original;

    @Column(name = "authentication")
    private String authentication;

    @Column(name = "cashback")
    private String cashback;

    // Getters et Setters

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
