package com.hps.configmaster_backend.dao;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import com.hps.configmaster_backend.entity.Bank;
import com.hps.configmaster_backend.entity.Country;
import com.hps.configmaster_backend.entity.Currency;

public interface ICountryRepository extends JpaRepository<Country, String> {

	 @Query("SELECT b FROM Country b")
	    public List<Country> getCountries();
}
