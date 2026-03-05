package com.hps.configmaster_backend.models;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import jakarta.validation.constraints.Pattern;

public class MigLimitStandModule {

    @NotNull(message = "Bank code cannot be null")
    @Size(max = 20, message = "Bank code cannot exceed 20 characters")
    private String bankCode;

    @NotNull(message = "Product code cannot be null")
    @Size(min = 4, max = 4, message = "Product code must be 4 characters")
    private String productCode;

    @NotNull(message = "Limits ID cannot be null")
    @Size(min = 1, max = 3, message = "Limits ID must be 1-3 characters")
    private String limitsId;

    // --- Period fields are NULLABLE: PL/SQL uses IS NULL checks to determine
    //     which period combination to apply (daily-only, weekly-only, monthly-only,
    //     weekly+monthly, daily+weekly+monthly, etc.)

    @Size(max = 20, message = "Daily domestic amount cannot exceed 20 characters")
    private String dailyDomAmnt;

    @Size(max = 3, message = "Daily domestic number must be max 3 characters")
    private String dailyDomNbr;

    @Size(max = 20, message = "Daily international amount cannot exceed 20 characters")
    private String dailyIntAmnt;

    @Size(max = 3, message = "Daily international number must be max 3 characters")
    private String dailyIntNbr;

    @Size(max = 20, message = "Daily total amount cannot exceed 20 characters")
    private String dailyTotalAmnt;

    @Size(max = 3, message = "Daily total number must be max 3 characters")
    private String dailyTotalNbr;

    @Size(max = 20, message = "Minimum amount per transaction cannot exceed 20 characters")
    private String minAmountPerTransaction;

    @Size(max = 20, message = "Maximum amount per transaction cannot exceed 20 characters")
    private String maxAmountPerTransaction;

    @Size(max = 20, message = "Weekly domestic amount cannot exceed 20 characters")
    private String weeklyDomAmnt;

    @Size(max = 3, message = "Weekly domestic number must be max 3 characters")
    private String weeklyDomNbr;

    @Size(max = 20, message = "Weekly international amount cannot exceed 20 characters")
    private String weeklyIntAmnt;

    @Size(max = 3, message = "Weekly international number must be max 3 characters")
    private String weeklyIntNbr;

    @Size(max = 20, message = "Weekly total amount cannot exceed 20 characters")
    private String weeklyTotalAmnt;

    @Size(max = 3, message = "Weekly total number must be max 3 characters")
    private String weeklyTotalNbr;

    @Size(max = 20, message = "Monthly domestic amount cannot exceed 20 characters")
    private String monthlyDomAmnt;

    @Size(max = 3, message = "Monthly domestic number must be max 3 characters")
    private String monthlyDomNbr;

    @Size(max = 20, message = "Monthly international amount cannot exceed 20 characters")
    private String monthlyIntAmnt;

    @Size(max = 3, message = "Monthly international number must be max 3 characters")
    private String monthlyIntNbr;

    @Size(max = 20, message = "Monthly total amount cannot exceed 20 characters")
    private String monthlyTotalAmnt;

    @Size(max = 3, message = "Monthly total number must be max 3 characters")
    private String monthlyTotalNbr;

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

    public String getLimitsId() {
        return limitsId;
    }

    public void setLimitsId(String limitsId) {
        this.limitsId = limitsId;
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
