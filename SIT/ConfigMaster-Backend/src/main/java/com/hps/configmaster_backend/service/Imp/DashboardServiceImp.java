package com.hps.configmaster_backend.service.Imp;

import java.sql.Date;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.dao.IDashboardRepository;
import com.hps.configmaster_backend.models.TransactionModel;
import com.hps.configmaster_backend.service.IDashboardervice;

@Service
public class DashboardServiceImp implements IDashboardervice {

	
	@Autowired
	private IDashboardRepository dashboardRepository;
	
	
    public List<Object[]> getTransactionStats(String date, String bankCode) {
        List<Object[]> results = dashboardRepository.getTransactionStats(date, bankCode);
       
        return results;
    }
}
	
	

