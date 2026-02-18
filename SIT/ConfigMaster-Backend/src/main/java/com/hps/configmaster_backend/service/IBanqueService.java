package com.hps.configmaster_backend.service;

import java.util.Date;
import java.util.List;

import com.hps.configmaster_backend.entity.Bank;
import com.hps.configmaster_backend.entity.MigBinRangePlasticProd;
import com.hps.configmaster_backend.entity.MigLimitStand;
import com.hps.configmaster_backend.entity.MigResources;
import com.hps.configmaster_backend.entity.MigServiceProd;
import com.hps.configmaster_backend.entity.NewBranch;
import com.hps.configmaster_backend.entity.PreMigCardFees;
import com.hps.configmaster_backend.models.BankReq;

public interface IBanqueService {
	
	
	public Integer insertIntoTempTables(BankReq banqueM) ;
	public Integer deletBank(String codeBank);
	public int editBanque();
	public List<Bank> getBanques();
    public Integer callPlSqlFunction(BankReq banqueM) ;
    public Integer deletTempBank(BankReq banqueM);
    public Integer processBank(BankReq banqueM);
    public Bank getBank(String codeBank);

}
