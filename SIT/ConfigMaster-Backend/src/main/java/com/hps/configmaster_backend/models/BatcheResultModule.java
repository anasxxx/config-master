package com.hps.configmaster_backend.models;

import java.util.Map;

public class BatcheResultModule {

	

	private String batchName;
	private String batchStatu;
	//private String BatchProcessing;
	//private String TaskId;
	//private String businessDate;                                                                   
    //private String systemDate; 
    //private Map<String,String>  ShellReturnCode;
    private Map<String,String>  PowerCARDReturnCode  ;
public String getBatchName() {
		return batchName;
	}
	public void setBatchName(String batchName) {
		this.batchName = batchName;
	}
	public String getBatchStatu() {
		return batchStatu;
	}
	public void setBatchStatu(String batchStatu) {
		this.batchStatu = batchStatu;
	}
/*	public String getBatchProcessing() {
		return BatchProcessing;
	}
	public void setBatchProcessing(String batchProcessing) {
		BatchProcessing = batchProcessing;
	}
	public String getTaskId() {
		return TaskId;
	}
	public void setTaskId(String taskId) {
		TaskId = taskId;
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
	public Map<String, String> getShellReturnCode() {
		return ShellReturnCode;
	}
	public void setShellReturnCode(Map<String, String> shellReturnCode) {
		ShellReturnCode = shellReturnCode;
	}
	public Map<String, String> getPowerCARDReturnCode() {
		return PowerCARDReturnCode;
	}
	public void setPowerCARDReturnCode(Map<String, String> powerCARDReturnCode) {
		PowerCARDReturnCode = powerCARDReturnCode;
	}
    
  */  
    
}
