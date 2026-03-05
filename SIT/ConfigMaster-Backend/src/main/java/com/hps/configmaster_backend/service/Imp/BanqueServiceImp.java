package com.hps.configmaster_backend.service.Imp;

import java.sql.Timestamp;
import java.sql.Types;
import java.util.Date;
import java.util.List;
import java.util.Map;
import java.util.Optional;

import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.SqlOutParameter;
import org.springframework.jdbc.core.SqlParameter;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.simple.SimpleJdbcCall;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.hps.configmaster_backend.dao.IBanqueRepository;
import com.hps.configmaster_backend.entity.*;
import com.hps.configmaster_backend.models.*;
import com.hps.configmaster_backend.service.*;

@Service
public class BanqueServiceImp implements IBanqueService {

    @Autowired private MigBinRangePlasticProdServiceI migBinRangePlasticProdService;
    @Autowired private MigLimitStandServiceI migLimitStandService;
    @Autowired private IBanqueRepository banqueRepository;
    @Autowired private MigResourcesServiceI migResourcesService;
    @Autowired private MigServiceProdServiceI migServiceProdService;
    @Autowired private NewBranchServiceI newBranchService;
    @Autowired private PreMigCardFeesServiceI preMigCardFeesService;
    @Autowired private JdbcTemplate jdbcTemplate;

    @Override
    @Transactional
    public Integer insertIntoTempTables(BankReq banqueM) {
        try {
            banqueM.getBranches().forEach(b -> {
                NewBranch branch = new NewBranch();
                BeanUtils.copyProperties(b, branch);
                newBranchService.addNewBranch(branch);
            });

            banqueM.getRessources().forEach(r -> {
                MigResources resource = new MigResources();
                BeanUtils.copyProperties(r, resource);
                migResourcesService.addMigResources(resource);
            });

            banqueM.getCardProducts().forEach(product -> {
                MigBinRangePlasticProd prod = new MigBinRangePlasticProd();
                PreMigCardFees fees = new PreMigCardFees();
                MigServiceProd service = new MigServiceProd();

                BeanUtils.copyProperties(product.getInfo(), prod);
                BeanUtils.copyProperties(product.getFees(), fees);
                BeanUtils.copyProperties(product.getServices(), service);

                migBinRangePlasticProdService.addMigBinRangePlasticProd(prod);
                preMigCardFeesService.addPreMigCardFees(fees);
                migServiceProdService.addMigServiceProd(service);

                product.getLimits().forEach(limit -> {
                    MigLimitStand lim = new MigLimitStand();
                    BeanUtils.copyProperties(limit, lim);

                    // Création de la clé composite
                    MigLimitStandId id = new MigLimitStandId();
                    id.setProductCode(limit.getProductCode());
                    id.setLimitsId(limit.getLimitsId());

                    // Assigner l'ID composite à l'entité
                    lim.setId(id);

                    // Appel du service pour insérer
                    migLimitStandService.addMigLimitStand(lim);
               
                });
            });

            return 1;
        } catch (Exception e) {
            System.out.println("=== INSERT TEMP TABLES ERROR ===");
            System.out.println("  Exception: " + e.getClass().getName() + " - " + e.getMessage());
            Throwable cause = e.getCause();
            while (cause != null) {
                System.out.println("  Caused by: " + cause.getClass().getName() + " - " + cause.getMessage());
                cause = cause.getCause();
            }
            e.printStackTrace();
            throw new RuntimeException("Erreur lors de l'ajout des données temporaires: " + e.getMessage(), e);
        }
    }

    @Override
    @Transactional
    public Integer deletTempBank(BankReq banqueM) {
        try {
            banqueM.getBranches().forEach(b -> 
                newBranchService.deletNewBranch(b.getBranchCode()));

            banqueM.getRessources().forEach(r -> 
                migResourcesService.deletMigResources(r.getResourceWording()));

            banqueM.getCardProducts().forEach(product -> {
                migBinRangePlasticProdService.deletMigBinRangePlasticProd(product.getInfo().getProductCode());
                preMigCardFeesService.deletPreMigCardFees(product.getFees().getCardFeesCode());
                migServiceProdService.deletMigServiceProd(product.getServices().getProductCode());

               product.getLimits().forEach(limit -> 
                        migLimitStandService.deletMigLimitStand(limit.getProductCode(), limit.getLimitsId()));
            }); 

            return 1;
        } catch (Exception e) {
            throw new RuntimeException("Erreur lors de la suppression des données temporaires", e);
        }
    }

