package com.hps.configmaster_backend.models;


public class TransactionModel {
	private String transactionDate;
    private String issuingBank;
    private long totalTransaction;

    private String perApproved;
    private String perCancellationApproved;
    private String perCancellationRejected;
    private String perDeclinedFonc;
    private String perDeclinedTech;
	public String getTransactionDate() {
		return transactionDate;
	}
	public void setTransactionDate(String transactionDate) {
		this.transactionDate = transactionDate;
	}
	public String getIssuingBank() {
		return issuingBank;
	}
	public void setIssuingBank(String issuingBank) {
		this.issuingBank = issuingBank;
	}
	public long getTotalTransaction() {
		return totalTransaction;
	}
	public void setTotalTransaction(long totalTransaction) {
		this.totalTransaction = totalTransaction;
	}
	public String getPerApproved() {
		return perApproved;
	}
	public void setPerApproved(String perApproved) {
		this.perApproved = perApproved;
	}
	public String getPerCancellationApproved() {
		return perCancellationApproved;
	}
	public void setPerCancellationApproved(String perCancellationApproved) {
		this.perCancellationApproved = perCancellationApproved;
	}
	public String getPerCancellationRejected() {
		return perCancellationRejected;
	}
	public void setPerCancellationRejected(String perCancellationRejected) {
		this.perCancellationRejected = perCancellationRejected;
	}
	public String getPerDeclinedFonc() {
		return perDeclinedFonc;
	}
	public void setPerDeclinedFonc(String perDeclinedFonc) {
		this.perDeclinedFonc = perDeclinedFonc;
	}
	public String getPerDeclinedTech() {
		return perDeclinedTech;
	}
	public void setPerDeclinedTech(String perDeclinedTech) {
		this.perDeclinedTech = perDeclinedTech;
	}
    
    
}
