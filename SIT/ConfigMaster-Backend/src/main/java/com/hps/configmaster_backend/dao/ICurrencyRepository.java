package com.hps.configmaster_backend.dao;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import com.hps.configmaster_backend.entity.Bank;
import com.hps.configmaster_backend.entity.Currency;

public interface ICurrencyRepository extends JpaRepository<Currency, String> {

	
	@Query("SELECT b FROM Currency b")
    public List<Currency> getCurrencies();
}
