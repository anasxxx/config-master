package com.hps.configmaster_backend.service.Imp;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.dao.IResourcesRepository;
import com.hps.configmaster_backend.entity.Resources;
import com.hps.configmaster_backend.service.IResourcesSerivce;
@Service
public class ResourcesSerivceImp implements IResourcesSerivce {

	@Autowired
	IResourcesRepository resourcesRepository;

	@Override
	public List<Resources> getAllResources() {
		
		return resourcesRepository.findAll();
	}
	
	
}
