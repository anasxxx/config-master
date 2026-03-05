package com.hps.configmaster_backend.service.Imp;

import org.springframework.beans.factory.annotation.Autowired;

import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.dao.IMigLimitStandRepositry;
import com.hps.configmaster_backend.entity.MigLimitStand;
import com.hps.configmaster_backend.service.MigLimitStandServiceI;

import jakarta.transaction.Transactional;

@Service
public class MigLimitStandServiceImp  implements MigLimitStandServiceI {

	
	@Autowired
	IMigLimitStandRepositry migLimitStandRepositry;
	
	@Override
	public MigLimitStand addMigLimitStand(MigLimitStand limit) {
		return migLimitStandRepositry.save(limit);
	}
	
	

	@Override
	@Transactional
	
	public void deletMigLimitStand(String productCode, String limitId) {


		
	    migLimitStandRepositry.deleteByProductCodeAndLimitId(productCode, limitId);
	}


	
	

	

}
