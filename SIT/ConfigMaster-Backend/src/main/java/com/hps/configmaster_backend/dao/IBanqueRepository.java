package com.hps.configmaster_backend.dao;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import com.hps.configmaster_backend.entity.Bank;

public interface IBanqueRepository extends JpaRepository<Bank, String> {

    @Query("SELECT b FROM Bank b WHERE b.bankCode = :codeBank")
    public Bank getBank(String codeBank);
    @Query("SELECT b.bankCode AS bankCode, b.currencyCode AS currencyCode, " +
            "b.countryCode AS countryCode, b.businessDate AS businessDate " +
            "FROM Bank b")
     List<Bank> findAllBankDetails();
    
}
