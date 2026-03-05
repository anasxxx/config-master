package com.hps.configmaster_backend.service;

import com.hps.configmaster_backend.entity.MigLimitStand;

public interface MigLimitStandServiceI {
	
	public MigLimitStand addMigLimitStand(MigLimitStand limit);
	public void deletMigLimitStand(String productCode, String limitId);
	


}
