package com.hps.configmaster_backend.service.Imp;

import java.util.Collections;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.dao.ICurrencyRepository;
import com.hps.configmaster_backend.entity.Currency;
import com.hps.configmaster_backend.service.ICurrencyService;
@Service
public class CurrencyServiceImp implements ICurrencyService  {

	@Autowired
	private ICurrencyRepository currencyRepository;
	@Override
	public List<Currency> getCurrencies() {

		List<Currency> currencies = (List<Currency>) currencyRepository.getCurrencies();
	    return currencies != null && !currencies.isEmpty() ? currencies : Collections.emptyList();
	
	}
	
	

}
