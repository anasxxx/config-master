package com.hps.configmaster_backend.service;

import java.util.List;

import com.hps.configmaster_backend.models.BatchOfCampagneModule;

public interface IBatchOfCampagneService {

	public List<BatchOfCampagneModule> getUsecasOfCampaign(String campagne);

	
	
}
