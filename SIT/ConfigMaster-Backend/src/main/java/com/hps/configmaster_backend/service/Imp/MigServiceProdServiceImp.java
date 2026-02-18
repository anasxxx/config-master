package com.hps.configmaster_backend.service.Imp;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.dao.IMigServiceProdRepositry;
import com.hps.configmaster_backend.entity.MigServiceProd;
import com.hps.configmaster_backend.service.MigServiceProdServiceI;

import jakarta.transaction.Transactional;
@Service
public class MigServiceProdServiceImp implements MigServiceProdServiceI {

	@Autowired
	IMigServiceProdRepositry   migServiceProdRepositry;
	@Transactional
	@Override
	public MigServiceProd addMigServiceProd(MigServiceProd service) {
		return migServiceProdRepositry.save(service);
	}

	
	@Override
	public void deletMigServiceProd (String serviceId)
 {
		migServiceProdRepositry.deleteById(serviceId);
	}
}