    @Override
    @Transactional
    public Integer callPlSqlFunction(BankReq banqueM) {
        Timestamp timestamp = banqueM.getpBusinessDate() != null ?
            new Timestamp(banqueM.getpBusinessDate().getTime()) : null;

        // ── Resolve alpha currency code → numeric code ──────────────────
        String currencyCode = banqueM.getpCurrencyCode();
        if (currencyCode != null && currencyCode.matches("[A-Za-z]+")) {
            try {
                String numCode = jdbcTemplate.queryForObject(
                    "SELECT currency_code FROM currency_table WHERE TRIM(currency_code_alpha) = ?",
                    String.class, currencyCode.toUpperCase().trim());
                System.out.println("  Resolved currency " + currencyCode + " -> " + numCode);
                currencyCode = numCode.trim();
            } catch (Exception e) {
                System.out.println("  WARNING: Could not resolve currency alpha '" + currencyCode + "': " + e.getMessage());
            }
        }

        // ── Resolve alpha country code → numeric code ───────────────────
        String countryCode = banqueM.getpCountryCode();
        if (countryCode != null && countryCode.matches("[A-Za-z]+")) {
            String upperCode = countryCode.toUpperCase().trim();
            String numCode = null;

            // 1) Try exact match on iso_country_alpha (handles 3-char alpha like "MAR")
            try {
                numCode = jdbcTemplate.queryForObject(
                    "SELECT country_code FROM country WHERE TRIM(iso_country_alpha) = ?",
                    String.class, upperCode);
            } catch (Exception ignored) {}

            // 2) If 2-char alpha-2, convert to ISO alpha-3 using Java Locale, then look up
            if (numCode == null && upperCode.length() == 2) {
                try {
                    java.util.Locale loc = new java.util.Locale("", upperCode);
                    String alpha3 = loc.getISO3Country();   // "MA" → "MAR"
                    if (alpha3 != null && !alpha3.isEmpty()) {
                        numCode = jdbcTemplate.queryForObject(
                            "SELECT country_code FROM country WHERE TRIM(iso_country_alpha) = ?",
                            String.class, alpha3.toUpperCase());
                    }
                } catch (Exception ignored) {}
            }

            // 3) Fallback: search by wording
            if (numCode == null) {
                try {
                    numCode = jdbcTemplate.queryForObject(
                        "SELECT country_code FROM country WHERE LOWER(wording) LIKE ? AND ROWNUM = 1",
                        String.class, "%" + upperCode.toLowerCase() + "%");
                } catch (Exception ignored) {}
            }

            if (numCode != null) {
                System.out.println("  Resolved country " + countryCode + " -> " + numCode.trim());
                countryCode = numCode.trim();
            } else {
                System.out.println("  WARNING: Could not resolve country alpha '" + countryCode + "'");
            }
        }

        final String resolvedCurrency = currencyCode;
        final String resolvedCountry = countryCode;

        System.out.println("=== PL/SQL CALL DEBUG ===");
        System.out.println("  p_business_date = " + timestamp);
        System.out.println("  p_bank_code     = [" + banqueM.getpBankCode() + "]");
        System.out.println("  p_bank_wording  = [" + banqueM.getpBankWording() + "]");
        System.out.println("  p_currency_code = [" + resolvedCurrency + "]");
        System.out.println("  p_country_code  = [" + resolvedCountry + "]");
        System.out.println("  p_action_flag   = [" + banqueM.getP_action_flag() + "]");

        try {
            Integer result = jdbcTemplate.execute(
                (java.sql.Connection con) -> {
                    java.sql.CallableStatement cs = con.prepareCall(
                        "{ ? = call PCRD_ST_BOARD_CONV_MAIN.MAIN_BOARD_CONV_PARAM(?, ?, ?, ?, ?, ?) }");
                    cs.registerOutParameter(1, Types.INTEGER);
                    cs.setTimestamp(2, (Timestamp) null);  // will set below
                    cs.setString(3, null);
                    cs.setString(4, null);
                    cs.setString(5, null);
                    cs.setString(6, null);
                    cs.setString(7, null);
                    return cs;
                },
                (java.sql.CallableStatement cs) -> {
                    if (timestamp != null) cs.setTimestamp(2, timestamp);
                    cs.setString(3, banqueM.getpBankCode());
                    cs.setString(4, banqueM.getpBankWording());
                    cs.setString(5, resolvedCurrency);
                    cs.setString(6, resolvedCountry);
                    cs.setString(7, banqueM.getP_action_flag());
                    cs.execute();
                    int ret = cs.getInt(1);
                    System.out.println("  PL/SQL raw return = " + ret);
                    return ret;
                }
            );
            System.out.println("  PL/SQL final result = " + result);
            return result != null ? result : -1;
        } catch (Exception e) {
            System.out.println("  PL/SQL EXCEPTION: " + e.getClass().getName() + " - " + e.getMessage());
            Throwable cause = e.getCause();
            while (cause != null) {
                System.out.println("  CAUSED BY: " + cause.getClass().getName() + " - " + cause.getMessage());
                cause = cause.getCause();
            }
            throw new RuntimeException("PL/SQL call failed: " + e.getMessage(), e);
        }
    }
    @Override
    public Integer processBank(BankReq banqueM) {
        boolean insertDone = false;
        try {
        	Integer result=0;
            // 1. Insertion des données temporaires
            insertIntoTempTables(banqueM);
            insertDone = true;

            // 2. Appel de la fonction PL/SQL
            Integer plsqlResult = callPlSqlFunction(banqueM);
            if (plsqlResult != 0) {
            	System.out.println(plsqlResult);
            	result=plsqlResult;
            	System.out.println(plsqlResult);

            }

            // 3. Suppression des données temporaires
            deletTempBank(banqueM);
            insertDone = false; // cleanup done

            return result; // succès
        } catch (Exception e) {
            throw new RuntimeException("Échec du traitement complet de la banque : " + e.getMessage(), e);
        } finally {
            // Always clean up staging tables if insert was done
            if (insertDone) {
                try {
                    deletTempBank(banqueM);
                } catch (Exception cleanupEx) {
                    System.out.println("WARNING: Failed to cleanup staging tables: " + cleanupEx.getMessage());
                }
            }
        }
    }


