package com.hps.configmaster_backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.EmbeddedId;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;



@Entity
@Table(name = "st_pre_limit_stand")
public class MigLimitStand {
    

    @Column(name = "BANK_CODE", nullable = false, length = 20)
    private String bankCode;
    
    
   
    @EmbeddedId
    private MigLimitStandId id;

    @Column(name = "DAILY_DOM_AMNT", nullable = true, length = 20)
    private String dailyDomAmnt;

    @Column(name = "DAILY_DOM_NBR", nullable = true, length = 3)
    private String dailyDomNbr;

    @Column(name = "DAILY_INT_AMNT", nullable = true, length = 20)
    private String dailyIntAmnt;

    @Column(name = "DAILY_INT_NBR", nullable = true, length = 3)
    private String dailyIntNbr;

    @Column(name = "DAILY_TOTAL_AMNT", nullable = true, length = 20)
    private String dailyTotalAmnt;

    @Column(name = "DAILY_TOTAL_NBR", nullable = true, length = 3)
    private String dailyTotalNbr;

    @Column(name = "MIN_AMOUNT_PER_TRANSACTION", nullable = true, length = 20)
    private String minAmountPerTransaction;

    @Column(name = "MAX_AMOUNT_PER_TRANSACTION", nullable = true, length = 20)
    private String maxAmountPerTransaction;

    @Column(name = "WEEKLY_DOM_AMNT", nullable = true, length = 20)
    private String weeklyDomAmnt;

    @Column(name = "WEEKLY_DOM_NBR", nullable = true, length = 3)
    private String weeklyDomNbr;

    @Column(name = "WEEKLY_INT_AMNT", nullable = true, length = 20)
    private String weeklyIntAmnt;

    @Column(name = "WEEKLY_INT_NBR", nullable = true, length = 3)
    private String weeklyIntNbr;

    @Column(name = "WEEKLY_TOTAL_AMNT", nullable = true, length = 20)
    private String weeklyTotalAmnt;

    @Column(name = "WEEKLY_TOTAL_NBR", nullable = true, length = 3)
    private String weeklyTotalNbr;

    @Column(name = "MONTHLY_DOM_AMNT", nullable = true, length = 20)
    private String monthlyDomAmnt;

    @Column(name = "MONTHLY_DOM_NBR", nullable = true, length = 3)
    private String monthlyDomNbr;

    @Column(name = "MONTHLY_INT_AMNT", nullable = true, length = 20)
    private String monthlyIntAmnt;

    @Column(name = "MONTHLY_INT_NBR", nullable = true, length = 3)
    private String monthlyIntNbr;

    @Column(name = "MONTHLY_TOTAL_AMNT", nullable = true, length = 20)
    private String monthlyTotalAmnt;

    @Column(name = "MONTHLY_TOTAL_NBR", nullable = true, length = 3)
    private String monthlyTotalNbr;

    // Getters and Setters

    public String getBankCode() {
        return bankCode;
    }

    public void setBankCode(String bankCode) {
        this.bankCode = bankCode;
    }

   

   

    public MigLimitStandId getId() {
		return id;
	}

	public void setId(MigLimitStandId id) {
		this.id = id;
	}

	public String getDailyDomAmnt() {
        return dailyDomAmnt;
    }

    public void setDailyDomAmnt(String dailyDomAmnt) {
        this.dailyDomAmnt = dailyDomAmnt;
    }

    public String getDailyDomNbr() {
        return dailyDomNbr;
    }

    public void setDailyDomNbr(String dailyDomNbr) {
        this.dailyDomNbr = dailyDomNbr;
    }

    public String getDailyIntAmnt() {
        return dailyIntAmnt;
    }

    public void setDailyIntAmnt(String dailyIntAmnt) {
        this.dailyIntAmnt = dailyIntAmnt;
    }

    public String getDailyIntNbr() {
        return dailyIntNbr;
    }

