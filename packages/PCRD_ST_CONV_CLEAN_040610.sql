
  CREATE OR REPLACE EDITIONABLE PACKAGE "POWERCARD"."PCRD_ST_CONV_CLEAN" 
IS
    V_ENV_INFO_TRACE   GLOBAL_VARS.ENV_INFO_TRACE_TYPE;

    FUNCTION AUT_CONV_DATA_ROLLBACK (p_bank_code                            IN                  BANK.bank_code%TYPE ,
                                    p_bank_wording               IN                     BANK.bank_name%TYPE)
                                RETURN PLS_INTEGER;
                                
    FUNCTION AUT_CONV_FINALPARAM_ROLLBACK (p_bank_code                            IN                  BANK.bank_code%TYPE,
                                      p_bank_wording               IN                     BANK.bank_name%TYPE,
                                     p_country_code              IN                  country.country_code%TYPE
                                                    )
        RETURN PLS_INTEGER;

    FUNCTION AUT_CONV_GLB_TEMP_ROLLBACK (p_bank_code                            IN                  BANK.bank_code%TYPE,
                                      p_bank_wording               IN                     BANK.bank_name%TYPE,
                                     p_country_code              IN                  country.country_code%TYPE
                                                    )
        RETURN PLS_INTEGER;


    FUNCTION AUT_CONV_PRODUCT_TEMP_ROLLBACK (p_bank_code                            IN                  BANK.bank_code%TYPE,
                                      p_bank_wording               IN                     BANK.bank_name%TYPE,
                                     p_country_code              IN                  country.country_code%TYPE
                                                    )
        RETURN PLS_INTEGER;




    FUNCTION MAIN_AUT_CLEAN (p_bank_code                            IN                  BANK.bank_code%TYPE,
                                      p_bank_wording               IN                     BANK.bank_name%TYPE,
                                     p_country_code              IN                  country.country_code%TYPE
                                                    )
        RETURN PLS_INTEGER;


    FUNCTION BANK_PARAM_CLEAN (p_bank_code                            IN                  BANK.bank_code%TYPE,
                                p_bank_wording               IN                     BANK.bank_name%TYPE,
                                     p_country_code              IN                  country.country_code%TYPE
                                                    )
        RETURN PLS_INTEGER;
END PCRD_ST_CONV_CLEAN;
/

