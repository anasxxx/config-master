package com.hps.configmaster_backend.service;

import com.hps.configmaster_backend.entity.PreMigCardFees;

public interface PreMigCardFeesServiceI {
	
	public PreMigCardFees addPreMigCardFees(PreMigCardFees fees);
	public void deletPreMigCardFees(String  feesId);

}
