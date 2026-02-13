package com.hps.configmaster_backend.service.Imp;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.dao.IMigResourcesRepositry;
import com.hps.configmaster_backend.entity.MigResources;
import com.hps.configmaster_backend.service.MigResourcesServiceI;
@Service
public class MigResourcesServiceImp implements MigResourcesServiceI  {

	
	@Autowired
	IMigResourcesRepositry migResourcesRepositry;
	@Override
	public MigResources addMigResources(MigResources ressource) {
		return migResourcesRepositry.save(ressource);
		
	}	
	
	@Override

	public void deletMigResources(String ressourceId)
 {
		
		migResourcesRepositry.deleteById(ressourceId);
	}

	
}
