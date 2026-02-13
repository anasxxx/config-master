package com.hps.configmaster_backend.service.Imp;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.dao.IPreMigCardFeesRepositry;
import com.hps.configmaster_backend.entity.PreMigCardFees;
import com.hps.configmaster_backend.service.PreMigCardFeesServiceI;
@Service
public class PreMigCardFeesServiceImp implements PreMigCardFeesServiceI {

	@Autowired 
	IPreMigCardFeesRepositry preMigCardFeesRepositry;
	@Override
	public PreMigCardFees addPreMigCardFees(PreMigCardFees fees) {
		return preMigCardFeesRepositry.save(fees);
	}
	@Override

	public void deletPreMigCardFees(String  feesId)
 {
		preMigCardFeesRepositry.deleteById(feesId);
	}
}
