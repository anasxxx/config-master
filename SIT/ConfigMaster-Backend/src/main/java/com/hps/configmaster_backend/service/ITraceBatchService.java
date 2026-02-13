package com.hps.configmaster_backend.service;

import java.io.IOException;
import java.util.List;

import com.hps.configmaster_backend.models.TraceBatchModel;

public interface ITraceBatchService {

	
	
	public List<TraceBatchModel>  getTraceOfBatch(String campagne,String batch) throws IOException;
}
