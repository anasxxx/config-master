package com.hps.configmaster_backend.service.Imp;

import java.util.Collections;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.dao.ICountryRepository;
import com.hps.configmaster_backend.entity.Country;
import com.hps.configmaster_backend.service.ICountryService;
@Service
public class CountryServiceImp implements ICountryService {

	@Autowired
	ICountryRepository countryRepository;
	@Override
	public List<Country> getCountries() {

		 List<Country> countries = (List<Country>) countryRepository.getCountries();
		    return countries != null && !countries.isEmpty() ? countries : Collections.emptyList();
	}

	
	
}
