package com.hps.configmaster_backend.service;

import java.nio.file.Path;
import java.util.List;

import com.hps.configmaster_backend.models.SimulationResultModule;

import java.io.IOException;

public interface ISimulationResulService {

public 	SimulationResultModule parseLogFile(String campagne) throws IOException;

public byte[] downloadFileFromSftp(String campagne,String batchName);
	
	
	
	
	
	
}
