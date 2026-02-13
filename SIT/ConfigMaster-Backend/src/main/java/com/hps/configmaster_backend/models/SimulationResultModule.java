package com.hps.configmaster_backend.models;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class SimulationResultModule {


	
	 private List<BatcheResultModule> batcheResultModule;
	    private List<RapportResultModule> failedReports;
	    
	    public SimulationResultModule()
	    {
	    	batcheResultModule=new ArrayList<BatcheResultModule>();
	    	failedReports=new ArrayList<RapportResultModule>();
	    }
	    
		public List<BatcheResultModule> getBatcheResultModule() {
			return batcheResultModule;
		}
		public void setBatcheResultModule(List<BatcheResultModule> batcheResultModule) {
			this.batcheResultModule = batcheResultModule;
		}
		public List<RapportResultModule> getFailedReports() {
			return failedReports;
		}
		public void setFailedReports(List<RapportResultModule> failedReports) {
			this.failedReports = failedReports;
		}

	    
	    
}
