package com.hps.configmaster_backend.models;

import java.util.ArrayList;
import java.util.List;

public class TraceBatchModel {

    private String batchName;
    private String batchStatus;
    private String batchProcessing;
    private String taskId;
    private String businessDate;
    private String systemDate;
    private List<String> shellReturnCodes = new ArrayList<>();
    private List<String> powerCardReturnCodes = new ArrayList<>();
    

    private List<String> cardholder_Processed = new ArrayList<>();
    private List<String> cardholder_Passed  = new ArrayList<>();
    private List<String> cardholder_Rejected  = new ArrayList<>();

    
    
    public String getBatchName() {
        return batchName;
    }

    public void setBatchName(String batchName) {
        this.batchName = batchName;
    }

    public String getBatchStatus() {
        return batchStatus;
    }

    public void setBatchStatus(String batchStatus) {
        this.batchStatus = batchStatus;
    }

    public String getBatchProcessing() {
        return batchProcessing;
    }

    public void setBatchProcessing(String batchProcessing) {
        this.batchProcessing = batchProcessing;
    }

    public String getTaskId() {
        return taskId;
    }

    public void setTaskId(String taskId) {
        this.taskId = taskId;
    }

    public String getBusinessDate() {
        return businessDate;
    }

    public void setBusinessDate(String businessDate) {
        this.businessDate = businessDate;
    }

    public String getSystemDate() {
        return systemDate;
    }

    public void setSystemDate(String systemDate) {
        this.systemDate = systemDate;
    }

    public List<String> getShellReturnCodes() {
        return shellReturnCodes;
    }

    public void setShellReturnCodes(List<String> shellReturnCodes) {
        this.shellReturnCodes = shellReturnCodes;
    }

    public List<String> getPowerCardReturnCodes() {
        return powerCardReturnCodes;
    }

    public void setPowerCardReturnCodes(List<String> powerCardReturnCodes) {
        this.powerCardReturnCodes = powerCardReturnCodes;
    }

	public List<String> getCardholder_Processed() {
		return cardholder_Processed;
	}

	public void setCardholder_Processed(List<String> cardholder_Processed) {
		this.cardholder_Processed = cardholder_Processed;
	}

	public List<String> getCardholder_Passed() {
		return cardholder_Passed;
	}

	public void setCardholder_Passed(List<String> cardholder_Passed) {
		this.cardholder_Passed = cardholder_Passed;
	}

	public List<String> getCardholder_Rejected() {
		return cardholder_Rejected;
	}

	public void setCardholder_Rejected(List<String> cardholder_Rejected) {
		this.cardholder_Rejected = cardholder_Rejected;
	}
    
    
    
    
}
