package com.hps.configmaster_backend.controller;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.hps.configmaster_backend.entity.Country;
import com.hps.configmaster_backend.entity.Currency;
import com.hps.configmaster_backend.entity.Resources;
import com.hps.configmaster_backend.models.CountryModule;
import com.hps.configmaster_backend.models.CurrencyModule;
import com.hps.configmaster_backend.models.ResourcesModule;
import com.hps.configmaster_backend.service.ICountryService;
import com.hps.configmaster_backend.service.ICurrencyService;
import com.hps.configmaster_backend.service.IResourcesSerivce;

@RestController
@RequestMapping("/v1/api/banksParam")

public class BankParametreController {
	@Autowired
	private ICountryService countryService;
	@Autowired
	private ICurrencyService currencyService;
	@Autowired
	private IResourcesSerivce resourcesSerivce;
	
	@GetMapping("/country")
    public ResponseEntity<?> getCountryCode() {
        try {
            List<Country> countries = countryService.getCountries();
            if (countries == null || countries.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NO_CONTENT).body("No countries found.");
            }
            List<CountryModule> currencyModels = countries.stream().map(currency -> {
            	CountryModule model = new CountryModule();
	            BeanUtils.copyProperties(currency, model);
	            return model;
	        }).collect(Collectors.toList());
            return ResponseEntity.ok(countries); // 200 OK
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("An error occurred while retrieving countries.");
        }
    }

	@GetMapping("/currency")
	public ResponseEntity<?> getCurrencyCode() {
	    try {
	        List<Currency> currencies = currencyService.getCurrencies();
	        if (currencies == null || currencies.isEmpty()) {
	            return ResponseEntity.status(HttpStatus.NO_CONTENT).body("No currencies found.");
	        }

	        // Mapper les entités vers les modèles (DTO)
	        List<CurrencyModule> currencyModels = currencies.stream().map(currency -> {
	        	CurrencyModule model = new CurrencyModule();
	            BeanUtils.copyProperties(currency, model);
	            return model;
	        }).collect(Collectors.toList());

	        return ResponseEntity.ok(currencyModels); // 200 OK avec la liste des modèles
	    } catch (Exception e) {
	        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
	                .body("An error occurred while retrieving currencies.");
	    }
	}

	@GetMapping("/Resources")
	public ResponseEntity<?> getResources() {
	    try {
	        List<Resources> resources = resourcesSerivce.getAllResources();
	        
	        if (resources == null || resources.isEmpty()) {
	            return ResponseEntity.status(HttpStatus.NO_CONTENT).body("No resources found.");
	        }
	        
	        List<ResourcesModule> resourceModels = resources.stream()
	            .map(res -> {
	                ResourcesModule model = new ResourcesModule();
	                BeanUtils.copyProperties(res, model);
	                return model;
	            })
	            .collect(Collectors.toList());
	            
	        return ResponseEntity.ok(resourceModels);
	    } catch (Exception e) {
	        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
	                .body("An error occurred while retrieving resources.");
	    }
	}

		
	}
	

