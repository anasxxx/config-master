package com.hps.configmaster_backend.service;

import java.sql.Date;
import java.util.List;

import com.hps.configmaster_backend.models.TransactionModel;

public interface IDashboardervice {
    public List<Object[]> getTransactionStats(String date, String bankCode) ;


}
