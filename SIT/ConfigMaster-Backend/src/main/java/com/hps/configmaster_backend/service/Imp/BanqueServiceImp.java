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
                    id.setBankCode(limit.getProductCode());
                    id.setLimitsId(limit.getLimitsId());

                    // Assigner l'ID composite à l'entité
                    lim.setId(id);

                    // Appel du service pour insérer
                    migLimitStandService.addMigLimitStand(lim);
               
                });
            });

            return 1;
        } catch (Exception e) {
            throw new RuntimeException("Erreur lors de l'ajout des données temporaires", e);
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
                    migLimitStandService.deletMigLimitStand(limit.getLimitsId()));
            }); 

            return 1;
        } catch (Exception e) {
            throw new RuntimeException("Erreur lors de la suppression des données temporaires", e);
        }
    }

    @Override
    @Transactional
    public Integer callPlSqlFunction(BankReq banqueM) {
        SimpleJdbcCall jdbcCall = new SimpleJdbcCall(jdbcTemplate)
            .withCatalogName("pcrd_st_board_conv_main")
            .withFunctionName("MAIN_BOARD_CONV_PARAM")
            .declareParameters(
                new SqlParameter("p_business_date", Types.DATE),
                new SqlParameter("p_bank_code", Types.VARCHAR),
                new SqlParameter("p_bank_wording", Types.VARCHAR),
                new SqlParameter("p_currency_code", Types.CHAR),
                new SqlParameter("p_country_code", Types.CHAR),
                new SqlParameter("p_action_flag", Types.CHAR)
            );

        Timestamp timestamp = banqueM.getpBusinessDate() != null ?
            new Timestamp(banqueM.getpBusinessDate().getTime()) : null;

        MapSqlParameterSource params = new MapSqlParameterSource()
            .addValue("p_business_date", timestamp)
            .addValue("p_bank_code", banqueM.getpBankCode())
            .addValue("p_bank_wording", banqueM.getpBankWording())
            .addValue("p_currency_code", banqueM.getpCurrencyCode())
            .addValue("p_country_code", banqueM.getpCountryCode())
            .addValue("p_action_flag", banqueM.getP_action_flag());

        Integer result = jdbcCall.executeFunction(Integer.class, params);
        return result != null ? result : -1;
    }
    @Override
    public Integer processBank(BankReq banqueM) {
        try {
        	Integer result=0;
            // 1. Insertion des données temporaires
            insertIntoTempTables(banqueM);

            // 2. Appel de la fonction PL/SQL
            Integer plsqlResult = callPlSqlFunction(banqueM);
            if (plsqlResult != 0) {
            	System.out.println(plsqlResult);
            	result=plsqlResult;
            	System.out.println(plsqlResult);

            }

            // 3. Suppression des données temporaires
            deletTempBank(banqueM);

            return result; // succès
        } catch (Exception e) {
            throw new RuntimeException("Échec du traitement complet de la banque : " + e.getMessage(), e);
        }
    }


    @Override
    public Integer deletBank(String codeBank) {
        Bank bank = getBank(codeBank);
        if (bank == null) return -1;

        SimpleJdbcCall jdbcCall = new SimpleJdbcCall(jdbcTemplate)
            .withCatalogName("pcrd_st_board_conv_main")
            .withFunctionName("MAIN_BOARD_CONV_PARAM")
            .declareParameters(
                new SqlParameter("p_business_date", Types.DATE),
                new SqlParameter("p_bank_code", Types.VARCHAR),
                new SqlParameter("p_bank_wording", Types.VARCHAR),
                new SqlParameter("p_currency_code", Types.CHAR),
                new SqlParameter("p_country_code", Types.CHAR),
                new SqlParameter("p_action_flag", Types.CHAR)
            );

        MapSqlParameterSource params = new MapSqlParameterSource()
            .addValue("p_business_date", bank.getBusinessDate())
            .addValue("p_bank_code", bank.getBankCode())
            .addValue("p_bank_wording", bank.getBankName())
            .addValue("p_currency_code", bank.getCurrencyCode())
            .addValue("p_country_code", bank.getCountryCode())
            .addValue("p_action_flag", 0);

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
