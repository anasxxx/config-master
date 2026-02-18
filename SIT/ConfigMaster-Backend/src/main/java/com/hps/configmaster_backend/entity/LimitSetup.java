package com.hps.configmaster_backend.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.*;

@Entity
@Table(name = "P7_SA_LIMITS_SETUP")
public class LimitSetup {

    
    
    @EmbeddedId
    private LimitSetupId id;

    @Column(name = "WORDING")
    private String wording;

    // Daily
    @Column(name = "PER1_TYPE")
    private String dailyType;

    @Column(name = "ON_PER1_ONUS_AMNT")
    private String dailyDomAmnt;

    @Column(name = "ON_PER1_ONUS_NBR")
    private String dailyDomNbr;

    @Column(name = "ON_PER1_INTERNAT_AMNT")
    private String dailyIntAmnt;

    @Column(name = "ON_PER1_INTERNAT_NBR")
    private String dailyIntNbr;

    @Column(name = "ON_PER1_TOT_AMNT")
    private String dailyTotalAmnt;

    @Column(name = "ON_PER1_TOT_NBR")
    private String dailyTotalNbr;

    // Weekly
    @Column(name = "PER2_TYPE")
    private String weeklyType;

    @Column(name = "ON_PER2_ONUS_AMNT")
    private String weeklyDomAmnt;

    @Column(name = "ON_PER2_ONUS_NBR")
    private String weeklyDomNbr;

    @Column(name = "ON_PER2_INTERNAT_AMNT")
    private String weeklyIntAmnt;

    @Column(name = "ON_PER2_INTERNAT_NBR")
    private String weeklyIntNbr;

    @Column(name = "ON_PER2_TOT_AMNT")
    private String weeklyTotalAmnt;

    @Column(name = "ON_PER2_TOT_NBR")
    private String weeklyTotalNbr;

    // Monthly
    @Column(name = "PER3_TYPE")
    private String monthlyType;

    @Column(name = "ON_PER3_ONUS_AMNT")
    private String monthlyDomAmnt;

    @Column(name = "ON_PER3_ONUS_NBR")
    private String monthlyDomNbr;

    @Column(name = "ON_PER3_INTERNAT_AMNT")
    private String monthlyIntAmnt;

    @Column(name = "ON_PER3_INTERNAT_NBR")
    private String monthlyIntNbr;

    @Column(name = "ON_PER3_TOT_AMNT")
    private String monthlyTotalAmnt;

    @Column(name = "ON_PER3_TOT_NBR")
    private String monthlyTotalNbr;

    @ManyToOne
    @JoinColumns({
        @JoinColumn(name = "bank_code", referencedColumnName = "bank_code", insertable = false, updatable = false),
        @JoinColumn(name = "limit_index", referencedColumnName = "LIMITS_INDEXES", insertable = false, updatable = false)

    })
    private CardProduct cardProduct;
    

   
    @OneToOne
    @JoinColumns({
        @JoinColumn(name = "BANK_CODE", referencedColumnName = "BANK_CODE", insertable = false, updatable = false),
        @JoinColumn(name = "LIMIT_INDEX", referencedColumnName = "LIMIT_INDEX", insertable = false, updatable = false),
        @JoinColumn(name = "LIMITS_ID", referencedColumnName = "LIMITS_ID", insertable = false, updatable = false)

    })
    
    private SpecificTransactionLimit specificTransactionLimit;
    
    
	

	public SpecificTransactionLimit getSpecificTransactionLimit() {
		return specificTransactionLimit;
	}

	public void setSpecificTransactionLimit(SpecificTransactionLimit specificTransactionLimit) {
		this.specificTransactionLimit = specificTransactionLimit;
	}

	public LimitSetupId getId() {
		return id;
	}

	public void setId(LimitSetupId id) {
		this.id = id;
	}

	
   

    public String getWording() {
        return wording;
    }

    public void setWording(String wording) {
        this.wording = wording;
    }

    public String getDailyType() {
        return dailyType;
    }

    public void setDailyType(String dailyType) {
        this.dailyType = dailyType;
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

    public String getWeeklyType() {
        return weeklyType;
    }

    public void setWeeklyType(String weeklyType) {
        this.weeklyType = weeklyType;
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

    public String getMonthlyType() {
        return monthlyType;
    }

    public void setMonthlyType(String monthlyType) {
        this.monthlyType = monthlyType;
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