CREATE OR REPLACE EDITIONABLE PACKAGE BODY "POWERCARD"."PCRD_ST_CONV_CLEAN" 
IS
    FUNCTION MAIN_AUT_CLEAN (p_bank_code   IN   BANK.bank_code%TYPE,
                              p_bank_wording               IN                     BANK.bank_name%TYPE,
                              p_country_code                 IN                 COUNTRY.country_code%TYPE)
 RETURN PLS_INTEGER
    IS
        RETURN_STATUS   PLS_INTEGER;
    BEGIN
        --DEFINE TRACES RECORD
        V_ENV_INFO_TRACE.USER_NAME       := 'AUTOMATISATION';
        V_ENV_INFO_TRACE.MODULE_CODE     := 'AUT';
        V_ENV_INFO_TRACE.LANG            := 'E';
        V_ENV_INFO_TRACE.FUNCTION_NAME   := 'MAIN_AUT_CLEAN';
        V_ENV_INFO_TRACE.PACKAGE_NAME    := SUBSTR($$PLSQL_UNIT,1,30);

        V_ENV_INFO_TRACE.USER_MESSAGE    := 'START ';
        PCRD_GENERAL_TOOLS.PUT_TRACES (V_ENV_INFO_TRACE, $$PLSQL_LINE);





        RETURN_STATUS                    := PCRD_ST_CONV_CLEAN.AUT_CONV_DATA_ROLLBACK(P_BANK_CODE,
                                                                                    p_bank_wording    );

        IF RETURN_STATUS <> DECLARATION_CST.OK
        THEN
            V_ENV_INFO_TRACE.USER_MESSAGE   := 'ERROR WHILE CALLING PCRD_ST_CONV_CLEAN.AUT_CONV_DATA_ROLLBACK';
            PCRD_GENERAL_TOOLS.PUT_TRACES (V_ENV_INFO_TRACE, $$PLSQL_LINE);
            RETURN RETURN_STATUS;
        END IF;



        RETURN_STATUS                    := PCRD_ST_CONV_CLEAN.AUT_CONV_FINALPARAM_ROLLBACK(P_BANK_CODE,
                                                                                    p_bank_wording,
                                                                                    p_country_code);

        IF RETURN_STATUS <> DECLARATION_CST.OK
        THEN
            V_ENV_INFO_TRACE.USER_MESSAGE   := 'ERROR WHILE CALLING PCRD_ST_CONV_CLEAN.AUT_CONV_FINALPARAM_ROLLBACK';
            PCRD_GENERAL_TOOLS.PUT_TRACES (V_ENV_INFO_TRACE, $$PLSQL_LINE);
            RETURN RETURN_STATUS;
        END IF;



        RETURN_STATUS                    := PCRD_ST_CONV_CLEAN.AUT_CONV_GLB_TEMP_ROLLBACK(P_BANK_CODE,
                                                                                    p_bank_wording,
                                                                                    p_country_code     );

        IF RETURN_STATUS <> DECLARATION_CST.OK
        THEN
            V_ENV_INFO_TRACE.USER_MESSAGE   := 'ERROR WHILE CALLING PCRD_ST_CONV_CLEAN.AUT_CONV_GLB_TEMP_ROLLBACK';
            PCRD_GENERAL_TOOLS.PUT_TRACES (V_ENV_INFO_TRACE, $$PLSQL_LINE);
            RETURN RETURN_STATUS;
        END IF;


        RETURN_STATUS                    := PCRD_ST_CONV_CLEAN.AUT_CONV_PRODUCT_TEMP_ROLLBACK(P_BANK_CODE,
                                                                                    p_bank_wording,
                                                                                    p_country_code     );

        IF RETURN_STATUS <> DECLARATION_CST.OK
        THEN
            V_ENV_INFO_TRACE.USER_MESSAGE   := 'ERROR WHILE CALLING PCRD_ST_CONV_CLEAN.AUT_CONV_PRODUCT_TEMP_ROLLBACK';
            PCRD_GENERAL_TOOLS.PUT_TRACES (V_ENV_INFO_TRACE, $$PLSQL_LINE);
            RETURN RETURN_STATUS;
        END IF;






        RETURN DECLARATION_CST.OK;



    EXCEPTION WHEN OTHERS
    THEN
    v_env_info_trace.user_message   :=  NULL;
    PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
    RETURN (declaration_cst.ERROR);

    END MAIN_AUT_CLEAN;

    FUNCTION BANK_PARAM_CLEAN (   p_bank_code               IN                  BANK.bank_code%TYPE,
                                    p_bank_wording               IN                     BANK.bank_name%TYPE,
                                    p_country_code                IN                  COUNTRY.country_code%TYPE)

        RETURN PLS_INTEGER
    IS
    BEGIN


            EXECUTE IMMEDIATE ' DELETE           PCARD_TASKS_EXEC_GROUP_BANK         WHERE        bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             BANK_ADDENDUM                   WHERE        bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           BANK                       WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           CENTER                         WHERE         center_name =:1'     USING p_bank_wording  ;
            EXECUTE IMMEDIATE ' DELETE             CITY        WHERE        country_code  = :1'             USING  p_country_code ;
            EXECUTE IMMEDIATE ' DELETE          Region         WHERE        country_code  = :1'             USING  p_country_code ;

        RETURN DECLARATION_CST.OK;
    END BANK_PARAM_CLEAN;


    FUNCTION AUT_CONV_DATA_ROLLBACK (   p_bank_code               IN                  BANK.bank_code%TYPE,
                                        p_bank_wording               IN                     BANK.bank_name%TYPE)

        RETURN PLS_INTEGER
    IS
    BEGIN
            EXECUTE IMMEDIATE ' DELETE st_temp_resources  ';
            EXECUTE IMMEDIATE ' INSERT INTO st_temp_resources  SELECT * FROM resources WHERE wording = :1' USING p_bank_wording;

            EXECUTE IMMEDIATE ' DELETE           user_passwords          where login in (select user_code from users where  institution_fk = :1)'       USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           users                WHERE        institution_fk = :1'      USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           profile             WHERE        institution_fk = :1'      USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           SUSPEND_NETWORK_INC_TRX             WHERE        issuer_bank_code = :1'      USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           TERMINAL_ATM_WATCH_ACTIVITY         WHERE        bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           VISA_FRAUD_REPORTING                 WHERE        acquirer_reference_number IN (SELECT microfilm_ref_number FROM transaction_hist    WHERE issuer_bank_code = :1)'          USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             TRANS_HIST_LIMIT_USE_DATA            WHERE        microfilm_ref_number IN (SELECT  microfilm_ref_number FROM   TRANSACTION_HIST   WHERE issuer_bank_code = :1)'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             TRANSACTION_HIST_ADD_CHIP              WHERE        microfilm_ref_number IN (SELECT  microfilm_ref_number FROM   TRANSACTION_HIST   WHERE issuer_bank_code = :1)'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             TRANSACTION_HIST_ADD_FRAUD             WHERE        microfilm_ref_number IN (SELECT  microfilm_ref_number FROM   TRANSACTION_HIST   WHERE issuer_bank_code = :1)'           USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             TRANSACTION_HIST_ADD_TCR01             WHERE        microfilm_ref_number IN (SELECT  microfilm_ref_number FROM   TRANSACTION_HIST   WHERE issuer_bank_code = :1)'            USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             TRANSACTION_HIST_TO_ARCHIVE            WHERE        microfilm_ref_number IN (SELECT  microfilm_ref_number FROM   TRANSACTION_HIST   WHERE issuer_bank_code = :1)'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           TRANSACTION_HIST                    WHERE        issuer_bank_code = :1'      USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           TRANSACTION_HIST_MVT                WHERE        issuer_bank_code = :1'      USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           TRANSACTION_HIST_CARD               WHERE        issuer_bank_code = :1'      USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             TRANSACTION_HIST_ADD_CHIP            WHERE        microfilm_ref_number IN (SELECT  microfilm_ref_number FROM   TRANSACTION_HIST   WHERE issuer_bank_code = :1)'       USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             TRANSACTION_HIST_ADD_FRAUD           WHERE        microfilm_ref_number IN (SELECT  microfilm_ref_number FROM   TRANSACTION_HIST   WHERE issuer_bank_code = :1)'        USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             TRANSACTION_HIST_ADD_TCR01          WHERE        microfilm_ref_number IN (SELECT  microfilm_ref_number FROM   TRANSACTION_HIST   WHERE issuer_bank_code = :1)'         USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             TRANSACTION_HIST_TO_ARCHIVE         WHERE        microfilm_ref_number IN (SELECT  microfilm_ref_number FROM   TRANSACTION_HIST   WHERE issuer_bank_code = :1)'        USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             PCARD_USER_BLOCKED                   WHERE        bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             RESOURCE_ACTIVITY_HIST               WHERE         resource_id in (SELECT resource_id FROM st_temp_resources )';
            EXECUTE IMMEDIATE ' DELETE             RESOURCE_ACTIVITY_SET                WHERE         resource_id in (SELECT resource_id FROM st_temp_resources )';
            EXECUTE IMMEDIATE ' DELETE             RESOURCE_EVENT_LOG                   WHERE         resource_id in (SELECT resource_id FROM st_temp_resources )';
            EXECUTE IMMEDIATE ' DELETE             SWITCH_MSG_FLOW_INFO                WHERE         src_resource_id in (SELECT resource_id FROM st_temp_resources )';
            EXECUTE IMMEDIATE ' DELETE             SWITCH_MSG_FLOW_INFO                WHERE         dst_resource_id in (SELECT resource_id FROM st_temp_resources )';
            EXECUTE IMMEDIATE ' DELETE           TRANS_MV_LINKUP                       WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           TRANS_MV_BATCH                         WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             TEMP_SMS_EMAIL_OPERATION_LOG        WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE          CARD_ACTIVITY                          WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE          CARD_ACTIVITY_ADDENDUM                 WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE          POTENTIAL_CHARGEBACK                   WHERE         issuer_bank_code = :1'      USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE          SMS_STAGING_TABLE                      WHERE          bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE          TERMINAL_ATM_SETTLEMENT                WHERE         bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             TERMINAL_ATM_CLOSURE                WHERE         bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             TERMINAL_ATM_EVENT_LOG                WHERE         bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             TERMINAL_ATM_JOURNAL_LOG_HST        WHERE         bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             TERMINAL_ATM                        WHERE         bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             NDC_WATCH_CONFIG                    WHERE         bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE          APPL_ONEPAGE_CAPTURE_VALID_HST        WHERE         bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE          ATM_CASHSEND_REQUEST_HST            WHERE         payer_bank_code = :1'        USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE          ATM_COMMANDS                        WHERE         termINal_number IN (SELECT termINal_number FROM termINal_atm  WHERE bank_code = :1)'      USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE          ATM_REPLY_SWITCH                    WHERE         bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE          ATM_RESPONSE_LABEL                     WHERE         bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           TERMINAL_ATM_WATCH_ACTIVITY_HT      WHERE         bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           AUTHO_ACTIVITY_ADM                  WHERE         issuINg_bank = :1'          USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           AUTHO_ACTIVITY_SAF                  WHERE         issuINg_bank = :1'          USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           AUTHO_ACTIVITY_EVT                  WHERE         issuINg_bank = :1'          USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           AUTHO_ACTIVITY_HST                  WHERE         issuINg_bank = :1'          USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           AUTHO_ACTIVITY_MTH                  WHERE         issuINg_bank = :1'          USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           AUTHO_ACTIVITY_ATM                  WHERE         issuINg_bank = :1'          USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           AUTHO_ACTIVITY_ASM                  WHERE         issuINg_bank = :1'          USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           AUTHO_ACTIVITY_PRE                  WHERE         issuINg_bank = :1'          USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           AUTHO_ACTIVITY_MSC                  WHERE         issuINg_bank = :1'          USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           AUTHO_ACTIVITY_TRN                  WHERE         issuINg_bank = :1'          USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           EMAIL_STAGING_TABLE                 WHERE         bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             ONLINE_SETTLEMENT_NETWORK         ';
            EXECUTE IMMEDIATE ' DELETE           P7_STATUS_LOG_FILE                  WHERE         acquirer_bank= :1'          USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           P7_STATUS_LOG_FILE                  WHERE          issuINg_bank= :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           PCARD_AUTHENTIFICATION_HIST         WHERE         bank_code = :1'              USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             PIN_RESET_HIST                         WHERE         card_number IN (SELECT card_number FROM card  WHERE bank_code = :1 )'     USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             pIN_change_INfo                     WHERE         card_number IN (SELECT card_number FROM card  WHERE bank_code = :1 )'     USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             ACCOUNTS_LINK                        WHERE         account_bank_code= :1'         USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             BALANCE                             WHERE         bank_code= :1'                 USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             CARD_ADDENDUM                         WHERE         bank_code= :1'                 USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             CARD_ADV_TO_SWITCH_BATCH            WHERE         bank_code= :1'                 USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             CARDBATCH                             WHERE         bank_code= :1'                 USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             LOYALTY_WELCOME_EVENT                 WHERE         bank_code= :1'                 USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             M_STAT_CARD                         WHERE         bank_code= :1'                 USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             M_STAT_PTSERV                         WHERE         bank_code= :1'                 USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             M_STAT_TRANSACTIONS                 WHERE         issuer_bank_code= :1'         USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             PCARD_USER_BLOCKED                     WHERE         bank_code= :1'                 USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             PCRD_FILE_PROCESSING                 WHERE         bank_code= :1'                 USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             OAS_MC_SUBSCRIPTION                 WHERE         bank_code= :1'                 USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           DWH_CARD_DIM_INCREMENTAL             WHERE         card_number IN (SELECT card_number FROM card WHERE bank_code = :1)'     USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           card_VAL                             WHERE         bank_code= :1'                 USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           card_perso                             WHERE         card_number IN (SELECT card_number FROM card  WHERE bank_code = :1 )'     USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           card_calcul                         WHERE         card_number IN (SELECT card_number FROM card  WHERE bank_code = :1 )'     USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           card_fees_billINg                     WHERE         bank_code= :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           card_production                     WHERE         bank_code= :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           PCRD_LAST_RENEWAL_PROCES_MONTH         WHERE         bank_code= :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           card                                 WHERE         bank_code= :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           CARD_CHANGE_ADV_TO_SWITCH             WHERE         card_number IN (SELECT card_number FROM card WHERE bank_code= :1)' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           card                                 WHERE         bank_code= :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           STOP_LIST_CARD_BIN_RANGE             WHERE         bank_code= :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           STOP_LIST_HIST                         WHERE         bank_code= :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE           client                                 WHERE         bank_code= :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_ACC_CONTRACT_ELMT_CRE            WHERE         contract_elmt_id IN (SELECT contract_elmt_id FROM MER_ACCEPTANCE_CONTRACT_ELMT WHERE bank_code  = :1)'      USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             CRE_MER_CHARGES                     WHERE         chargINg_id  IN (SELECT chargINg_id FROM MER_CHARGES WHERE bank_code = :1 )'                                 USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             CRE_MER_BILLING_CRITERIA             WHERE         criteria_id IN (SELECT criteria_id FROM mer_billINg_criteria WHERE bank_code = :1 ) '                        USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             CRE_MER_POSTING                     WHERE         postINg_id IN (SELECT postINg_id FROM MER_POSTING WHERE bank_code = :1 )  '                                   USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             CRE_MERCHANT_DATA                     WHERE         merchant_number IN (SELECT merchant_number FROM merchant WHERE bank_code = :1 )'                             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_ACCEPTED_NETWORKS                WHERE         contract_elmt_id IN (SELECT contract_elmt_id FROM MER_ACCEPTANCE_CONTRACT_ELMT WHERE bank_code  = :1)'      USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             ACCEPTED_CURRENCIES                 WHERE         contract_elmt_id IN (SELECT contract_elmt_id FROM MER_ACCEPTANCE_CONTRACT_ELMT WHERE bank_code  = :1)'      USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_ACC_CONTRACT_SERVICES            WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_ACC_CONTRACT_TRANSACTIONS       WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_ACCEPTANCE_CONTRACT_ELMT        WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_ACCEPTOR_POINT                  WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_ACCOUNT                            WHERE       mer_bank_code  = :1'        USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_ACQUIRING_SITE                    WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_ACTIVITY                           WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_CHARGES                            WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_BILLING_CRITERIA                   WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_CONTRACT_CARACTERISTICS            WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_POSTING                            WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_PRODUCT                            WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_PRODUCT_CONTEXT                    WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MER_SERVICES_LIST                      WHERE         bank_code = :1'             USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE             MERCHANT                               WHERE         bank_code = :1'             USING p_bank_code;


        RETURN DECLARATION_CST.OK;
    END AUT_CONV_DATA_ROLLBACK;


    FUNCTION AUT_CONV_FINALPARAM_ROLLBACK (   p_bank_code               IN                  BANK.bank_code%TYPE,
                                            p_bank_wording               IN               BANK.bank_name%TYPE,
                                            p_country_code                IN                  COUNTRY.country_code%TYPE)
        RETURN PLS_INTEGER
    IS
    BEGIN

            EXECUTE IMMEDIATE ' DELETE P7_PRD_LIMITS_SETUP     WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE CATALOGUE_STATUS_TRAIL    WHERE bank_code = :1' USING p_bank_code;
           EXECUTE IMMEDIATE ' DELETE P7_BANK_RESOURCE_PARAM    WHERE acquirer_bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE RESOURCES_PARAM         WHERE resource_id in ((SELECT resource_id FROM st_temp_resources ))';
            EXECUTE IMMEDIATE ' DELETE p7_routing_criteria                               WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE p7_RESOURCES_SERVICES    WHERE resource_id in ((SELECT resource_id FROM st_temp_resources ))';
            EXECUTE IMMEDIATE ' DELETE resources        WHERE resource_id in ((SELECT resource_id FROM st_temp_resources ))';
             EXECUTE IMMEDIATE ' DELETE MULTI_RANGE_PRODUCTS       WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE HSM_KEY_MEMBER       WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE HSM_KEY_MEMBER       WHERE  label = :1' USING p_bank_wording;
            EXECUTE IMMEDIATE ' DELETE catalogue_injected_param  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE catalogue_prod_eligibility  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE CATALOGUE_PRODUCT  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE MULTI_RANGE_PRODUCTS              WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE catalogue_injected_param  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE catalogue_prod_eligibility  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE CATALOGUE_PRODUCT  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE stop_list_versions  WHERE sl_bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE zip_code                                           WHERE   country_code =:1' USING p_country_code;
            EXECUTE IMMEDIATE ' DELETE city                                             WHERE city_name <>''DEFAULT'' and country_code =:1' USING p_country_code;
            EXECUTE IMMEDIATE ' DELETE region                                           WHERE region_name <>''DEFAULT'' and country_code =:1' USING p_country_code;
            EXECUTE IMMEDIATE ' DELETE EXHIBIT_REPORT                                   WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE pcard_report_param                               WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE P7_LIMITS                                        WHERE bank_code = :1' USING p_bank_code;--

            EXECUTE IMMEDIATE ' DELETE icc_card_verification_detail                      WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE emv_icc_appl_definition                          WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_TERMINAL_CASSETTES                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_SY_8FDK_SEL_FUNCT                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_SX_FDK_INFO_ENTRY                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_SW_FDK_SWITCH                                 WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_STATE_TABLE                                   WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_SK_FIT_SWITCH                                 WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_SJ_CLOSE                                      WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_SI_TRANS_REQUEST                              WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_SG_AMOUNT_CHECK                               WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_SF_AMOUNT_ENTRY                               WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_SD_PRESET_OPERATION                           WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_SB_PIN_ENTRY                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_SB_CUSTOMER_SELECTABLE_PIN                    WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_SA_CARD_READ                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_S__ICC_TRANS_DATA                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_S__ICC_RE_INIT                                WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_S__COMPL_ICC_INIT                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_S__C_APPLI_SEL_INIT                           WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_S__BEGIN_ICC_INIT                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_S__B_APPLI_SEL_INIT                           WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_S__AUTO_LANG_SEL                              WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_PRINTED_TEXT                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_PRINTED_OBJECT                                WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_PRINT_LAYOUT                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_JOURNAL_PRINTED_TEXT                          WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_JOURNAL_PRINTED_OBJECT                        WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_JOURNAL_PRINT_LAYOUT                          WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_IDLE_SCREENS                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_FIT                                           WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_EMV_TRANSACTION                               WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_EMV_TERMINAL                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_EMV_LANGUAGE                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_EMV_ENH_CONFIG                                WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_EMV_DATA_SETS                                 WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_EMV_CURRENCY                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_EMV_APPLICATION                               WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_DISPLAYED_TEXT                                WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_DISPLAYED_OBJECT                              WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE ATM_BRAND                                         WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_SCREEN_LAYOUT                                 WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_CASSETTE_TYPE                                 WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_CASSETTE_GROUPING                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_ALGORITHM_PARAM                               WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_TERMINAL_PROFILE_ADDENDUM                     WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NDC_TERMINAL_PROFILE                              WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE DBL_TERMINAL_PROFILE                              WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE TERMINAL_POS_GROUPING                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE TERMINAL_ATM_GROUP                                WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE bank_switch_cut_off                               WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE VISA_INTERCHANGE_PAR                              WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE TRANS_REJECT_FLAG_DEF                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE TITLE_LIST                                        WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE STK_INVENTORY_ITEM_DESC                           WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE RET_REQ_REASON_CODE                                WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE REMITTANCE_SEQ                                     WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE QUEUE_CRITERIA                                     WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE PWC_REPORTS_USER_SETUP                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE POTENTIAL_CHGBK_REASON_CODE                        WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE P7_REASON_CODE_MAPPING                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE NATIONAL_INTERCHANGE_PAR                           WHERE   acquirer_bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE M_EDUCATION_LIST                                   WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE HOLIDAYS_FE                                        WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE HOLIDAYS                                           WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE HOLD_STATEMENT_REASON_PARAM                        WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE EXTERNAL_ID_GEN_MODE                               WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE EVENT_PARAM_TABLE                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE ERSB_REASON_CODE                                   WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE DOCUMENT_LIST                                      WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE DATA_ACCESS                                        WHERE data_access_name =  :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE CHANNEL_TYPE_LIST                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE BRANCH                                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE BRANCH_GROUPS                                      WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE BANK_ACCOUNT_TYPE_LIST                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE APPLICATION_WORK_STATUS                            WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE APPLICATION_TYPE                                   WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE APPLICATION_REJECT_REASON                          WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE APPLICATION_REASON_FORCING                         WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE APPLICATION_EVENT                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE ACCOUNT_TYPE_LIST                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE ACCOUNT_LANG_LIST                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE PCRD_CONTACT_POSITION_LIST                         WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE POWERCARD_GLOBALS_BANK                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE mer_services_list                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE BANK_APPLICATION_PARAM                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE TRANS_CTRL_VALUE_PARAM                             WHERE acquirer_bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE emv_fallback_risk_mng                              WHERE issuer_bank_code      = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE emv_icc_application_param                          WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE icc_application_par_index                          WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE pcrd_trans_ctrl_param                              WHERE acquirer_bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE p7_action_when_event                               WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE queue_case_type                                    WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE scenario_case_reason_link                          WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE queue_case_reason_link                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE sms_parameter                                      WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE email_parameter                                    WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE queue_profile                                      WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE case_reason                                        WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE priority_table                                     WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE link_scenario_action                               WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE scenario_table                                     WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE queue                                              WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE action_table                                       WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE case_type                                          WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE TRANS_CONTROL_PARAM                                WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE trans_reject_param                                 WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE conversion_rate                                    WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE pwc_bank_report_parameters                         WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE emv_script_description                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE trans_bank_param                                   WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE replacement_reason_code                            WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE withdrawal_reason_code                             WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE stop_list_reason_code                              WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE working_days                                       WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE Status_reason_transition                           WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE status_reason_trans_source                         WHERE bank_code =:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE addresses_type_list                                WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE trans_mv_batch                                     WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE trans_mv_linkup                                    WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE trans_reason_code                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE group_reporting_def                                WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE department                                         WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE MARKUP_ELLIGIBLE_CURRENCIES                        WHERE bank_code= :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE MARKUP_CALCUL                                      WHERE bank_code= :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE clearing_partner                                 WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE bank_case_param                                  WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE customer_segment                                 WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE socioprof_list                                   WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE client_activity_set                              WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE owner_list                                       WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE card_range                                        WHERE issuing_bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE bank_network                                     WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE CARD_CARRIER_CRITERIA_PARAM                       WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE pcrd_card_prod_param                              WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE batch_renewal_criteria                            WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE p7_range_switch                                   WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE card_gen_counters                                 WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE STOP_LIST_FEES_PARAM                                 WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE autho_fees_param                                    WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE card_product                                       WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE status_reason_list                               WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE status_list                                      WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE markup_currency_index                             WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE markup_index                                     WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE vip_list                                         WHERE bank_code = :1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE emv_keys_assignment                               WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE credit_auth_param                                 WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE p7_emv_limit_setup                                WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE p7_spec_trans_limits                              WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE p7_sa_limits_setup                                WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE p7_SERVICES_SETUP                                 WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE P7_SERVICES_SETUP_NAME                            WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE card_fees                                         WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE card_type                                         WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE plastic_list                                      WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE EMV_TAGS_CHECKING_FLAGS                           WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE stop_list_parameters                              WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE remittance_agent                                  WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE PWC_TOKEN_INTERFACE_SETUP                         WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE PWC_TOKEN_FORMAT                                  WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE POS_BRAND                                         WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE MERCHANT_ACTIVITY_SET                             WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE BANK_CONTEXT_VALUE                                WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE POS_PROFILE                                       WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE POS_SOFT                                          WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE mer_exchange_matrix                               WHERE acquirer_bank=:1' USING p_bank_code;--
            EXECUTE IMMEDIATE ' DELETE frd_event_rule_def_val                            WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE frd_event_rule_def                                WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE icc_card_verification_detail                      WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE lis_version_param                                 WHERE  lis_identification_code IN (SELECT lis_code FROM  lis_bank_identification WHERE issuer_bank_code=:1)' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE lis_identification                                WHERE destination_bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE lis_bank_identification                           WHERE issuer_bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE stop_renewal_criteria                             WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE rskm_actions_list                                 WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE rskm_processing_list                              WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE high_risk_mcc                                     WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE rskm_mcc_list                                     WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE rskm_country_list                                 WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE rskm_card_list                                    WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE rskm_outlet_id_list                               WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE rskm_terminal_id_list                             WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE P7_SERVICES_criteria                              WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE P7_SERVICES_definition                            WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE reject_class                                      WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE rskm_action_list                                  WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE fraud_entities_list                               WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE iss_posting_rules                                 WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE statement_parameters                              WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE card_carrier_list                                 WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE auth_ctrl_value_param                             WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE Product_domain_setup                              WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE control_verification_flags                        WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE screen_criteria_param                             WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE chargeback_reason_code                            WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE MER_CHARGES                                       WHERE bank_code=:1 AND fee_transaction_code =''ST''' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE MER_TAX_PARAMETERS                                WHERE acquirer_bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE Fleet_ctrl_verif_flags                            WHERE bank_code=:1' USING p_bank_code;
            EXECUTE IMMEDIATE ' DELETE Entity_event_grouping                             WHERE bank_code=:1' USING p_bank_code;




        RETURN DECLARATION_CST.OK;
    END AUT_CONV_FINALPARAM_ROLLBACK;

     FUNCTION AUT_CONV_GLB_TEMP_ROLLBACK (   p_bank_code               IN                  BANK.bank_code%TYPE,
                                            p_bank_wording               IN               BANK.bank_name%TYPE,
                                            p_country_code           IN                  COUNTRY.country_code%TYPE)
        RETURN PLS_INTEGER
    IS
    BEGIN


            EXECUTE IMMEDIATE ' DELETE  st_new_hsm_key_member                           ';
            EXECUTE IMMEDIATE ' DELETE  st_new_chargeback_reason_code               ';
            EXECUTE IMMEDIATE ' DELETE  st_new_auth_ctrl_value_param                ';
            EXECUTE IMMEDIATE ' DELETE  st_new_iss_posting_rules                    ';
            EXECUTE IMMEDIATE ' DELETE  st_new_P7_SERVICES_criteria                 ';
            EXECUTE IMMEDIATE ' DELETE  st_new_stop_renewal_criteria                ';
            EXECUTE IMMEDIATE ' DELETE  st_new_BANK_CONTEXT_VALUE                   ';
            EXECUTE IMMEDIATE ' DELETE  st_new_owner_list  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_client_activity_set  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_socioprof_list ';
            EXECUTE IMMEDIATE ' DELETE  st_new_customer_segment ';
            EXECUTE IMMEDIATE ' DELETE  st_new_bank_case_param ';
            EXECUTE IMMEDIATE ' DELETE  st_new_bank_network  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_clearing_partner  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_vip_list ';
            EXECUTE IMMEDIATE ' DELETE  st_new_department ';
            EXECUTE IMMEDIATE ' DELETE  st_new_group_reporting_def ';
            EXECUTE IMMEDIATE ' DELETE  st_new_trans_reason_code ';
            EXECUTE IMMEDIATE ' DELETE  st_new_trans_mv_linkup  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_trans_mv_batch  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_addresses_type_list  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_status_list  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_status_reason_trans_source';
            EXECUTE IMMEDIATE ' DELETE  st_new_status_reason_list  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_Status_reason_transition  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_working_days  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_stop_list_reason_code  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_withdrawal_reason_code  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_replacement_reason_code  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_trans_bank_param ';
            EXECUTE IMMEDIATE ' DELETE  st_new_emv_script_description ';
            EXECUTE IMMEDIATE ' DELETE  st_new_pwc_bank_report_parameters ';
            EXECUTE IMMEDIATE ' DELETE  st_new_conversion_rate ';
            EXECUTE IMMEDIATE ' DELETE  st_new_trans_reject_param ';
            EXECUTE IMMEDIATE ' DELETE  st_new_TRANS_CONTROL_PARAM ';
            EXECUTE IMMEDIATE ' DELETE  st_new_case_type ';
            EXECUTE IMMEDIATE ' DELETE  st_new_action_table ';
            EXECUTE IMMEDIATE ' DELETE  st_new_queue ';
            EXECUTE IMMEDIATE ' DELETE  st_new_scenario_table ';
            EXECUTE IMMEDIATE ' DELETE  st_new_link_scenario_action ';
            EXECUTE IMMEDIATE ' DELETE  st_new_priority_table ';
            EXECUTE IMMEDIATE ' DELETE  st_new_case_reason ';
            EXECUTE IMMEDIATE ' DELETE  st_new_queue_profile ';
            EXECUTE IMMEDIATE ' DELETE  st_new_email_parameter ';
            EXECUTE IMMEDIATE ' DELETE  st_new_sms_parameter ';
            EXECUTE IMMEDIATE ' DELETE  st_new_queue_case_reason_link  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_scenario_case_reason_link ';
            EXECUTE IMMEDIATE ' DELETE  st_new_queue_case_type ';
            EXECUTE IMMEDIATE ' DELETE  st_new_p7_services_definition ';
            EXECUTE IMMEDIATE ' DELETE  st_new_p7_action_when_event ';
            EXECUTE IMMEDIATE ' DELETE  st_new_pcrd_trans_ctrl_param ';
            EXECUTE IMMEDIATE ' DELETE  st_new_emv_icc_application_param  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_emv_fallback_risk_mng ';
            EXECUTE IMMEDIATE ' DELETE  st_new_TRANS_CTRL_VALUE_PARAM ';
            EXECUTE IMMEDIATE ' DELETE  st_new_BANK_APPLICATION_PARAM ';
            EXECUTE IMMEDIATE ' DELETE  st_new_mer_services_list ';
            EXECUTE IMMEDIATE ' DELETE  st_new_POWERCARD_GLOBALS_BANK ';
            EXECUTE IMMEDIATE ' DELETE  st_new_PCRD_CONTACT_POSITION_LIST ';
            EXECUTE IMMEDIATE ' DELETE  st_new_ACCOUNT_LANG_LIST             ';
            EXECUTE IMMEDIATE ' DELETE  st_new_ACCOUNT_TYPE_LIST          ';
            EXECUTE IMMEDIATE ' DELETE  st_new_APPLICATION_EVENT   ';
            EXECUTE IMMEDIATE ' DELETE  st_new_APPLICATION_REASON_FORCING ';
            EXECUTE IMMEDIATE ' DELETE  st_new_APPLICATION_REJECT_REASON';
            EXECUTE IMMEDIATE ' DELETE  st_new_APPLICATION_TYPE        ';
            EXECUTE IMMEDIATE ' DELETE  st_new_APPLICATION_WORK_STATUS    ';
            EXECUTE IMMEDIATE ' DELETE  st_new_CHANNEL_TYPE_LIST  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_BANK_ACCOUNT_TYPE_LIST  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_DATA_ACCESS                  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_DOCUMENT_LIST            ';
            EXECUTE IMMEDIATE ' DELETE  st_new_ERSB_REASON_CODE          ';
            EXECUTE IMMEDIATE ' DELETE  st_new_EVENT_PARAM_TABLE         ';
            EXECUTE IMMEDIATE ' DELETE  st_new_pcard_report_param     ';--
            EXECUTE IMMEDIATE ' DELETE  st_new_EXHIBIT_REPORT            ';
            EXECUTE IMMEDIATE ' DELETE  st_new_EXTERNAL_ID_GEN_MODE     ';
            EXECUTE IMMEDIATE ' DELETE  st_new_HOLD_STATEMENT_REASON_PARAM ';
            EXECUTE IMMEDIATE ' DELETE  st_new_HOLIDAYS                    ';
            EXECUTE IMMEDIATE ' DELETE  st_new_HOLIDAYS_FE               ';
            EXECUTE IMMEDIATE ' DELETE  st_new_M_EDUCATION_LIST           ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NATIONAL_INTERCHANGE_PAR   ';
            EXECUTE IMMEDIATE ' DELETE  st_new_P7_REASON_CODE_MAPPING      ';
            EXECUTE IMMEDIATE ' DELETE  st_new_POTENTIAL_CHGBK_REASON_CODE  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_PWC_REPORTS_USER_SETUP      ';
            EXECUTE IMMEDIATE ' DELETE  st_new_QUEUE_CRITERIA           ';
            EXECUTE IMMEDIATE ' DELETE  st_new_REMITTANCE_SEQ          ';
            EXECUTE IMMEDIATE ' DELETE  st_new_RET_REQ_REASON_CODE       ';
            EXECUTE IMMEDIATE ' DELETE  st_new_STK_INVENTORY_ITEM_DESC    ';
            EXECUTE IMMEDIATE ' DELETE  st_new_STOP_LIST_VERSIONS             ';
            EXECUTE IMMEDIATE ' DELETE  st_new_TITLE_LIST            ';
            EXECUTE IMMEDIATE ' DELETE  st_new_TRANS_REJECT_FLAG_DEF    ';
            EXECUTE IMMEDIATE ' DELETE  st_new_VISA_INTERCHANGE_PAR       ';
            EXECUTE IMMEDIATE ' DELETE  st_new_bank_switch_cut_off        ';
            EXECUTE IMMEDIATE ' DELETE  st_new_TERMINAL_ATM_GROUP        ';
            EXECUTE IMMEDIATE ' DELETE  st_new_TERMINAL_POS_GROUPING       ';
            EXECUTE IMMEDIATE ' DELETE  st_new_DBL_TERMINAL_PROFILE        ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_TERMINAL_PROFILE       ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_TERMINAL_PROFILE_ADDENDUM ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_ALGORITHM_PARAM           ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_CASSETTE_GROUPING          ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_CASSETTE_TYPE          ';
            EXECUTE IMMEDIATE ' DELETE  st_new_ATM_BRAND                 ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_DISPLAYED_OBJECT          ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_DISPLAYED_TEXT            ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_EMV_APPLICATION        ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_EMV_CURRENCY           ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_EMV_DATA_SETS         ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_EMV_ENH_CONFIG         ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_EMV_LANGUAGE            ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_EMV_TERMINAL         ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_EMV_TRANSACTION      ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_FIT                  ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_IDLE_SCREENS         ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_JOURNAL_PRINT_LAYOUT    ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_JOURNAL_PRINTED_OBJECT   ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_JOURNAL_PRINTED_TEXT    ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_PRINT_LAYOUT           ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_PRINTED_OBJECT            ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_PRINTED_TEXT               ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_S__AUTO_LANG_SEL          ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_S__B_APPLI_SEL_INIT       ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_S__BEGIN_ICC_INIT          ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_S__C_APPLI_SEL_INIT      ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_S__COMPL_ICC_INIT         ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_S__ICC_RE_INIT            ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_S__ICC_TRANS_DATA        ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_SA_CARD_READ              ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_SB_CUSTOMER_SELECTABLE_PIN ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_SB_PIN_ENTRY            ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_SCREEN_LAYOUT             ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_SD_PRESET_OPERATION       ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_SF_AMOUNT_ENTRY         ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_SG_AMOUNT_CHECK          ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_SI_TRANS_REQUEST         ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_SJ_CLOSE                 ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_SK_FIT_SWITCH           ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_STATE_TABLE             ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_SW_FDK_SWITCH            ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_SX_FDK_INFO_ENTRY         ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_SY_8FDK_SEL_FUNCT        ';
            EXECUTE IMMEDIATE ' DELETE  st_new_NDC_TERMINAL_CASSETTES      ';


        RETURN DECLARATION_CST.OK;
    END AUT_CONV_GLB_TEMP_ROLLBACK;

    FUNCTION AUT_CONV_PRODUCT_TEMP_ROLLBACK (   p_bank_code               IN                  BANK.bank_code%TYPE,
                                            p_bank_wording               IN               BANK.bank_name%TYPE,
                                            p_country_code           IN                  COUNTRY.country_code%TYPE)
        RETURN PLS_INTEGER
    IS
    BEGIN
    dbms_output.put_line('DAAAAAAAAAAAAAAAAAAAAZ4 ');

            EXECUTE IMMEDIATE ' DELETE   st_mig_markup_currency_index';
            EXECUTE IMMEDIATE ' DELETE   st_mig_markup_index                   ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_markup_calcul                   ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_markup_elligible_currencies    ';
           EXECUTE IMMEDIATE ' DELETE   st_mig_ICC_CARD_VERIFICATION_DETAIL  ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_icc_application_par_index';
            EXECUTE IMMEDIATE ' DELETE   st_mig_Fleet_ctrl';
            EXECUTE IMMEDIATE ' DELETE   st_mig_Entity_event';
            EXECUTE IMMEDIATE ' DELETE   st_mig_product_domain';
            EXECUTE IMMEDIATE ' DELETE   st_mig_batch_renewal_criteria ';

            EXECUTE IMMEDIATE ' DELETE   st_mig_card_fees  ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_card_gen_counters ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_card_product ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_card_range';
            EXECUTE IMMEDIATE ' DELETE   st_mig_card_type ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_credit_auth_param ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_emv_keys_assignment ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_emv_limit_setup ';

            EXECUTE IMMEDIATE ' DELETE   st_mig_pcrd_card_prod_param';
            EXECUTE IMMEDIATE ' DELETE   st_mig_plastic_list';
            EXECUTE IMMEDIATE ' DELETE   st_mig_sa_limits_setup ';

            EXECUTE IMMEDIATE ' DELETE   st_mig_services_setup ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_services_name ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_spec_trans_limits ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_range_switch ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_P7_LIMITS ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_emv_icc_appl_definition ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_ctrl_verification_flags ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_RANGE_KEY';
            EXECUTE IMMEDIATE ' DELETE   st_mig_REGION ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_city ';
            EXECUTE IMMEDIATE ' DELETE   st_mig_branch  ';
      



        RETURN DECLARATION_CST.OK;
    END AUT_CONV_PRODUCT_TEMP_ROLLBACK;






END PCRD_ST_CONV_CLEAN;
/