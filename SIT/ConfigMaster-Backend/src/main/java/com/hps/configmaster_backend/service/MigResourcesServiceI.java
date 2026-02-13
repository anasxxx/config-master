package com.hps.configmaster_backend.service;

import com.hps.configmaster_backend.entity.MigResources;

public interface MigResourcesServiceI {

	public MigResources addMigResources(MigResources ressource);
	public void deletMigResources(String ressourceId);

}
