package com.hps.configmaster_backend.controller;

import com.hps.configmaster_backend.entity.*;
import com.hps.configmaster_backend.models.*;
import com.hps.configmaster_backend.service.IBanqueService;
import jakarta.validation.Valid;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.BindingResult;
import org.springframework.web.bind.annotation.*;

import org.springframework.jdbc.core.JdbcTemplate;
import java.util.*;
import java.util.stream.*;

@RestController
@RequestMapping("/v1/api/banks")
public class BankController {

    @Autowired
    private IBanqueService banqueService;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @PostMapping("/add")
    public ResponseEntity<?> addBank(@Valid @RequestBody BankReq banqueM, BindingResult bindingResult) {
        ResponseEntity<?> errorResponse = getValidationErrors(bindingResult);
        if (errorResponse != null) return errorResponse;
    	System.out.print("hello");

        try {
            Integer result = banqueService.processBank(banqueM);
        	System.out.print(result);
            if (result != 0) {
            	System.out.print(result);
				return buildError("Erreur lors du traitement de la banque (code=" + result + ")", HttpStatus.BAD_REQUEST);
            }

            return ResponseEntity.status(HttpStatus.CREATED).body(banqueM);
        } catch (Exception e) {
            return buildError(e.getMessage(), HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }

    @PostMapping("/edit")
    public ResponseEntity<?> editBank(@Valid @RequestBody BankReq banqueM, BindingResult bindingResult) {
    	 ResponseEntity<?> errorResponse = getValidationErrors(bindingResult);
         if (errorResponse != null) return errorResponse;

         try {
             Integer result = banqueService.processBank(banqueM);
             if (result != 0) {
				 return buildError("Erreur lors du traitement de la banque (code=" + result + ")", HttpStatus.BAD_REQUEST);
             }

             return ResponseEntity.status(HttpStatus.CREATED).body(banqueM);
         } catch (Exception e) {
             return buildError(e.getMessage(), HttpStatus.INTERNAL_SERVER_ERROR);
         }
     }

    @GetMapping("/getBank/{codeBank}")
    public ResponseEntity<?> getBankByCode(@PathVariable("codeBank") String codeBank) {
        Bank bank = banqueService.getBank(codeBank);
        if (bank == null) return buildError("Banque non trouvée", HttpStatus.NOT_FOUND);

        
        BankRes bankRes = mapBankToResponse(bank);
        return ResponseEntity.ok(bankRes);
    }

    @GetMapping("/getAll")
    public ResponseEntity<?> getBanks() {
        List<Bank> banques = banqueService.getBanques();
        if (banques == null || banques.isEmpty()) {
            return ResponseEntity.ok(Collections.emptyList());
        }

        List<BankRes> responses = new ArrayList<>();
        for (Bank bank : banques) {
        	
        	if(!"VB".equals(bank.getCategory()) && !"000001".equals(bank.getBankCode())) {
        	BankRes bankRes = new BankRes();
            bankRes.setpBankCode(bank.getBankCode());
            bankRes.setpBankWording(bank.getBankName());
            bankRes.setpBusinessDate(bank.getBusinessDate());
            bankRes.setpCountryCode(bank.getCountryCode());
            bankRes.setpCurrencyCode(bank.getCurrencyCode());
            
            responses.add(bankRes);
        }}

        return ResponseEntity.ok(responses);
    }

	// delete banque

    @DeleteMapping("/delete/{codeBank}")
    public ResponseEntity<String> deleteBank(@PathVariable String codeBank) {
        if (codeBank == null || codeBank.isEmpty()) {
            return new ResponseEntity<>("Code de banque invalide", HttpStatus.BAD_REQUEST);
        }

        try {
            // Appel à la méthode de suppression
            Integer isDeleted = banqueService.deletBank(codeBank);

            // Vérification du résultat de la suppression
            if (isDeleted == 0) {
                return ResponseEntity.ok("Banque supprimée avec succès"); // 200 OK avec message

            } else if (isDeleted == -2) {
                return new ResponseEntity<>("Erreur lors de la suppression de la banque", HttpStatus.INTERNAL_SERVER_ERROR);
            } else {
                return new ResponseEntity<>("Banque non trouvée", HttpStatus.NOT_FOUND);
            }
        } catch (Exception e) {
            return new ResponseEntity<>("Erreur interne du serveur", HttpStatus.INTERNAL_SERVER_ERROR);
        }
    }
    // Méthodes utilitaires

    private ResponseEntity<?> getValidationErrors(BindingResult result) {
        if (!result.hasErrors()) return null;

        Map<String, Object> errorMap = new HashMap<>();
        errorMap.put("message", "Veuillez vérifier les champs suivants");
        errorMap.put("status", HttpStatus.BAD_REQUEST.value());

        Map<String, String> fieldErrors = new HashMap<>();
        result.getFieldErrors().forEach(error -> fieldErrors.put(error.getField(), error.getDefaultMessage()));
        errorMap.put("errors", fieldErrors);

        return ResponseEntity.badRequest().body(errorMap);
    }

    private ResponseEntity<Object> buildError(String message, HttpStatus status) {
        Map<String, Object> error = new HashMap<>();
        error.put("message", message);
        error.put("status", status.value());
        return ResponseEntity.status(status).body(error);
    }

    private BankRes mapBankToResponse(Bank bank) {
    BankRes bankRes = new BankRes();
    bankRes.setpBankCode(bank.getBankCode());
    bankRes.setpBankWording(bank.getBankName());
    bankRes.setpBusinessDate(bank.getBusinessDate());
    bankRes.setpCountryCode(bank.getCountryCode());
    bankRes.setpCurrencyCode(bank.getCurrencyCode());

    // Branches
    Set<BranchRes> branchResList = bank.getBranches().stream()
        .map(this::mapBranch)
        .collect(Collectors.toSet());
    bankRes.setBranches(branchResList);
    // resource
    Set<MigResourcesModule> RessourceResList = bank.getRessources().stream()
            .map(this::mapResoource)
            .collect(Collectors.toSet());
        bankRes.setRessources(RessourceResList);

    // Products
    Set<CardProductRes> productResList = bank.getProdcuts().stream()
        .map(product -> mapCardProduct(product, bank.getBankCode()))
        .collect(Collectors.toSet());
    
    bankRes.setCardProducts(productResList);

    return bankRes;
   }

	private BranchRes mapBranch(Branch branch) {
	    BranchRes res = new BranchRes();
	    BeanUtils.copyProperties(branch, res);
	    return res;
	}

	private MigResourcesModule mapResoource(RessourceParam resource) {
		MigResourcesModule res=new MigResourcesModule();
		
		String codeRessiource =resource.getResource().getResource_code();
		switch (codeRessiource) {
        case "11" -> res.setResourceWording("VISA_BASE1");
        case "13" ->res.setResourceWording("VISA_SMS");
        case "03" -> res.setResourceWording("SID");
        case "02" -> res.setResourceWording("HOST_BANK");
        case "22" ->res.setResourceWording("MCD_MDS");
        case "40" -> res.setResourceWording("MCD_CIS");
        case "CS" -> res.setResourceWording("UPI");
        
    }
		
		
		res.setBankCode(resource.getBank().getBankCode());

	    return res;

	}
	private CardProductRes mapCardProduct(CardProduct product, String bankCode) {
	    CardProductRes productRes = new CardProductRes();
	    BeanUtils.copyProperties(product, productRes);
	    
	    String network = product.getNetwork();
	    if (network != null) {
	        switch (network.trim()) {
	            case "01":
	            	productRes.setNetwork("VISA");
	                break;
	            case "00":
	            	productRes.setNetwork("PRIVATIVE");
	                break;
	            case "21":
	            	productRes.setNetwork("GIMN");
	                break;
	            case "04":
	            	productRes.setNetwork("AMEX");
	                break;
	            case "02":
	            	productRes.setNetwork("MCRD");
	                break;
	            case "03":
	            	productRes.setNetwork("EUROPAY");
	                break;
	            case "07":
	            	productRes.setNetwork("TAG-YUP");
	                break;
	            case "05":
	            	productRes.setNetwork("DINERS");
	                break;
	            case "40":
	            	productRes.setNetwork("GMAC");
	                break;
	            case "09":
	            	productRes.setNetwork("TAG-CONNECT");
	                break;
	            default:
	                break;
	        }
	    }

	
	    if (product.getCardRange() != null) {
	        productRes.setBin(product.getCardRange().getBin());
	        productRes.setIndexPvk(product.getCardRange().getIndexPvk());
	        productRes.setTrancheMin(product.getCardRange().getTrancheMin());
	        productRes.setTrancheMax(product.getCardRange().getTrancheMax());
	    }
	
	    if (product.getCardFees() != null) {
	        FeesRes fees = new FeesRes();
	        BeanUtils.copyProperties(product.getCardFees(), fees);
	        productRes.setFees(fees);
	    }
	
	    MigServiceProdModule serviceModule = mapServices(product.getP7ServicesSetup());
	    serviceModule.setBankCode(bankCode);
	  serviceModule.setProductCode(product.getProductCode());

	    List<MigLimitStandModule> limitModules = mapLimits(product.getLimits(),bankCode, product.getProductCode());
	
	    productRes.setServices(serviceModule);
	   productRes.setLimits(limitModules);
	
	    return productRes;
	}
	
	private MigServiceProdModule mapServices(List<ServiceSetup> services) {
	    MigServiceProdModule module = new MigServiceProdModule();
	
	    for (ServiceSetup service : services) {
	        String wording = Optional.ofNullable(service.getWording()).orElse("").toUpperCase();
	
	        switch (wording) {
	            case "RETRAIT" -> module.setRetrait("X");
	            case "PAIEMENT" -> module.setAchat("X");
	            case "CASH ADVANCE" -> module.setAdvance("X");
	            case "BILL PAYMENT" -> module.setBillpayment("X");
	            case "E-COMMERCE" -> module.setEcommerce("X");
	            case "TRANSFER REQUEST" -> module.setTransfert("X");
	            case "QUASI CASH" -> module.setQuasicash("X");
	            case "SOLDE DEBIT" -> module.setSolde("X");
	            case "DEM.RELEVE DEBIT" -> module.setReleve("X");
	            case "PIN CHANGE" -> module.setPinchange("X");
	            case "REFUND" -> module.setRefund("X");
	            case "MONEY SEND" -> module.setMoneysend("X");
	            case "ORIGINAL CREDIT" -> module.setOriginal("X");
	            case "AUTHENTICATION REQUEST" -> module.setAuthentication("X");
	            case "CASH BACK" -> module.setCashback("X");
	        }
	    }
	
	    return module;
	}

	private List<MigLimitStandModule> mapLimits(List<LimitSetup> limits,String bankCode, String productCode) {
	    List<MigLimitStandModule> modules = new ArrayList<>();
	
	    for (LimitSetup limit : limits) {
	        MigLimitStandModule module = new MigLimitStandModule();
	        LimitSetupId id=limit.getId();
	        module.setBankCode(id.getBankCode());
	        System.out.println(id.getLimitIndex());
	        module.setProductCode(id.getLimitIndex());
	        String wording=limit.getWording();
	      /*  switch (wording) {
            case "RETRAIT" -> module.setLimitsId("1");     
            case "Cash advance" -> module.setLimitsId("3");
            case "ECOMMERCE" -> module.setLimitsId("9");
            case "QUASI CASH" -> module.setLimitsId("4");
            case "DEF LIMIT" -> module.setLimitsId("10");

        }*/
	        module.setLimitsId(limit.getId().getLimitId().toString());
	        
	        module.setMaxAmountPerTransaction(limit.getSpecificTransactionLimit().getMaxAmountPerTransaction());
	        module.setMinAmountPerTransaction(limit.getSpecificTransactionLimit().getMinAmountPerTransaction());
	        String type = limit.getDailyType(); // dailyType?
	        String weeklyType = limit.getWeeklyType();
	        String monthlyType = limit.getMonthlyType();
	
	        if ("D".equals(type)) {
	            mapDailyLimits(module, limit);
	        }
	        if ("W".equals(type)) {
	            mapWeeklyLimits(module, limit);
	        }
	        if ("M".equals(type)) {
	            mapMonthlyLimits(module, limit);
	        }
	
	        if ("D".equals(type) && "M".equals(weeklyType)) {
	            mapDailyLimits(module, limit);
	            mapMonthlyLimitsFromWeekly(module, limit);
	        }
	
	        if ("D".equals(type) && "W".equals(weeklyType)) {
	            mapDailyLimits(module, limit);
	            mapMonthlyLimitsFromWeekly(module, limit);
	        }
	
	        if ("W".equals(type) && "M".equals(weeklyType)) {
	            mapWeeklyLimits(module, limit);
	            mapMonthlyLimitsFromWeekly(module, limit);
	        }
	
	        modules.add(module);
	    }
	
	    return modules;
	}

	private void mapDailyLimits(MigLimitStandModule module, LimitSetup limit) {
	    module.setDailyDomAmnt(limit.getDailyDomAmnt());
	    module.setDailyDomNbr(limit.getDailyDomNbr());
	    module.setDailyIntAmnt(limit.getDailyIntAmnt());
	    module.setDailyIntNbr(limit.getDailyIntNbr());
	    module.setDailyTotalAmnt(limit.getDailyTotalAmnt());
	    module.setDailyTotalNbr(limit.getDailyTotalNbr());
	}

	private void mapWeeklyLimits(MigLimitStandModule module, LimitSetup limit) {
	    module.setWeeklyDomAmnt(limit.getDailyDomAmnt());
	    module.setWeeklyDomNbr(limit.getDailyDomNbr());
	    module.setWeeklyIntAmnt(limit.getDailyIntAmnt());
	    module.setWeeklyIntNbr(limit.getDailyIntNbr());
	    module.setWeeklyTotalAmnt(limit.getDailyTotalAmnt());
	    module.setWeeklyTotalNbr(limit.getDailyTotalNbr());
	}

	private void mapMonthlyLimits(MigLimitStandModule module, LimitSetup limit) {
	    module.setMonthlyDomAmnt(limit.getDailyDomAmnt());
	    module.setMonthlyDomNbr(limit.getDailyDomNbr());
	    module.setMonthlyIntAmnt(limit.getDailyIntAmnt());
	    module.setMonthlyIntNbr(limit.getDailyIntNbr());
	    module.setMonthlyTotalAmnt(limit.getDailyTotalAmnt());
	    module.setMonthlyTotalNbr(limit.getDailyTotalNbr());
	}

	private void mapMonthlyLimitsFromWeekly(MigLimitStandModule module, LimitSetup limit) {
	    module.setMonthlyDomAmnt(limit.getWeeklyDomAmnt());
	    module.setMonthlyDomNbr(limit.getWeeklyDomNbr());
	    module.setMonthlyIntAmnt(limit.getWeeklyIntAmnt());
	    module.setMonthlyIntNbr(limit.getWeeklyIntNbr());
	    module.setMonthlyTotalAmnt(limit.getWeeklyTotalAmnt());
	    module.setMonthlyTotalNbr(limit.getWeeklyTotalNbr());
	}

    @GetMapping("/diag")
    public ResponseEntity<?> diagnostics() {
        Map<String, Object> diag = new LinkedHashMap<>();

        // 1) Package status
        List<Map<String, Object>> pkgStatus = jdbcTemplate.queryForList(
            "SELECT object_name, object_type, status FROM user_objects " +
            "WHERE object_type IN ('PACKAGE','PACKAGE BODY') " +
            "AND object_name IN ('PCRD_ST_BOARD_CONV_MAIN','PCRD_ST_CONV_CLEAN'," +
            "'PCRD_ST_BOARD_CONV_COM','PCRD_ST_BOARD_CONV_ISS_PAR'," +
            "'PCRD_ST_CONV_CATALOGUE','GLOBAL_VARS','DECLARATION_CST','PCRD_GENERAL_TOOLS') " +
            "ORDER BY object_name, object_type");
        diag.put("packages", pkgStatus);

        // 2) Compilation errors
        List<Map<String, Object>> compErrors = jdbcTemplate.queryForList(
            "SELECT name, type, line, position, text FROM user_errors " +
            "WHERE name IN ('PCRD_ST_BOARD_CONV_MAIN','PCRD_ST_CONV_CLEAN'," +
            "'PCRD_ST_BOARD_CONV_COM','PCRD_ST_BOARD_CONV_ISS_PAR','PCRD_ST_CONV_CATALOGUE') " +
            "ORDER BY name, type, sequence");
        diag.put("compilationErrors", compErrors);

        // 3) Staging table counts
        Map<String, Integer> stagingCounts = new LinkedHashMap<>();
        String[] tables = {"st_pre_branch","st_pre_resources","st_pre_bin_range_plastic_prod",
                           "st_pre_mig_card_fees","st_pre_service_prod","st_pre_limit_stand"};
        for (String tbl : tables) {
            try {
                Integer cnt = jdbcTemplate.queryForObject("SELECT COUNT(*) FROM " + tbl, Integer.class);
                stagingCounts.put(tbl, cnt);
            } catch (Exception e) {
                stagingCounts.put(tbl, -1);
            }
        }
        diag.put("stagingCounts", stagingCounts);

        return ResponseEntity.ok(diag);
    }

    @PostMapping("/diag/recompile")
    public ResponseEntity<?> recompilePackages() {
        Map<String, Object> result = new LinkedHashMap<>();
        String[] packages = {
            "DECLARATION_CST", "GLOBAL_VARS", "PCRD_GENERAL_TOOLS",
            "PCRD_ST_CONV_CLEAN", "PCRD_ST_CONV_CATALOGUE",
            "PCRD_ST_BOARD_CONV_COM", "PCRD_ST_BOARD_CONV_ISS_PAR",
            "PCRD_ST_BOARD_CONV_MAIN"
        };
        List<Map<String, String>> recompileResults = new java.util.ArrayList<>();
        for (String pkg : packages) {
            Map<String, String> entry = new LinkedHashMap<>();
            entry.put("package", pkg);
            try {
                jdbcTemplate.execute("ALTER PACKAGE " + pkg + " COMPILE");
                entry.put("spec", "OK");
            } catch (Exception e) {
                entry.put("spec", "FAIL: " + e.getMessage());
            }
            try {
                jdbcTemplate.execute("ALTER PACKAGE " + pkg + " COMPILE BODY");
                entry.put("body", "OK");
            } catch (Exception e) {
                entry.put("body", "FAIL: " + e.getMessage());
            }
            recompileResults.add(entry);
        }
        result.put("recompile", recompileResults);

        // Check status after recompile
        List<Map<String, Object>> pkgStatus = jdbcTemplate.queryForList(
            "SELECT object_name, object_type, status FROM user_objects " +
            "WHERE object_type IN ('PACKAGE','PACKAGE BODY') " +
            "AND object_name IN ('PCRD_ST_BOARD_CONV_MAIN','PCRD_ST_CONV_CLEAN'," +
            "'PCRD_ST_BOARD_CONV_COM','PCRD_ST_BOARD_CONV_ISS_PAR'," +
            "'PCRD_ST_CONV_CATALOGUE','GLOBAL_VARS','DECLARATION_CST','PCRD_GENERAL_TOOLS') " +
            "ORDER BY object_name, object_type");
        result.put("packagesAfter", pkgStatus);

        // Check compilation errors after
        List<Map<String, Object>> compErrors = jdbcTemplate.queryForList(
            "SELECT name, type, line, position, text FROM user_errors " +
            "WHERE name IN ('PCRD_ST_BOARD_CONV_MAIN','PCRD_ST_CONV_CLEAN'," +
            "'PCRD_ST_BOARD_CONV_COM','PCRD_ST_BOARD_CONV_ISS_PAR','PCRD_ST_CONV_CATALOGUE') " +
            "ORDER BY name, type, sequence");
        result.put("errorsAfter", compErrors);

        return ResponseEntity.ok(result);
    }

    @PostMapping("/diag/clean-staging")
    public ResponseEntity<?> cleanStagingTables() {
        Map<String, Object> result = new LinkedHashMap<>();
        String[] tables = {"st_pre_branch","st_pre_resources","st_pre_bin_range_plastic_prod",
                           "st_pre_mig_card_fees","st_pre_service_prod","st_pre_limit_stand"};
        for (String tbl : tables) {
            try {
                int rows = jdbcTemplate.update("DELETE FROM " + tbl);
                result.put(tbl, "deleted " + rows + " rows");
            } catch (Exception e) {
                result.put(tbl, "FAIL: " + e.getMessage());
            }
        }
        return ResponseEntity.ok(result);
    }

    @GetMapping("/diag/plsql-source")
    public ResponseEntity<?> plsqlSource() {
        Map<String, Object> result = new LinkedHashMap<>();

        // Get MAIN function source
        List<Map<String, Object>> mainSrc = jdbcTemplate.queryForList(
            "SELECT line, text FROM user_source " +
            "WHERE name = 'PCRD_ST_BOARD_CONV_MAIN' AND type = 'PACKAGE BODY' " +
            "ORDER BY line");
        StringBuilder sb = new StringBuilder();
        for (Map<String, Object> row : mainSrc) {
            sb.append(row.get("TEXT"));
        }
        result.put("PCRD_ST_BOARD_CONV_MAIN_BODY", sb.toString());

        // Get COM body source
        List<Map<String, Object>> comSrc = jdbcTemplate.queryForList(
            "SELECT line, text FROM user_source " +
            "WHERE name = 'PCRD_ST_BOARD_CONV_COM' AND type = 'PACKAGE BODY' " +
            "ORDER BY line");
        StringBuilder sb2 = new StringBuilder();
        for (Map<String, Object> row : comSrc) {
            sb2.append(row.get("TEXT"));
        }
        result.put("PCRD_ST_BOARD_CONV_COM_BODY", sb2.toString());

        // Also get the DECLARATION_CST package spec for constant definitions
        List<Map<String, Object>> declSrc = jdbcTemplate.queryForList(
            "SELECT line, text FROM user_source " +
            "WHERE name = 'DECLARATION_CST' AND type = 'PACKAGE' " +
            "ORDER BY line");
        StringBuilder sb3 = new StringBuilder();
        for (Map<String, Object> row : declSrc) {
            sb3.append(row.get("TEXT"));
        }
        result.put("DECLARATION_CST_SPEC", sb3.toString());

        return ResponseEntity.ok(result);
    }

    @PostMapping("/diag/query")
    public ResponseEntity<?> diagQuery(@RequestBody Map<String, String> body) {
        String sql = body.get("sql");
        if (sql == null || sql.isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Missing 'sql' field"));
        }
        try {
            List<Map<String, Object>> rows = jdbcTemplate.queryForList(sql);
            return ResponseEntity.ok(Map.of("rows", rows, "count", rows.size()));
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/diag/execute")
    public ResponseEntity<?> diagExecute(@RequestBody Map<String, String> body) {
        String sql = body.get("sql");
        if (sql == null || sql.isBlank()) {
            return ResponseEntity.badRequest().body(Map.of("error", "Missing 'sql' field"));
        }
        try {
            jdbcTemplate.execute(sql);
            return ResponseEntity.ok(Map.of("result", "OK"));
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of("error", e.getMessage()));
        }
    }

}