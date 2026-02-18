package com.hps.configmaster_backend.service;

import java.util.List;

import com.hps.configmaster_backend.models.CampagneModule;

public interface ICampagneService {
	
    public List<CampagneModule> getAllCampagne(String profile) ;

}
