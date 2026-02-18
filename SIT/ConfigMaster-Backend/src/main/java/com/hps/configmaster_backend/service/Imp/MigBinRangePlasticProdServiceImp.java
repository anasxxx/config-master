package com.hps.configmaster_backend.service.Imp;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.hps.configmaster_backend.dao.IMigBinRangePlasticProdRepositry;
import com.hps.configmaster_backend.entity.MigBinRangePlasticProd;
import com.hps.configmaster_backend.service.MigBinRangePlasticProdServiceI;

@Service
public class MigBinRangePlasticProdServiceImp implements MigBinRangePlasticProdServiceI  {

	
	
	@Autowired
	IMigBinRangePlasticProdRepositry 	migBinRangePlasticProdRepositry;


	@Override
	@Transactional
	public MigBinRangePlasticProd addMigBinRangePlasticProd(MigBinRangePlasticProd prod) {
	    return migBinRangePlasticProdRepositry.save(prod);
	}
	@Override

	public void deletMigBinRangePlasticProd(String productId)
	{
		 migBinRangePlasticProdRepositry.deleteById(productId);
	}


}