    @Override
    public Integer deletBank(String codeBank) {
        Bank bank = getBank(codeBank);
        if (bank == null) return -1;

        SimpleJdbcCall jdbcCall = new SimpleJdbcCall(jdbcTemplate)
            .withCatalogName("pcrd_st_board_conv_main")
            .withFunctionName("MAIN_BOARD_CONV_PARAM")
            .withoutProcedureColumnMetaDataAccess()
            .declareParameters(
                new SqlOutParameter("RETURN_VALUE", Types.INTEGER),
                new SqlParameter("p_business_date", Types.TIMESTAMP),
                new SqlParameter("p_bank_code", Types.VARCHAR),
                new SqlParameter("p_bank_wording", Types.VARCHAR),
                new SqlParameter("p_currency_code", Types.VARCHAR),
                new SqlParameter("p_country_code", Types.VARCHAR),
                new SqlParameter("p_action_flag", Types.VARCHAR)
            );

        MapSqlParameterSource params = new MapSqlParameterSource()
            .addValue("p_business_date", bank.getBusinessDate())
            .addValue("p_bank_code", bank.getBankCode())
            .addValue("p_bank_wording", bank.getBankName())
            .addValue("p_currency_code", bank.getCurrencyCode())
            .addValue("p_country_code", bank.getCountryCode())
            .addValue("p_action_flag", "0");

        Integer result = jdbcCall.executeFunction(Integer.class, params);
        return result != null ? result : -1;
    }

    @Override
    public int editBanque() {
        return 0;
    }

    @Override
    public List<Bank> getBanques() {
        return banqueRepository.findAll();
    }

    @Override
    public Bank getBank(String codeBank) {
        return banqueRepository.findById(codeBank).orElse(null);
    }
}
