package com.hps.configmaster_backend.service;

import com.hps.configmaster_backend.entity.MigServiceProd;

public interface MigServiceProdServiceI {
	public MigServiceProd addMigServiceProd (MigServiceProd service);
	public void deletMigServiceProd (String serviceId);

}