    public void setDailyIntNbr(String dailyIntNbr) {
        this.dailyIntNbr = dailyIntNbr;
    }

    public String getDailyTotalAmnt() {
        return dailyTotalAmnt;
    }

    public void setDailyTotalAmnt(String dailyTotalAmnt) {
        this.dailyTotalAmnt = dailyTotalAmnt;
    }

    public String getDailyTotalNbr() {
        return dailyTotalNbr;
    }

    public void setDailyTotalNbr(String dailyTotalNbr) {
        this.dailyTotalNbr = dailyTotalNbr;
    }

    public String getMinAmountPerTransaction() {
        return minAmountPerTransaction;
    }

    public void setMinAmountPerTransaction(String minAmountPerTransaction) {
        this.minAmountPerTransaction = minAmountPerTransaction;
    }

    public String getMaxAmountPerTransaction() {
        return maxAmountPerTransaction;
    }

    public void setMaxAmountPerTransaction(String maxAmountPerTransaction) {
        this.maxAmountPerTransaction = maxAmountPerTransaction;
    }

    public String getWeeklyDomAmnt() {
        return weeklyDomAmnt;
    }

    public void setWeeklyDomAmnt(String weeklyDomAmnt) {
        this.weeklyDomAmnt = weeklyDomAmnt;
    }

    public String getWeeklyDomNbr() {
        return weeklyDomNbr;
    }

    public void setWeeklyDomNbr(String weeklyDomNbr) {
        this.weeklyDomNbr = weeklyDomNbr;
    }

    public String getWeeklyIntAmnt() {
        return weeklyIntAmnt;
    }

    public void setWeeklyIntAmnt(String weeklyIntAmnt) {
        this.weeklyIntAmnt = weeklyIntAmnt;
    }

    public String getWeeklyIntNbr() {
        return weeklyIntNbr;
    }

    public void setWeeklyIntNbr(String weeklyIntNbr) {
        this.weeklyIntNbr = weeklyIntNbr;
    }

    public String getWeeklyTotalAmnt() {
        return weeklyTotalAmnt;
    }

    public void setWeeklyTotalAmnt(String weeklyTotalAmnt) {
        this.weeklyTotalAmnt = weeklyTotalAmnt;
    }

    public String getWeeklyTotalNbr() {
        return weeklyTotalNbr;
    }

    public void setWeeklyTotalNbr(String weeklyTotalNbr) {
        this.weeklyTotalNbr = weeklyTotalNbr;
    }

    public String getMonthlyDomAmnt() {
        return monthlyDomAmnt;
    }

    public void setMonthlyDomAmnt(String monthlyDomAmnt) {
        this.monthlyDomAmnt = monthlyDomAmnt;
    }

    public String getMonthlyDomNbr() {
        return monthlyDomNbr;
    }

    public void setMonthlyDomNbr(String monthlyDomNbr) {
        this.monthlyDomNbr = monthlyDomNbr;
    }

    public String getMonthlyIntAmnt() {
        return monthlyIntAmnt;
    }

    public void setMonthlyIntAmnt(String monthlyIntAmnt) {
        this.monthlyIntAmnt = monthlyIntAmnt;
    }

    public String getMonthlyIntNbr() {
        return monthlyIntNbr;
    }

    public void setMonthlyIntNbr(String monthlyIntNbr) {
        this.monthlyIntNbr = monthlyIntNbr;
    }

    public String getMonthlyTotalAmnt() {
        return monthlyTotalAmnt;
    }

    public void setMonthlyTotalAmnt(String monthlyTotalAmnt) {
        this.monthlyTotalAmnt = monthlyTotalAmnt;
    }

    public String getMonthlyTotalNbr() {
        return monthlyTotalNbr;
    }

    public void setMonthlyTotalNbr(String monthlyTotalNbr) {
        this.monthlyTotalNbr = monthlyTotalNbr;
    }
}