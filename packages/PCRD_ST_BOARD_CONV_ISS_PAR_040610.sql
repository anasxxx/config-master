
  CREATE OR REPLACE 
  PACKAGE PCRD_ST_BOARD_CONV_ISS_PAR
  IS
------------------------------------------------------------------------------------------------
-- MODIFICATION HISTORY
-- Person        Version  Ref               Date           Comments
-- -----------   ------   -------------     -----------    -------------------------------------
-- A.SARA     1.0.0                         24/07/2024     Initial version
--------------------------------------------------------------------------------------------------------



FUNCTION    LOAD_BANK_CONV_ISS_PARAM          (  p_business_date           IN                  DATE,
                                            p_bank_code                  IN                  BANK.bank_code%TYPE,
                                            p_bank_wording               IN                     BANK.bank_name%TYPE,
                                            p_currency_code              IN                  CURRENCY_TABLE.currency_code%TYPE,
                                            p_currency_code_alpha                 IN                  CURRENCY_TABLE.currency_code_alpha%TYPE,
                                            p_country_code                 IN                 COUNTRY.country_code%TYPE,
                                            p_country_code_alpha                   IN                   COUNTRY.iso_country_alpha%TYPE  )
                                                    RETURN  PLS_INTEGER;

-----------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_branch_PARAMETERS     (  p_business_date                       IN                  DATE,
                                                      p_country_code           IN                  COUNTRY.country_code%TYPE     ,
                                                     p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE,
                                                  p_bank_code                           IN                  BANK.bank_code%TYPE)
                                                        RETURN  PLS_INTEGER ;
-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    RELOAD_RESOURCES_PARAM     (  p_business_date                       IN                  DATE,
                                            p_bank_wording               IN                     BANK.bank_name%TYPE,
                                                    p_bank_code                           IN                  BANK.bank_code%TYPE)
                                                        RETURN  PLS_INTEGER ;
-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_CARD_TYPE_PARAMETERS           (  p_business_date                       IN                  DATE,
                                                    p_bank_code                           IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                       IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;



-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_BIN_RANGE_PLASTIC_PAR          (  p_business_date                       IN                  DATE,
                                                    p_bank_code                           IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                       IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;


-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_CARD_FEES_PARAMETERS           (  p_business_date                       IN                  DATE,
                                                    p_bank_code                           IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                       IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;

-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_SERVICE_PROD_PARAM             (  p_business_date                       IN                  DATE,
                                                    p_bank_code                          IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                      IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;


-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_SERVICE_SETUP_PARAM            (  p_business_date                       IN                  DATE,
                                                    p_bank_code                           IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                       IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;
-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_P7_limits_PARAMETERS              (  p_business_date                       IN                  DATE,
                                                    p_bank_code                           IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                       IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;



-----------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_LIMIT_STAND_PARAM              (  p_business_date                       IN                  DATE,
                                                    p_bank_code                           IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                       IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;

-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_SA_LIMITS_SETUP_PARAM          (  p_business_date                       IN                  DATE,
                                                    p_bank_code                          IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                      IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;

-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_EMV_LIMIT_SETUP                (  p_business_date                      IN                  DATE,
                                                    p_bank_code                          IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                      IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;
-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_EMV_KEYS_ASSIG_PARAM           (  p_business_date                       IN                  DATE,
                                                    p_bank_code                           IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                       IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;

-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_EMV_ICC_APPL_DEF        (  p_business_date                       IN                  DATE,
                                                    p_bank_code                           IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                       IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;

-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_CONTROL_VERIFICATION_PARAM     (  p_business_date                       IN                  DATE,
                                                    p_bank_code                           IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                       IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;

-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_CARD_PRODUCT_PARAM             (  p_business_date                      IN                  DATE,
                                                    p_bank_code                          IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                      IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;


-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_CARD_RANGE_PARAM               (  p_business_date                       IN                  DATE,
                                                    p_bank_code                           IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                       IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;


-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_CARD_GEN_COUNTERS_PARAM        (  p_business_date                      IN                  DATE,
                                                    p_bank_code                          IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                      IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;


-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_ROUTING_CRITERIA_PARAM         (  p_business_date                       IN                  DATE,
                                                    p_bank_code                           IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                       IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;
-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_RENEWAL_CRITERIA_PARAM         (  p_business_date                       IN                  DATE,
                                                    p_bank_code                          IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                      IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;


-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_PCRD_CARD_PROD_PARAM           (  p_business_date                       IN                  DATE,
                                                    p_bank_code                          IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                      IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;


-----------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_Product_domain_PARAM           (  p_business_date                       IN                  DATE,
                                                    p_bank_code                          IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                      IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;




-----------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_icc_application_PARAM           (  p_business_date                       IN                  DATE,
                                                    p_bank_code                          IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                      IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;


FUNCTION    LOAD_Entity_event_PARAM           (  p_business_date                       IN                  DATE,
                                                    p_bank_code                          IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                      IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;

-----------------------------------------------------------------------------------------------------------------------------------

-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_markup_calcul         (  p_business_date                       IN                  DATE,
                                                    p_bank_code                          IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                      IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;

-----------------------------------------------------------------------------------------------------------------------------------


-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_markup_index           (  p_business_date                       IN                  DATE,
                                                    p_bank_code                          IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                      IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;

-----------------------------------------------------------------------------------------------------------------------------------



---------------------------------------------------------------------------------------------------------------------------------


-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_markup_el_cur          (  p_business_date                       IN                  DATE,
                                                    p_bank_code                          IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                      IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;

-----------------------------------------------------------------------------------------------------------------------------------


-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_Fleet_ctrl_PARAM           (  p_business_date                       IN                  DATE,
                                                    p_bank_code                          IN                  BANK.bank_code%TYPE,
                                                    p_currency_code                      IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                        RETURN  PLS_INTEGER ;

-----------------------------------------------------------------------------------------------------------------------------------

FUNCTION    MOVE_PARAMETERS_LOADED              (  p_business_date                       IN                  DATE,
                                                    p_bank_code                           IN                  BANK.bank_code%TYPE)
                                                        RETURN  PLS_INTEGER ;


-----------------------------------------------------------------------------------------------------------------------------------

END pcrd_st_board_conv_iss_par;
/
CREATE OR REPLACE   
PACKAGE BODY PCRD_ST_BOARD_CONV_ISS_PAR 
IS
------------------------------------------------------------------------------------------------
-- MODIFICATION HISTORY
-- Person        Version  Ref               Date           Comments
-- -----------   ------   -------------     -----------    -------------------------------------
-- A.SARA     1.0.0                         24/07/2024     Initial version
-------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_BANK_CONV_ISS_PARAM      ( p_business_date                   IN                  DATE,
                                            p_bank_code                  IN                  BANK.bank_code%TYPE,
                                            p_bank_wording               IN                     BANK.bank_name%TYPE,
                                            p_currency_code              IN                  CURRENCY_TABLE.currency_code%TYPE,
                                            p_currency_code_alpha                 IN                  CURRENCY_TABLE.currency_code_alpha%TYPE,
                                            p_country_code                 IN                 COUNTRY.country_code%TYPE,
                                            p_country_code_alpha                   IN                   COUNTRY.iso_country_alpha%TYPE                                             )
                                    RETURN  PLS_INTEGER IS


Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;



BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_BANK_CONV_ISS_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;


    Return_Status   :=  pcrd_st_board_conv_iss_par.RELOAD_RESOURCES_PARAM  (   p_business_date,
                                                                            p_bank_wording,
                                                                                p_bank_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.RELOAD_RESOURCES_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;


    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_branch_PARAMETERS  (   p_business_date,
                                                                              p_country_code,
                                                                                p_currency_code ,
                                                                                p_bank_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_branch_PARAMETERS :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;



    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_CARD_TYPE_PARAMETERS  (   p_business_date,
                                                                                p_bank_code,
                                                                                p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_CARD_TYPE_PARAMETERS :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;


    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_BIN_RANGE_PLASTIC_PAR  (  p_business_date,
                                                                                p_bank_code,
                                                                                p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_BIN_RANGE_PLASTIC_PAR :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;


    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_CARD_FEES_PARAMETERS  (   p_business_date,
                                                                                p_bank_code,
                                                                                p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_CARD_FEES_PARAMETERS :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;


    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_SERVICE_PROD_PARAM          (  p_business_date,
                                                                                p_bank_code,
                                                                                p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_SERVICE_PROD_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;

    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_SERVICE_SETUP_PARAM      (  p_business_date,
                                                                                p_bank_code,
                                                                                p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_SERVICE_SETUP_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;

    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_P7_limits_PARAMETERS          (  p_business_date,
                                                                                p_bank_code,
                                                                                p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_P7_limits_PARAMETERS :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;

    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_LIMIT_STAND_PARAM          (  p_business_date,
                                                                                p_bank_code,
                                                                                p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_LIMIT_STAND_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;

    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_SA_LIMITS_SETUP_PARAM      (  p_business_date,
                                                                                p_bank_code,
                                                                                p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_SA_LIMITS_SETUP_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;

    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_EMV_LIMIT_SETUP          (  p_business_date,
                                                                                p_bank_code,
                                                                                p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_EMV_LIMIT_SETUP :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;


    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_EMV_KEYS_ASSIG_PARAM      (  p_business_date,
                                                                                p_bank_code,
                                                                                p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_EMV_KEYS_ASSIG_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;
    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_EMV_ICC_APPL_DEF          (  p_business_date,
                                                                                p_bank_code,
                                                                                p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_EMV_ICC_APPL_DEF :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;


    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_CONTROL_VERIFICATION_PARAM  ( p_business_date,
                                                                                    p_bank_code,
                                                                                    p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_CONTROL_VERIFICATION_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;


    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_CARD_PRODUCT_PARAM              (  p_business_date,
                                                                                    p_bank_code,
                                                                                    p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_CARD_PRODUCT_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;

    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_CARD_RANGE_PARAM              (  p_business_date,
                                                                                    p_bank_code,
                                                                                    p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_CARD_RANGE_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;

    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_CARD_GEN_COUNTERS_PARAM      (p_business_date,
                                                                                    p_bank_code,
                                                                                    p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_CARD_GEN_COUNTERS_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;

    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_ROUTING_CRITERIA_PARAM      ( p_business_date,
                                                                                    p_bank_code,
                                                                                    p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_ROUTING_CRITERIA_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;



    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_RENEWAL_CRITERIA_PARAM        (  p_business_date,
                                                                                    p_bank_code,
                                                                                    p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_RENEWAL_CRITERIA_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;

    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_PCRD_CARD_PROD_PARAM          (  p_business_date,
                                                                                    p_bank_code,
                                                                                    p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_PCRD_CARD_PROD_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;

    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_Product_domain_PARAM          (  p_business_date,
                                                                                    p_bank_code,
                                                                                    p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_Product_domain_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;

    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_Entity_event_PARAM          (  p_business_date,
                                                                                    p_bank_code,
                                                                                    p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_Entity_event_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;
     Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_icc_application_PARAM          (  p_business_date,
                                                                                    p_bank_code,
                                                                                    p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_icc_application_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;

    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_markup_calcul          (  p_business_date,
                                                                                    p_bank_code,
                                                                                    p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_markup_calcul :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;

    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_markup_index         (  p_business_date,
                                                                                    p_bank_code,
                                                                                    p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_markup_index :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);

      END IF;
    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_markup_el_cur          (  p_business_date,
                                                                                    p_bank_code,
                                                                                    p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_markup_el_cur :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;
    Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_Fleet_ctrl_PARAM          (  p_business_date,
                                                                                    p_bank_code,
                                                                                    p_currency_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_Fleet_ctrl_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;


  Return_Status   :=  pcrd_st_board_conv_iss_par.MOVE_PARAMETERS_LOADED     (   p_business_date,
                                                                             p_bank_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.MOVE_PARAMETERS_LOADED :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);

    END IF;

    IF Return_Status = declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':Cest OK :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);


    END IF;


  Return_Status   :=  pcrd_st_conv_catalogue.MAIN_AUT_POST      (   p_bank_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_conv_catalogue.MAIN_AUT_POST :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);

    END IF;


    IF Return_Status = declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':Cest OK 2:'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);

    COMMIT;
    END IF;

    RETURN (declaration_cst.OK);

EXCEPTION WHEN OTHERS
THEN
    v_env_info_trace.user_message   :=  NULL;
    PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
    RETURN (declaration_cst.ERROR);
END LOAD_BANK_CONV_ISS_PARAM;
----------------------------------------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_CARD_TYPE_PARAMETERS           (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is

    Return_Status                       PLS_INTEGER;
    v_env_info_trace                    global_vars.env_info_trace_type;
    v_sequence                          NUMBER(2):=0;
    v_mig_card_type_rec                   st_mig_CARD_TYPE%ROWTYPE := NULL;

CURSOR CUR_BIN_RANGE_PLASTIC_PROD IS
    SELECT  *
    FROM      st_pre_bin_range_plastic_prod
    where  product_code is not null
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_CARD_TYPE_PARAMETERS';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_BIN_RANGE_PLASTIC_PROD_rec    IN  cur_BIN_RANGE_PLASTIC_PROD
    LOOP


        v_mig_card_type_rec.bank_code                   :=  p_bank_code ;
        v_mig_card_type_rec.network_card_type           :=  TRIM(v_bin_range_plastic_prod_rec.product_type);
        v_mig_card_type_rec.abrv_wording                :=  substr(trim(v_bin_range_plastic_prod_rec.description),1,16) ;
        v_mig_card_type_rec.wording                     :=  substr(trim( v_bin_range_plastic_prod_rec.description) ,1,30) ;
        v_mig_card_type_rec.class                       :=  '01';
        v_mig_card_type_rec.class_group                 :=  'IN';
        v_mig_card_type_rec.class_level                 :=  '1';
        v_mig_card_type_rec.corporate_card_flag         :=  'N';
        v_mig_card_type_rec.cobranded_card_flag         :=  'N';
        v_mig_card_type_rec.purchase_card_flag          :=  'N';
        v_mig_card_type_rec.business_card_flag          :=  'N';
        v_mig_card_type_rec.affinity_card_flag          :=  'N';

        IF      TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='VISA'
            THEN
                v_mig_card_type_rec.network_code                :=  '01'    ;

        ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='PRIVATIVE'
            THEN
                v_mig_card_type_rec.network_code                :=  '00'    ;
        ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='GIMN'
            THEN
                v_mig_card_type_rec.network_code                :=  '21'    ;
        ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='AMEX'
            THEN
                v_mig_card_type_rec.network_code                :=  '04'    ;
        ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='MCRD'
            THEN
                v_mig_card_type_rec.network_code                :=  '02'    ;
        ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='EUROPAY'
            THEN
                v_mig_card_type_rec.network_code                :=  '03'    ;
        ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='TAG-YUP'
            THEN
                v_mig_card_type_rec.network_code                :=  '07'    ;
        ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='DINERS'
            THEN
                v_mig_card_type_rec.network_code                :=  '05'    ;
        END IF;


        v_sequence  :=  v_sequence + 1;

        INSERT INTO   st_mig_CARD_TYPE VALUES v_mig_card_type_rec;

    END LOOP;

    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_CARD_TYPE_PARAMETERS;
--------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_BIN_RANGE_PLASTIC_PAR          (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_plastic_list_rec                st_mig_PLASTIC_LIST%ROWTYPE := NULL;

CURSOR cur_BIN_RANGE_PLASTIC_PROD IS
    SELECT  *
    FROM      st_pre_bin_range_plastic_prod
    where  product_code is not null
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_BIN_RANGE_PLASTIC_PAR';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_BIN_RANGE_PLASTIC_PROD_rec    IN  cur_BIN_RANGE_PLASTIC_PROD
    LOOP


        v_mig_plastic_list_rec.bank_code                         := p_bank_code ;
        v_mig_plastic_list_rec.plastic_code                      := TRIM(v_bin_range_plastic_prod_rec.plastic_type);
        v_mig_plastic_list_rec.abrv_wording                      := SUBSTR(TRIM('PLASTIC_'|| v_bin_range_plastic_prod_rec.description),1,16)           ;
        v_mig_plastic_list_rec.wording                           := SUBSTR(TRIM('PLASTIC_'|| v_bin_range_plastic_prod_rec.description) ,1,30)     ;
        v_mig_plastic_list_rec.production_ind                    := 'PE';
        v_mig_plastic_list_rec.free_text_1                       := NULL;
        v_mig_plastic_list_rec.free_text_position_1              := NULL;
        v_mig_plastic_list_rec.free_text_2                       := NULL;
        v_mig_plastic_list_rec.free_text_position_2              := NULL;

        INSERT INTO   st_mig_PLASTIC_LIST VALUES v_mig_plastic_list_rec;

    END LOOP;

    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_BIN_RANGE_PLASTIC_PAR;

--------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_CARD_FEES_PARAMETERS           (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_card_fees_rec                   st_mig_CARD_FEES%ROWTYPE :=    NULL;


CURSOR CUR_pre_mig_CARD_FEES IS
    SELECT  *
    FROM      st_pre_mig_CARD_FEES
    ORDER BY  card_fees_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_CARD_FEES_PARAMETERS';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_pre_mig_CARD_FEES_rec  IN  CUR_pre_mig_CARD_FEES
    LOOP


        v_mig_card_fees_rec.CARD_FEES_CODE                  := v_pre_mig_CARD_FEES_rec.CARD_FEES_CODE;--Code frais
        v_mig_card_fees_rec.description                     := TRIM('FRAIS_'|| TRIM(SUBSTR(v_pre_mig_CARD_FEES_rec.description , 1, 23)) ) ;
        v_mig_card_fees_rec.abrv_description                := SUBSTR(trim(v_pre_mig_CARD_FEES_rec.description),1,12)  ;--abrv_description frais
        v_mig_card_fees_rec.bank_code                       := p_bank_code                                        ;
        v_mig_card_fees_rec.STATUS                          := 'N'                                                ;
        v_mig_card_fees_rec.card_fees_billing_evt           :=  v_pre_mig_CARD_FEES_rec.card_fees_billing_evt    ;
        v_mig_card_fees_rec.card_fees_grace_period          := NULL         ;
        v_mig_card_fees_rec.card_fees_billing_date          := 'X'         ;
        v_mig_card_fees_rec.card_fees_billing_period        := v_pre_mig_CARD_FEES_rec.card_fees_billing_period        ;
        v_mig_card_fees_rec.number_of_year                  := NULL               ;
        v_mig_card_fees_rec.currency_code                   := p_currency_code                ;
        v_mig_card_fees_rec.subscription_amount             := v_pre_mig_CARD_FEES_rec.subscription_amount          ;
       v_mig_card_fees_rec.fees_amount_first                := v_pre_mig_CARD_FEES_rec.fees_amount_first        ;
        v_mig_card_fees_rec.fees_amount_renew               := v_pre_mig_CARD_FEES_rec.fees_amount_first        ;
        v_mig_card_fees_rec.subsequent_renewal_fees         := v_pre_mig_CARD_FEES_rec.fees_amount_first        ;
        v_mig_card_fees_rec.promotion_fees_amount           := '0'           ;
        v_mig_card_fees_rec.damaged_replacement_fees        := v_pre_mig_CARD_FEES_rec.damaged_replacement_fees        ;
        v_mig_card_fees_rec.erroneous_replacement_fees      := v_pre_mig_CARD_FEES_rec.damaged_replacement_fees        ;
        v_mig_card_fees_rec.lost_replacement_fees           := v_pre_mig_CARD_FEES_rec.damaged_replacement_fees            ;
        v_mig_card_fees_rec.stolen_replacement_fees         := v_pre_mig_CARD_FEES_rec.damaged_replacement_fees      ;
        v_mig_card_fees_rec.countrefeit_replacement_fees    := v_pre_mig_CARD_FEES_rec.damaged_replacement_fees     ;
        v_mig_card_fees_rec.emergency_replacement_fees      := v_pre_mig_CARD_FEES_rec.damaged_replacement_fees     ;
        v_mig_card_fees_rec.pin_replacement_fees            := v_pre_mig_CARD_FEES_rec.pin_replacement_fees     ;
        v_mig_card_fees_rec.other_replacement_fees          := v_pre_mig_CARD_FEES_rec.damaged_replacement_fees     ;
        v_mig_card_fees_rec.other_fees_1_indicator          := 'I'         ;
        v_mig_card_fees_rec.plastic_fees                    := '0'                   ;
        v_mig_card_fees_rec.plastic_fees_indicator          := 'I'          ;
        v_mig_card_fees_rec.photo_fees                      := '0'                      ;
        v_mig_card_fees_rec.photo_fees_indicator            := 'I'            ;
        v_mig_card_fees_rec.promotion_starting_date         := NULL        ;
        v_mig_card_fees_rec.promotion_ending_date           := NULL       ;
        v_mig_card_fees_rec.other_fees_1                    := NULL      ;
        v_mig_card_fees_rec.other_fees_2                    := NULL      ;
        v_mig_card_fees_rec.other_fees_2_indicator          := NULL      ;
        v_mig_card_fees_rec.other_fees_3                    := NULL      ;
        v_mig_card_fees_rec.other_fees_3_indicator          := NULL      ;
        v_mig_card_fees_rec.other_fees_4                    := NULL      ;
        v_mig_card_fees_rec.other_fees_4_indicator          := NULL      ;

         INSERT INTO   st_mig_CARD_FEES VALUES v_mig_card_fees_rec;
    END LOOP;
    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_CARD_FEES_PARAMETERS;




--------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_SERVICE_PROD_PARAM             (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_SERVICES_NAME_rec               st_mig_SERVICES_NAME%ROWTYPE :=    NULL;
v_desc_product                        st_pre_bin_range_plastic_prod.description%TYPE;

CURSOR cur_Service_PROD IS
    SELECT  *
    FROM      st_pre_service_PROD
    where  product_code IS NOT NULL
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_SERVICE_PROD_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_service_prod_rec  IN  CUR_SERVICE_PROD
    LOOP

        BEGIN
            SELECT description
            INTO v_desc_product
            FROM   st_pre_bin_range_plastic_prod
            WHERE product_code =v_service_prod_rec.product_code;

            v_mig_services_name_rec.bank_code                                 := p_bank_code;
            v_mig_services_name_rec.SERVICES_SETUP_INDEX                      := 'S'||TRIM(v_service_prod_rec.product_code);
            v_mig_services_name_rec.abrv_wording                              := 'Service_'||substr(TRIM(v_desc_product),1,8);
            v_mig_services_name_rec.wording                                   := 'Service_'||substr(TRIM(v_desc_product),1,20);

            INSERT INTO   st_mig_SERVICES_NAME VALUES v_mig_services_name_rec;
       END;
    END LOOP;
    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_SERVICE_PROD_PARAM;



FUNCTION    LOAD_SERVICE_SETUP_PARAM            (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_SERVICES_SETUP_rec              st_mig_SERVICES_SETUP%ROWTYPE :=   NULL;
v_desc_product                        st_pre_bin_range_plastic_prod.description%TYPE;
v_sequence_id                       P7_SERVICES_SETUP.sequence_id%Type;

CURSOR CUR_SERVICE_PROD IS
    SELECT  *
    FROM      st_pre_service_PROD
    where  product_code is not null
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_SERVICE_SETUP_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    SELECT P7_SERVICES_SETUP_x.NEXTVAL
        INTO v_sequence_id
        FROM dual;

    FOR v_service_prod_rec  IN  CUR_SERVICE_PROD
    LOOP
        SELECT description
        into v_desc_product
        from   st_pre_bin_range_plastic_prod
        where product_code =v_Service_PROD_rec.product_code;

        v_mig_services_setup_rec.bank_code                                  := p_bank_code;
        v_mig_services_setup_rec.SERVICE_SETUP_INDEX                        := 'S'||TRIM(v_service_prod_rec.product_code);
        v_mig_services_setup_rec.discrimination_flag                        := 'Y';
--ACC VERIFICATION
               v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='51';
                v_mig_services_setup_rec.abrv_wording                       :='ACC VERIFICATION';
                v_mig_services_setup_rec.wording                            :='ACC VERIFICATION';

                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;

--RETRAIT
        IF v_service_prod_rec.retrait IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='01';
                v_mig_services_setup_rec.abrv_wording                       :='RETRAIT';
                v_mig_services_setup_rec.wording                            :='RETRAIT';

                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;
--Achat
        IF v_service_prod_rec.Achat IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='00';
                v_mig_services_setup_rec.abrv_wording                       :='PAIEMENT';
                v_mig_services_setup_rec.wording                            :='PAIEMENT';
                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;

--Cash advance
        IF v_service_prod_rec.advance IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='17';
                v_mig_services_setup_rec.abrv_wording                       :='CASH ADVANCE';
                v_mig_services_setup_rec.wording                            :='CASH ADVANCE';
                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;
--E-COMMERCE
        IF v_service_prod_rec.ecommerce IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='90';
                v_mig_services_setup_rec.abrv_wording                       :='E-COMMERCE';
                v_mig_services_setup_rec.wording                            :='E-COMMERCE';
                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;
--OCT
        IF v_service_prod_rec.transfert IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='40';
                v_mig_services_setup_rec.abrv_wording                       :='TRANSFER REQUEST';
                v_mig_services_setup_rec.wording                            :='TRANSFER REQUEST';
                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;

--QUASI CASH
        IF v_service_prod_rec.quasicash IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='11';
                v_mig_services_setup_rec.abrv_wording                       :='QUASI CASH';
                v_mig_services_setup_rec.wording                            :='QUASI CASH';
                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;
--DEMANDE DE SOLDE
        IF v_service_prod_rec.solde IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='31';
                v_mig_services_setup_rec.abrv_wording                       :='SOLDE DEBIT';
                v_mig_services_setup_rec.wording                            :='SOLDE DEBIT';
                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;
--DDEM.RELEVE DEBIT
        IF v_service_prod_rec.releve IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='38';
                v_mig_services_setup_rec.abrv_wording                       :='DEM.RELEVE DEBIT';
                v_mig_services_setup_rec.wording                            :='DEM.RELEVE DEBIT';
                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;
--PIN CHANGE
        IF v_service_prod_rec.pinchange IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='91';
                v_mig_services_setup_rec.abrv_wording                       :='PIN CHANGE';
                v_mig_services_setup_rec.wording                            :='PIN CHANGE';
                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;

--REFUND
        IF v_service_prod_rec.refund IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='20';
                v_mig_services_setup_rec.abrv_wording                       :='REFUND';
                v_mig_services_setup_rec.wording                            :='REFUND';
                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;
--MONEY SEND
        IF v_service_prod_rec.moneysend IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='28';
                v_mig_services_setup_rec.abrv_wording                       :='MONEY SEND';
                v_mig_services_setup_rec.wording                            :='MONEY SEND';
                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;
--BILL PAYMENT
        IF v_service_prod_rec.billpayment IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='50';
                v_mig_services_setup_rec.abrv_wording                       :='BILL PAYMENT';
                v_mig_services_setup_rec.wording                            :='BILL PAYMENT';
                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;

--ORIGINAL CREDIT
        IF v_service_prod_rec.ORIGINAL IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='26';
                v_mig_services_setup_rec.abrv_wording                       :='ORIGINAL CREDIT';
                v_mig_services_setup_rec.wording                            :='ORIGINAL CREDIT';
                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;

--Authentication request
        IF v_service_prod_rec.Authentication IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='30';
                v_mig_services_setup_rec.abrv_wording                       :='Authen req';
                v_mig_services_setup_rec.wording                            :='Authentication request';
                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;

--Cash back
        IF v_service_prod_rec.cashback IS NOT NULL
            THEN
                v_mig_services_setup_rec.sequence_id                        := v_sequence_id;
                v_mig_services_setup_rec.processing_code                    :='09';
                v_mig_services_setup_rec.abrv_wording                       :='Cash back';
                v_mig_services_setup_rec.wording                            :='Cash back';
                INSERT INTO   st_mig_SERVICES_SETUP VALUES v_mig_services_setup_rec;
                v_sequence_id:= v_sequence_id+1;
        END IF;
    END LOOP;
    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_SERVICE_SETUP_PARAM;


--------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_P7_limits_PARAMETERS           (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_P7_limits_rec                 P7_limits%ROWTYPE :=    NULL;
v_index                                p7_sa_limits_setup.limit_index%TYPE;

CURSOR CUR_LIMIT_STAND IS
    SELECT  *
    FROM      st_pre_service_PROD
    where  product_code is not null
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_P7_limits_PARAMETERS';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_P7_limits_rec   IN  cur_limit_stand
    LOOP
        v_index:= 'L'||TRIM(v_P7_limits_rec.product_code);



        INSERT INTO   st_mig_P7_LIMITS VALUES(p_bank_code,v_index,'LIMIT  ','LIMIT  ',p_currency_code,'N',NULL,NULL,3,'N',NULL,NULL,3,'MGR_DEBIT',TO_DATE('2024-06-12 22:06:13', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);
------
    END LOOP;
    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_P7_limits_PARAMETERS;


--------------------------------------
FUNCTION    LOAD_LIMIT_STAND_PARAM              (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is

Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_sa_limits_setup_rec             st_mig_SA_LIMITS_SETUP%ROWTYPE :=  NULL;
v_index                                p7_sa_limits_setup.limit_index%TYPE;
v_desc_product                        st_pre_bin_range_plastic_prod.description%TYPE;

CURSOR CUR_LIMIT_STAND IS
    SELECT  *
    FROM      st_pre_limit_stand
    WHERE  product_code IS NOT NULL
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_LIMIT_STAND_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_limit_stand_rec   IN  cur_limit_stand
    LOOP
        SELECT  description
        INTO    v_desc_product
        FROM      st_pre_bin_range_plastic_prod
        where product_code =SUBSTR(v_limit_stand_rec.product_code,2,4);


        v_mig_sa_limits_setup_rec.bank_code                                 := p_bank_code;
        v_mig_sa_limits_setup_rec.limit_index                               :=TRIM(v_limit_stand_rec.product_code);
        v_mig_sa_limits_setup_rec.limits_id                                 := TRIM(v_limit_stand_rec.limits_id );
        v_index                                                             :=  TRIM(v_limit_stand_rec.product_code);



    IF        v_mig_sa_limits_setup_rec.limits_id ='1'
        THEN
        v_mig_sa_limits_setup_rec.wording                                   := 'RET_'||SUBSTR(TRIM(v_desc_product),1,24);
        v_mig_sa_limits_setup_rec.abrv_wording                              := 'RET_'||SUBSTR(TRIM(v_desc_product),1,12);
    ELSIF  v_mig_sa_limits_setup_rec.limits_id ='2'
        THEN
        v_mig_sa_limits_setup_rec.wording                                   := 'PUR_'||SUBSTR(TRIM(v_desc_product),1,24);
        v_mig_sa_limits_setup_rec.abrv_wording                              := 'PUR_'||SUBSTR(TRIM(v_desc_product),1,12);
    ELSIF  v_mig_sa_limits_setup_rec.limits_id ='3'
        THEN
        v_mig_sa_limits_setup_rec.wording                                   := 'CAV_'||SUBSTR(TRIM(v_desc_product),1,24);
        v_mig_sa_limits_setup_rec.abrv_wording                              := 'CAV_'||SUBSTR(TRIM(v_desc_product),1,12);
    ELSIF  v_mig_sa_limits_setup_rec.limits_id ='4'
        THEN
        v_mig_sa_limits_setup_rec.wording                                   := 'QCA_'||SUBSTR(TRIM(v_desc_product),1,24);
        v_mig_sa_limits_setup_rec.abrv_wording                              := 'QCA_'||SUBSTR(TRIM(v_desc_product),1,12);
    ELSIF  v_mig_sa_limits_setup_rec.limits_id ='9'
        THEN
        v_mig_sa_limits_setup_rec.wording                                   := 'ECO_'||SUBSTR(TRIM(v_desc_product),1,24);
        v_mig_sa_limits_setup_rec.abrv_wording                              := 'ECO_'||SUBSTR(TRIM(v_desc_product),1,12);
    ELSIF  v_mig_sa_limits_setup_rec.limits_id ='10'
        THEN
        v_mig_sa_limits_setup_rec.wording                                   := 'DEF_'||SUBSTR(TRIM(v_desc_product),1,24);
        v_mig_sa_limits_setup_rec.abrv_wording                              := 'DEF_'||SUBSTR(TRIM(v_desc_product),1,12);

    END IF;


        v_mig_sa_limits_setup_rec.abrv_wording                              := SUBSTR(TRIM(v_desc_product),1,16);
        v_mig_sa_limits_setup_rec.currency_code                             := p_currency_code;
        v_mig_sa_limits_setup_rec.host_scenario_processing                  :='R';

        IF  v_limit_stand_rec.daily_total_amnt  IS NULL
        AND     v_limit_stand_rec.weekly_total_amnt IS NULL
        AND     v_limit_stand_rec.monthly_total_amnt IS NULL
        THEN
            v_env_info_trace.user_message   :=  'ERREUR PAS DE LIMITES PARAMÉTRÉE!!';
            PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
            RETURN (declaration_cst.ERROR);
        END IF;
        -------------------------------------------------------------------------- MONTHLY   -------------------------------------------------------------
        IF  v_limit_stand_rec.daily_total_amnt  IS NULL
        AND v_limit_stand_rec.weekly_total_amnt IS NULL
        AND v_limit_stand_rec.monthly_total_amnt IS NOT NULL
        THEN
            v_mig_sa_limits_setup_rec.per1_opt                                  :='C' ;
            v_mig_sa_limits_setup_rec.per1_type                                 :='M' ;
            v_mig_sa_limits_setup_rec.per1_value                                :='1';
            v_mig_sa_limits_setup_rec.per1_day_of                               :='1' ;
            v_mig_sa_limits_setup_rec.nb_periods                                :='1' ;
                    -----online------
            v_mig_sa_limits_setup_rec.on_per1_onus_amnt                         :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt)  ,'999999999')                 ;
            v_mig_sa_limits_setup_rec.on_per1_onus_nbr                          :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per1_nat_amnt                          :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt)     ,'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_nat_nbr                           :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per1_internat_amnt                     :=NVL(TRIM(v_limit_stand_rec.monthly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_internat_nbr                      :=NVL(TRIM(v_limit_stand_rec.monthly_int_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per1_tot_amnt                          :=NVL(TRIM(v_limit_stand_rec.monthly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_tot_nbr                           :=NVL(TRIM(v_limit_stand_rec.monthly_total_nbr),'999')                   ;
                --------delegation------
            v_mig_sa_limits_setup_rec.off_per1_onus_amnt                        :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_onus_nbr                         :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per1_nat_amnt                         :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_nat_nbr                          :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per1_internat_amnt                    :=NVL(TRIM(v_limit_stand_rec.monthly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_internat_nbr                     :=NVL(TRIM(v_limit_stand_rec.monthly_int_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per1_tot_amnt                         :=NVL(TRIM(v_limit_stand_rec.monthly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_tot_nbr                          :=NVL(TRIM(v_limit_stand_rec.monthly_total_nbr),'999')                   ;

        END IF;
        -------------------------------------------------------------------------- WEEKLY   -------------------------------------------------------------
        IF  v_limit_stand_rec.daily_total_amnt  IS NULL
        AND     v_limit_stand_rec.weekly_total_amnt IS NOT NULL
        AND     v_limit_stand_rec.monthly_total_amnt IS NULL
        THEN
            v_mig_sa_limits_setup_rec.per1_opt                                  :='C' ;
            v_mig_sa_limits_setup_rec.per1_type                                 :='W' ;
            v_mig_sa_limits_setup_rec.per1_value                                :='1' ;
            v_mig_sa_limits_setup_rec.per1_day_of                               :='1' ;
            v_mig_sa_limits_setup_rec.nb_periods                                :='1' ;
            -----online------
            v_mig_sa_limits_setup_rec.on_per1_onus_amnt                         :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_onus_nbr                          :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per1_nat_amnt                          :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_nat_nbr                           :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per1_internat_amnt                     :=NVL(TRIM(v_limit_stand_rec.weekly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_internat_nbr                      :=NVL(TRIM(v_limit_stand_rec.weekly_int_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per1_tot_amnt                          :=NVL(TRIM(v_limit_stand_rec.weekly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_tot_nbr                           :=NVL(TRIM(v_limit_stand_rec.weekly_total_nbr),'999')                   ;
            --------delegation------
            v_mig_sa_limits_setup_rec.off_per1_onus_amnt                        :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_onus_nbr                         :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per1_nat_amnt                         :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_nat_nbr                          :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per1_internat_amnt                    :=NVL(TRIM(v_limit_stand_rec.weekly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_internat_nbr                     :=NVL(TRIM(v_limit_stand_rec.weekly_int_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per1_tot_amnt                         :=NVL(TRIM(v_limit_stand_rec.weekly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_tot_nbr                          :=NVL(TRIM(v_limit_stand_rec.weekly_total_nbr),'999')                   ;
        END IF;
    ----------------------------------------------------------------------WEEKLY et MONTHLY   -------------------------------------------------------------
        IF  v_limit_stand_rec.daily_total_amnt  IS NULL
        AND v_limit_stand_rec.weekly_total_amnt IS NOT NULL
        AND v_limit_stand_rec.monthly_total_amnt IS NOT NULL
        THEN
            v_mig_sa_limits_setup_rec.per1_opt                                  :='C' ;
            v_mig_sa_limits_setup_rec.per1_type                                 :='W' ;
            v_mig_sa_limits_setup_rec.per1_value                                :='1' ;
            v_mig_sa_limits_setup_rec.per1_day_of                               :='1' ;
            v_mig_sa_limits_setup_rec.per2_opt                                  :='C' ;
            v_mig_sa_limits_setup_rec.per2_type                                 :='M' ;
            v_mig_sa_limits_setup_rec.per2_value                                :='1';
            v_mig_sa_limits_setup_rec.per2_day_of                               :='1' ;
            v_mig_sa_limits_setup_rec.nb_periods                                :='2' ;
                    -----online------
            v_mig_sa_limits_setup_rec.on_per1_onus_amnt                         :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_onus_nbr                          :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per1_nat_amnt                          :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_nat_nbr                           :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per1_internat_amnt                     :=NVL(TRIM(v_limit_stand_rec.weekly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_internat_nbr                      :=NVL(TRIM(v_limit_stand_rec.weekly_int_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per1_tot_amnt                          :=NVL(TRIM(v_limit_stand_rec.weekly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_tot_nbr                           :=NVL(TRIM(v_limit_stand_rec.weekly_total_nbr),'999')                   ;
            v_mig_sa_limits_setup_rec.on_per2_onus_amnt                         :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_onus_nbr                          :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per2_nat_amnt                          :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_nat_nbr                           :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per2_internat_amnt                     :=NVL(TRIM(v_limit_stand_rec.monthly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_internat_nbr                      :=NVL(TRIM(v_limit_stand_rec.monthly_int_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per2_tot_amnt                          :=NVL(TRIM(v_limit_stand_rec.monthly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_tot_nbr                           :=NVL(TRIM(v_limit_stand_rec.monthly_total_nbr),'999')                   ;
                --------delegation------
            v_mig_sa_limits_setup_rec.off_per1_onus_amnt                        :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_onus_nbr                         :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per1_nat_amnt                         :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_nat_nbr                          :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per1_internat_amnt                    :=NVL(TRIM(v_limit_stand_rec.weekly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_internat_nbr                     :=NVL(TRIM(v_limit_stand_rec.weekly_int_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per1_tot_amnt                         :=NVL(TRIM(v_limit_stand_rec.weekly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_tot_nbr                          :=NVL(TRIM(v_limit_stand_rec.weekly_total_nbr),'999')                   ;
            v_mig_sa_limits_setup_rec.off_per2_onus_amnt                        :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_onus_nbr                         :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per2_nat_amnt                         :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_nat_nbr                          :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per2_internat_amnt                    :=NVL(TRIM(v_limit_stand_rec.monthly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_internat_nbr                     :=NVL(TRIM(v_limit_stand_rec.monthly_int_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per2_tot_amnt                         :=NVL(TRIM(v_limit_stand_rec.monthly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_tot_nbr                          :=NVL(TRIM(v_limit_stand_rec.monthly_total_nbr),'999')                   ;
        END IF;
    --------------------------------------------------------------------DAILY   -------------------------------------------------------------

        IF  v_limit_stand_rec.DAILY_TOTAL_AMNT  IS NOT NULL
        AND     v_limit_stand_rec.WEEKLY_TOTAL_AMNT IS  NULL
        AND     v_limit_stand_rec.MONTHLY_TOTAL_AMNT IS  NULL
        THEN
            v_mig_sa_limits_setup_rec.per1_opt                                  :='C' ;
            v_mig_sa_limits_setup_rec.per1_type                                 :='D' ;
            v_mig_sa_limits_setup_rec.nb_periods                                :='1' ;
            v_mig_sa_limits_setup_rec.per1_value                                :='1' ;
            v_mig_sa_limits_setup_rec.per1_day_of                               :='1' ;
            -----online------
            v_mig_sa_limits_setup_rec.on_per1_onus_amnt                         :=NVL(TRIM(v_limit_stand_rec.daily_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_onus_nbr                          :=NVL(TRIM(v_limit_stand_rec.daily_dom_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.on_per1_nat_amnt                          :=NVL(TRIM(v_limit_stand_rec.daily_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_nat_nbr                           :=NVL(TRIM(v_limit_stand_rec.daily_dom_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.on_per1_internat_amnt                     :=NVL(TRIM(v_limit_stand_rec.daily_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_internat_nbr                      :=NVL(TRIM(v_limit_stand_rec.daily_int_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.on_per1_tot_amnt                          :=NVL(TRIM(v_limit_stand_rec.daily_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_tot_nbr                           :=NVL(TRIM(v_limit_stand_rec.daily_total_nbr),'999')                     ;
        --------DELEGATION------
            v_mig_sa_limits_setup_rec.OFF_per1_onus_amnt                        :=NVL(TRIM(v_limit_stand_rec.DAILY_DOM_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.OFF_per1_onus_nbr                         :=NVL(TRIM(v_limit_stand_rec.DAILY_DOM_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.OFF_per1_nat_amnt                         :=NVL(TRIM(v_limit_stand_rec.DAILY_DOM_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.OFF_per1_nat_nbr                          :=NVL(TRIM(v_limit_stand_rec.DAILY_DOM_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.OFF_per1_internat_amnt                    :=NVL(TRIM(v_limit_stand_rec.DAILY_INT_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.OFF_per1_internat_nbr                     :=NVL(TRIM(v_limit_stand_rec.DAILY_INT_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.OFF_per1_tot_amnt                         :=NVL(TRIM(v_limit_stand_rec.DAILY_TOTAL_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.OFF_per1_tot_nbr                          :=NVL(TRIM(v_limit_stand_rec.DAILY_TOTAL_nbr),'999')                     ;
        ------
        END IF;
        --------------------------------------------------------------------DAILY et monthly  -------------------------------------------------------------
        IF  v_limit_stand_rec.daily_total_amnt  IS NOT NULL
        AND     v_limit_stand_rec.weekly_total_amnt IS  NULL
        AND     v_limit_stand_rec.monthly_total_amnt IS NOT NULL
        THEN
            v_mig_sa_limits_setup_rec.per1_opt                                  :='C' ;
            v_mig_sa_limits_setup_rec.per1_type                                 :='D' ;
            v_mig_sa_limits_setup_rec.per2_opt                                  :='C' ;
            v_mig_sa_limits_setup_rec.per2_type                                 :='M' ;
            v_mig_sa_limits_setup_rec.per2_value                                :='1';
            v_mig_sa_limits_setup_rec.per2_day_of                               :='1' ;
            v_mig_sa_limits_setup_rec.nb_periods                                :='2' ;
            v_mig_sa_limits_setup_rec.per1_value                                :='1' ;
            v_mig_sa_limits_setup_rec.per1_day_of                               :='1' ;
                -----online------
            v_mig_sa_limits_setup_rec.on_per1_onus_amnt                         :=NVL(TRIM(v_limit_stand_rec.daily_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_onus_nbr                          :=NVL(TRIM(v_limit_stand_rec.daily_dom_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.on_per1_nat_amnt                          :=NVL(TRIM(v_limit_stand_rec.daily_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_nat_nbr                           :=NVL(TRIM(v_limit_stand_rec.daily_dom_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.on_per1_internat_amnt                     :=NVL(TRIM(v_limit_stand_rec.daily_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_internat_nbr                      :=NVL(TRIM(v_limit_stand_rec.daily_int_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.on_per1_tot_amnt                          :=NVL(TRIM(v_limit_stand_rec.daily_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_tot_nbr                           :=NVL(TRIM(v_limit_stand_rec.daily_total_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per2_onus_amnt                         :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_onus_nbr                          :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per2_nat_amnt                          :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_nat_nbr                           :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per2_internat_amnt                     :=NVL(TRIM(v_limit_stand_rec.monthly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_internat_nbr                      :=NVL(TRIM(v_limit_stand_rec.monthly_int_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per2_tot_amnt                          :=NVL(TRIM(v_limit_stand_rec.monthly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_tot_nbr                           :=NVL(TRIM(v_limit_stand_rec.monthly_total_nbr),'999')                   ;
            --------DELEGATION------
            v_mig_sa_limits_setup_rec.off_per1_onus_amnt                        :=NVL(TRIM(v_limit_stand_rec.daily_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_onus_nbr                         :=NVL(TRIM(v_limit_stand_rec.daily_dom_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.off_per1_nat_amnt                         :=NVL(TRIM(v_limit_stand_rec.daily_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_nat_nbr                          :=NVL(TRIM(v_limit_stand_rec.daily_dom_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.off_per1_internat_amnt                    :=NVL(TRIM(v_limit_stand_rec.daily_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_internat_nbr                     :=NVL(TRIM(v_limit_stand_rec.daily_int_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.off_per1_tot_amnt                         :=NVL(TRIM(v_limit_stand_rec.daily_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_tot_nbr                          :=NVL(TRIM(v_limit_stand_rec.daily_total_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per2_onus_amnt                        :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_onus_nbr                         :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per2_nat_amnt                         :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_nat_nbr                          :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per2_internat_amnt                    :=NVL(TRIM(v_limit_stand_rec.monthly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_internat_nbr                     :=NVL(TRIM(v_limit_stand_rec.monthly_int_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per2_tot_amnt                         :=NVL(TRIM(v_limit_stand_rec.monthly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_tot_nbr                          :=NVL(TRIM(v_limit_stand_rec.monthly_total_nbr),'999')                   ;
        END IF;
 --------------------------------------------------------------------DAILY et WEEKLY  -------------------------------------------------------------
        IF  v_limit_stand_rec.daily_total_amnt  IS NOT NULL
        AND     v_limit_stand_rec.weekly_total_amnt IS NOT NULL
        AND     v_limit_stand_rec.monthly_total_amnt IS  NULL
        THEN
            v_mig_sa_limits_setup_rec.per1_value                                :='1' ;
            v_mig_sa_limits_setup_rec.per1_day_of                               :='1' ;
            v_mig_sa_limits_setup_rec.per1_opt                                  :='C' ;
            v_mig_sa_limits_setup_rec.per1_type                                 :='D' ;
            v_mig_sa_limits_setup_rec.per2_opt                                  :='C' ;
            v_mig_sa_limits_setup_rec.per2_type                                 :='W' ;
            v_mig_sa_limits_setup_rec.per2_value                                :='1' ;
            v_mig_sa_limits_setup_rec.per2_day_of                               :='1' ;
            v_mig_sa_limits_setup_rec.nb_periods                                :='2' ;
                -----online------
            v_mig_sa_limits_setup_rec.on_per1_onus_amnt                         :=NVL(TRIM(v_limit_stand_rec.daily_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_onus_nbr                          :=NVL(TRIM(v_limit_stand_rec.daily_dom_nbr),'999')                      ;
            v_mig_sa_limits_setup_rec.on_per1_nat_amnt                          :=NVL(TRIM(v_limit_stand_rec.daily_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_nat_nbr                           :=NVL(TRIM(v_limit_stand_rec.daily_dom_nbr),'999')                      ;
            v_mig_sa_limits_setup_rec.on_per1_internat_amnt                     :=NVL(TRIM(v_limit_stand_rec.daily_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_internat_nbr                      :=NVL(TRIM(v_limit_stand_rec.daily_int_nbr),'999')                      ;
            v_mig_sa_limits_setup_rec.on_per1_tot_amnt                          :=NVL(TRIM(v_limit_stand_rec.daily_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_tot_nbr                           :=NVL(TRIM(v_limit_stand_rec.daily_total_nbr),'999')                    ;
            v_mig_sa_limits_setup_rec.on_per2_onus_amnt                         :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_onus_nbr                          :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per2_nat_amnt                          :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_nat_nbr                           :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per2_internat_amnt                     :=NVL(TRIM(v_limit_stand_rec.weekly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_internat_nbr                      :=NVL(TRIM(v_limit_stand_rec.weekly_int_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per2_tot_amnt                          :=NVL(TRIM(v_limit_stand_rec.weekly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_tot_nbr                           :=NVL(TRIM(v_limit_stand_rec.weekly_total_nbr),'999')                   ;
        --------DELEGATION------
            v_mig_sa_limits_setup_rec.off_per1_onus_amnt                        :=NVL(TRIM(v_limit_stand_rec.daily_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_onus_nbr                         :=NVL(TRIM(v_limit_stand_rec.daily_dom_nbr),'999')                      ;
            v_mig_sa_limits_setup_rec.off_per1_nat_amnt                         :=NVL(TRIM(v_limit_stand_rec.daily_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_nat_nbr                          :=NVL(TRIM(v_limit_stand_rec.daily_dom_nbr),'999')                      ;
            v_mig_sa_limits_setup_rec.off_per1_internat_amnt                    :=NVL(TRIM(v_limit_stand_rec.daily_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_internat_nbr                     :=NVL(TRIM(v_limit_stand_rec.daily_int_nbr),'999')                      ;
            v_mig_sa_limits_setup_rec.off_per1_tot_amnt                         :=NVL(TRIM(v_limit_stand_rec.daily_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_tot_nbr                          :=NVL(TRIM(v_limit_stand_rec.daily_total_nbr),'999')                    ;
            v_mig_sa_limits_setup_rec.off_per2_onus_amnt                        :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_onus_nbr                         :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per2_nat_amnt                         :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_nat_nbr                          :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per2_internat_amnt                    :=NVL(TRIM(v_limit_stand_rec.weekly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_internat_nbr                     :=NVL(TRIM(v_limit_stand_rec.weekly_int_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per2_tot_amnt                         :=NVL(TRIM(v_limit_stand_rec.weekly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_tot_nbr                          :=NVL(TRIM(v_limit_stand_rec.weekly_total_nbr),'999')                   ;
        END IF;
 --------------------------------------------------------------------DAILY , WEEKLY et monthly -------------------------------------------------------------
        IF  v_limit_stand_rec.DAILY_TOTAL_AMNT  IS NOT NULL
        AND     v_limit_stand_rec.WEEKLY_TOTAL_AMNT IS NOT NULL
        AND     v_limit_stand_rec.MONTHLY_TOTAL_AMNT IS NOT NULL
        THEN
            v_mig_sa_limits_setup_rec.per1_value                                :='1' ;
            v_mig_sa_limits_setup_rec.per1_day_of                               :='1' ;
            v_mig_sa_limits_setup_rec.per1_opt                                  :='C' ;
            v_mig_sa_limits_setup_rec.per1_type                                 :='D' ;
            v_mig_sa_limits_setup_rec.per2_opt                                  :='C' ;
            v_mig_sa_limits_setup_rec.per2_type                                 :='W' ;
            v_mig_sa_limits_setup_rec.per2_value                                :='1' ;
            v_mig_sa_limits_setup_rec.per2_day_of                               :='1' ;
            v_mig_sa_limits_setup_rec.per3_opt                                  :='C' ;
            v_mig_sa_limits_setup_rec.per3_type                                 :='M' ;
            v_mig_sa_limits_setup_rec.per3_value                                :='1';
            v_mig_sa_limits_setup_rec.per3_day_of                               :='1' ;
            v_mig_sa_limits_setup_rec.nb_periods                                :='3' ;
            -----online------
            v_mig_sa_limits_setup_rec.on_per1_onus_amnt                         :=NVL(TRIM(v_limit_stand_rec.daily_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_onus_nbr                          :=NVL(TRIM(v_limit_stand_rec.daily_dom_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.on_per1_nat_amnt                          :=NVL(TRIM(v_limit_stand_rec.daily_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_nat_nbr                           :=NVL(TRIM(v_limit_stand_rec.daily_dom_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.on_per1_internat_amnt                     :=NVL(TRIM(v_limit_stand_rec.daily_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_internat_nbr                      :=NVL(TRIM(v_limit_stand_rec.daily_int_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.on_per1_tot_amnt                          :=NVL(TRIM(v_limit_stand_rec.daily_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per1_tot_nbr                           :=NVL(TRIM(v_limit_stand_rec.daily_total_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per2_onus_amnt                         :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_onus_nbr                          :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                      ;
            v_mig_sa_limits_setup_rec.on_per2_nat_amnt                          :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_nat_nbr                           :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                      ;
            v_mig_sa_limits_setup_rec.on_per2_internat_amnt                     :=NVL(TRIM(v_limit_stand_rec.weekly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_internat_nbr                      :=NVL(TRIM(v_limit_stand_rec.weekly_int_nbr),'999')                      ;
            v_mig_sa_limits_setup_rec.on_per2_tot_amnt                          :=NVL(TRIM(v_limit_stand_rec.weekly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per2_tot_nbr                           :=NVL(TRIM(v_limit_stand_rec.weekly_total_nbr),'999')                    ;
            v_mig_sa_limits_setup_rec.on_per3_onus_amnt                         :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per3_onus_nbr                          :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per3_nat_amnt                          :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per3_nat_nbr                           :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per3_internat_amnt                     :=NVL(TRIM(v_limit_stand_rec.monthly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per3_internat_nbr                      :=NVL(TRIM(v_limit_stand_rec.monthly_int_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.on_per3_tot_amnt                          :=NVL(TRIM(v_limit_stand_rec.monthly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.on_per3_tot_nbr                           :=NVL(TRIM(v_limit_stand_rec.monthly_total_nbr),'999')                   ;
        --------DELEGATION------                                                                                                             ;
            v_mig_sa_limits_setup_rec.off_per1_onus_amnt                        :=NVL(TRIM(v_limit_stand_rec.daily_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_onus_nbr                         :=NVL(TRIM(v_limit_stand_rec.daily_dom_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.off_per1_nat_amnt                         :=NVL(TRIM(v_limit_stand_rec.daily_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_nat_nbr                          :=NVL(TRIM(v_limit_stand_rec.daily_dom_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.off_per1_internat_amnt                    :=NVL(TRIM(v_limit_stand_rec.daily_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_internat_nbr                     :=NVL(TRIM(v_limit_stand_rec.daily_int_nbr),'999')                       ;
            v_mig_sa_limits_setup_rec.off_per1_tot_amnt                         :=NVL(TRIM(v_limit_stand_rec.daily_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per1_tot_nbr                          :=NVL(TRIM(v_limit_stand_rec.daily_total_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per2_onus_amnt                        :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_onus_nbr                         :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                      ;
            v_mig_sa_limits_setup_rec.off_per2_nat_amnt                         :=NVL(TRIM(v_limit_stand_rec.weekly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_nat_nbr                          :=NVL(TRIM(v_limit_stand_rec.weekly_dom_nbr),'999')                      ;
            v_mig_sa_limits_setup_rec.off_per2_internat_amnt                    :=NVL(TRIM(v_limit_stand_rec.weekly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_internat_nbr                     :=NVL(TRIM(v_limit_stand_rec.weekly_int_nbr),'999')                      ;
            v_mig_sa_limits_setup_rec.off_per2_tot_amnt                         :=NVL(TRIM(v_limit_stand_rec.weekly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per2_tot_nbr                          :=NVL(TRIM(v_limit_stand_rec.weekly_total_nbr),'999')                    ;
            v_mig_sa_limits_setup_rec.off_per3_onus_amnt                        :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per3_onus_nbr                         :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per3_nat_amnt                         :=NVL(TRIM(v_limit_stand_rec.monthly_dom_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per3_nat_nbr                          :=NVL(TRIM(v_limit_stand_rec.monthly_dom_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per3_internat_amnt                    :=NVL(TRIM(v_limit_stand_rec.monthly_int_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per3_internat_nbr                     :=NVL(TRIM(v_limit_stand_rec.monthly_int_nbr),'999')                     ;
            v_mig_sa_limits_setup_rec.off_per3_tot_amnt                         :=NVL(TRIM(v_limit_stand_rec.monthly_total_amnt),'999999999') ;
            v_mig_sa_limits_setup_rec.off_per3_tot_nbr                          :=NVL(TRIM(v_limit_stand_rec.monthly_total_nbr),'999')                   ;

        END IF;

        INSERT INTO   st_mig_SA_LIMITS_SETUP VALUES v_mig_sa_limits_setup_rec;
       ---  ----------------------------------------
    END LOOP;
    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_LIMIT_STAND_PARAM;

--------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_SA_LIMITS_SETUP_PARAM          (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_spec_trans_limits_rec           st_mig_SPEC_TRANS_LIMITS%ROWTYPE :=    NULL;
v_sequence                          P7_SPEC_TRANS_LIMITS.seq_number%TYPE :='0';

CURSOR cur_spec_limits_setup IS
    SELECT  *
    FROM      st_pre_limit_stand
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_SA_LIMITS_SETUP_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    SELECT NVL(MAX(SEQ_NUMBER),'0') + 1
    INTO v_sequence
    FROM P7_SPEC_TRANS_LIMITS;

    FOR v_spec_limits_setup_rec   IN  cur_spec_limits_setup
    LOOP
        v_mig_spec_trans_limits_rec.seq_number                                          := v_sequence ;
        v_mig_spec_trans_limits_rec.bank_code                                           := p_bank_code;
        v_mig_spec_trans_limits_rec.limit_index                                         := TRIM(v_spec_limits_setup_rec.product_code);
        v_mig_spec_trans_limits_rec.limits_id                                           := TRIM(v_spec_limits_setup_rec.limits_id);
        v_mig_spec_trans_limits_rec.currency_code                                       := p_CURRENCY_CODE;
        v_mig_spec_trans_limits_rec.min_amount_per_transaction                          := v_spec_limits_setup_rec.MIN_AMOUNT_PER_TRANSACTION;
        v_mig_spec_trans_limits_rec.max_amount_per_transaction                          := v_spec_limits_setup_rec.MAX_AMOUNT_PER_TRANSACTION;

        IF   v_spec_limits_setup_rec.limits_id ='1'
        THEN
            v_mig_spec_trans_limits_rec.wording                                     := 'RETRAIT';
            v_mig_spec_trans_limits_rec.processing_code                             := '01';
            v_mig_spec_trans_limits_rec.mcc_group                                   :=NULL;
            v_mig_spec_trans_limits_rec.card_present                                := 'N';
            v_mig_spec_trans_limits_rec.card_entry_mode                                := 'E';

            INSERT INTO   st_mig_SPEC_TRANS_LIMITS VALUES v_mig_spec_trans_limits_rec;


            v_sequence:= v_sequence +1;

        ELSIF v_spec_limits_setup_rec.limits_id ='2'
        THEN
            v_mig_spec_trans_limits_rec.wording                                     := 'PURCHASE';
            v_mig_spec_trans_limits_rec.processing_code                             := '00';
            v_mig_spec_trans_limits_rec.mcc_group                                   :=NULL;
            v_mig_spec_trans_limits_rec.card_present                                := NULL;
            v_mig_spec_trans_limits_rec.card_entry_mode                                := NULL;

            INSERT INTO   st_mig_SPEC_TRANS_LIMITS VALUES v_mig_spec_trans_limits_rec;


            v_sequence:= v_sequence +1;


        ELSIF v_spec_limits_setup_rec.limits_id ='3'
        THEN
            v_mig_spec_trans_limits_rec.wording                                     := 'Cash advance';
            v_mig_spec_trans_limits_rec.processing_code                             := '17';
            v_mig_spec_trans_limits_rec.mcc_group                                   :=NULL;
            v_mig_spec_trans_limits_rec.card_present                                := NULL;
            v_mig_spec_trans_limits_rec.card_entry_mode                                := NULL;

            INSERT INTO   st_mig_SPEC_TRANS_LIMITS VALUES v_mig_spec_trans_limits_rec;


            v_sequence:= v_sequence +1;

        ELSIF v_spec_limits_setup_rec.limits_id ='4'
        THEN
            v_mig_spec_trans_limits_rec.wording                                     := 'QUASI CASH';
            v_mig_spec_trans_limits_rec.processing_code                             := '11';
            v_mig_spec_trans_limits_rec.mcc_group                                   :=NULL;
            v_mig_spec_trans_limits_rec.card_present                                := NULL;
            v_mig_spec_trans_limits_rec.card_entry_mode                                := NULL;

            INSERT INTO   st_mig_SPEC_TRANS_LIMITS VALUES v_mig_spec_trans_limits_rec;


            v_sequence:= v_sequence +1;
        ELSIF v_spec_limits_setup_rec.limits_id ='9'
        THEN
            v_mig_spec_trans_limits_rec.wording                                     := 'ECOM';
            v_mig_spec_trans_limits_rec.processing_code                             := '00';
            v_mig_spec_trans_limits_rec.mcc_group                                   :=NULL;
            v_mig_spec_trans_limits_rec.card_present                                := 'N';
            v_mig_spec_trans_limits_rec.card_entry_mode                                := 'E';

            INSERT INTO   st_mig_SPEC_TRANS_LIMITS VALUES v_mig_spec_trans_limits_rec;


            v_sequence:= v_sequence +1;

        ELSIF v_spec_limits_setup_rec.limits_id ='10'
        THEN
            v_mig_spec_trans_limits_rec.wording                                     := 'DEF LIMIT';
            v_mig_spec_trans_limits_rec.processing_code                             := NULL;
            v_mig_spec_trans_limits_rec.mcc_group                                   :=NULL;
            v_mig_spec_trans_limits_rec.card_present                                := NULL;

            INSERT INTO   st_mig_SPEC_TRANS_LIMITS VALUES v_mig_spec_trans_limits_rec;

            v_sequence:= v_sequence +1;


        END IF;
    END LOOP;

    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_SA_LIMITS_SETUP_PARAM;
------------------------------------------------------------------------------------------------------------------------------------

FUNCTION    LOAD_EMV_LIMIT_SETUP           (  p_business_date           IN                  DATE,
                                                p_bank_code             IN                  BANK.bank_code%TYPE,
                                                p_currency_code         IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_emv_limit_setup_rec             st_mig_EMV_LIMIT_SETUP%ROWTYPE :=  NULL;





CURSOR CUR_LIMIT_STAND IS
    SELECT  *
    FROM      st_pre_service_PROD
    where  product_code is not null
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_P7_limits_PARAMETERS';
    v_env_info_trace.lang           :=  global_vars.LANG;






        FOR v_P7_limits_rec   IN  cur_limit_stand
        LOOP

        v_mig_emv_limit_setup_rec.bank_code                                 := p_bank_code;
        v_mig_emv_limit_setup_rec.limit_index                               := 'L'||TRIM(v_P7_limits_rec.product_code)  ;
        v_mig_emv_limit_setup_rec.abrv_wording                              := 'EMVLS';
        v_mig_emv_limit_setup_rec.wording                                   := 'EMV Limit Setup';
        v_mig_emv_limit_setup_rec.currency_code1                            := p_currency_code;
        v_mig_emv_limit_setup_rec.currency_code2                            := p_currency_code;
        v_mig_emv_limit_setup_rec.consecutive_trx_limit_int_c               := '0';
        v_mig_emv_limit_setup_rec.consecutive_trx_limit_int_t               := '0';
        v_mig_emv_limit_setup_rec.cumul_trx_amount_limit_dom                := '0';
        v_mig_emv_limit_setup_rec.cumul_trx_amount_limit_tot                := '0';
        v_mig_emv_limit_setup_rec.cumul_trx_amount_limit_dual               := '0';
        v_mig_emv_limit_setup_rec.application_trx_counter                   := '0';
        v_mig_emv_limit_setup_rec.currency_conversion_factor                := '1';
        v_mig_emv_limit_setup_rec.limit_off_after_trx_onl                   := '0';
        v_mig_emv_limit_setup_rec.limit_per_offline_trx                     := '0';
        v_mig_emv_limit_setup_rec.max_nbr_offline_trx_intl                  := NULL;
        v_mig_emv_limit_setup_rec.consec_trx_limit_int_up_cc                := '1';

        INSERT INTO   st_mig_EMV_LIMIT_SETUP VALUES v_mig_emv_limit_setup_rec;

        END LOOP;


    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_EMV_LIMIT_SETUP;
-----------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_EMV_KEYS_ASSIG_PARAM           (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_emv_keys_assignment_rec       EMV_KEYS_ASSIGNMENT%ROWTYPE :=  NULL;
v_sequence_id                       PLS_INTEGER := 0;

CURSOR CUR_BIN_RANGE_PLASTIC_PROD IS
    SELECT  *
    FROM      st_pre_bin_range_plastic_prod
    WHERE  product_code IS NOT NULL
    and substr(service_code,1,1) not in ('1','5','7') --SAQ19062020
    ORDER BY product_code;
BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_EMV_KEYS_ASSIG_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    SELECT  NVL(MAX(sequence_id),0) + 1
    INTO    v_sequence_id
    FROM    EMV_KEYS_ASSIGNMENT;

    FOR v_bin_range_plastic_prod_rec    IN  cur_BIN_RANGE_PLASTIC_PROD
    LOOP

        v_mig_emv_keys_assignment_rec.sequence_id                                   :=  v_sequence_id;
        v_mig_emv_keys_assignment_rec.bank_code                                     :=  p_bank_code;
        v_mig_emv_keys_assignment_rec.card_number                                   :=  NULL    ;
        v_mig_emv_keys_assignment_rec.issuer_bin                                    :=  NULL ;
        v_mig_emv_keys_assignment_rec.product_code                                  :=  TRIM(v_bin_range_plastic_prod_rec.product_code)  ;
        v_mig_emv_keys_assignment_rec.icc_application_code                          :=  '0001';
        v_mig_emv_keys_assignment_rec.public_key_id                                 :=  NULL;
        v_mig_emv_keys_assignment_rec.kmc_seq                                       :=  '001';
        v_mig_emv_keys_assignment_rec.kek_seq                                       :=  '001';
        v_mig_emv_keys_assignment_rec.mdk_seq                                       :=  '001';
        v_mig_emv_keys_assignment_rec.mac_seq                                       :=  '001';
        v_mig_emv_keys_assignment_rec.enc_seq                                       :=  '001';

        INSERT INTO   st_mig_EMV_KEYS_ASSIGNMENT VALUES v_mig_emv_keys_assignment_rec;
        v_sequence_id:=v_sequence_id+1;

    END LOOP;

    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_EMV_KEYS_ASSIG_PARAM;


-----------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_EMV_ICC_APPL_DEF           (  p_business_date                IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_emv_icc_appl_def_rec           EMV_KEYS_ASSIGNMENT%ROWTYPE :=  NULL;
v_sequence_id                       PLS_INTEGER := 0;
P_product_code                        card_product.product_code%TYPE;

CURSOR CUR_BIN_RANGE_PLASTIC_PROD IS
    SELECT  *
    FROM      st_pre_bin_range_plastic_prod
    WHERE  product_code IS NOT NULL
    and substr(service_code,1,1) not in ('1','5','7')
    ORDER BY product_code;
BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_EMV_ICC_APPL_DEF';
    v_env_info_trace.lang           :=  global_vars.LANG;



    FOR v_bin_range_plastic_prod_rec    IN  cur_BIN_RANGE_PLASTIC_PROD
    LOOP
        P_product_code :=  TRIM(v_bin_range_plastic_prod_rec.product_code);



    INSERT INTO   st_mig_emv_icc_appl_definition
    VALUES(p_bank_code,'0001',P_product_code,'VSDC',NULL,'Y','Y','Y',NULL,NULL,NULL,NULL,'00820000','00820000',NULL,NULL,NULL,NULL,NULL,NULL,'MGR',NULL,NULL,NULL);



    END LOOP;

    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_EMV_ICC_APPL_DEF;


-----------------------------------------------------------------------------------------------------------------------------------
FUNCTION    RELOAD_RESOURCES_PARAM           (  p_business_date                 IN                  DATE,
                                                p_bank_wording               IN                     BANK.bank_name%TYPE,
                                                            p_bank_code               IN                  BANK.bank_code%TYPE)

                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_resource_wording                        resources.wording%TYPE;
v_resource_id                         resources.resource_id%TYPE;
v_resource_code                     resources.resource_code%TYPE;
v_node_id                           resources.node_id%TYPE;
v_desc                              resources.wording%TYPE;
v_start_shl                         resources.pris_start_script_name%TYPE;
v_stop_shl                          resources.pris_stop_script_name%TYPE;
v_trace                                resources.pris_log_file_name%TYPE;
v_params                            RESOURCES_PARAM.params%TYPE;
v_index                               PLS_INTEGER := 0;

CURSOR CUR_RESOURCES_PROD IS
    SELECT  *
    FROM      st_pre_resources where bank_code = p_bank_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'RELOAD_RESOURCES_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

        SELECT  MAX(TO_NUMBER(NVL(sequence_id,0)))+ 1
        INTO    v_index
        FROM    p7_RESOURCES_SERVICES  ;

    FOR v_resources_rec    IN  CUR_RESOURCES_PROD
    LOOP

    v_index:=v_index+1;

    ------------------------------------------
    IF v_resources_rec.resource_wording = 'VISA_BASE1'
    THEN

    select  LPAD( MAX(NVL(RESOURCE_id,0))+ 1,6,'0')
    into v_resource_id from resources where resource_code ='11'   ;
        v_resource_id               := v_resource_id  ;
        v_resource_code             := '11' ;
        v_node_id                   :=  '0001' ;
        v_desc                      :=  substr(p_bank_code,1,3)  || '_base1_01'    ;
        v_start_shl                 :=  'start_base1'||substr(p_bank_code ,1,3)|| '_01'   ;
        v_stop_shl                  :=  'stop_base1'||substr(p_bank_code ,1,3)|| '_01'   ;
        v_trace                        := 'BASE1_'||substr(p_bank_code ,1,3)|| '_01.TRC000'  ;
        v_params                    :=  'B01006244211B02006244211B03003834B04003GRCB05002CMR06008CAMEROONB07001NB08001NB09001NB10001N'  ;


    INSERT INTO    st_Architecture_Convergence
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,'VISA_BASE1');

    INSERT INTO resources
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,p_bank_wording,'PRIS','H','N','N','BASE1','$BIN',v_start_shl,'$SHL',v_stop_shl,'$SHL','Y','Y','03','01','001','000002',NULL,NULL,NULL,NULL,'Y','S',NULL,'10.100.76.18','6661',NULL,NULL,v_trace,4096,0,999,'6',5,2,5000,2000,30,NULL,'T',0,0,0,'N','OFF','009447392585594220054010',944739,1,'N',NULL,NULL,'0001','F','01','Manager','Manager',NULL,NULL,NULL,NULL,'76275000','76275','076','170',NULL,NULL,NULL,'X','INITIAL_LOAD',TO_DATE('2023-07-17 06:19:32', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    INSERT INTO p7_RESOURCES_SERVICES
    VALUES(v_index,v_resource_id,NULL,NULL,NULL,NULL,NULL,NULL,NULL,v_desc,p_bank_wording,'Y','POWERCARD',TO_DATE('2023-07-17 06:19:33', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    INSERT INTO P7_BANK_RESOURCE_PARAM
    VALUES(v_resource_id,p_bank_code,1,'N','N',TO_DATE('2021-10-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),2,'Y','Y','Y','Y','Y','Y','POWERCARD',TO_DATE('2021-10-08 19:45:30', 'YYYY-MM-DD HH24:MI:SS'),'POWERCARD',TO_DATE('2021-10-08 19:02:05', 'YYYY-MM-DD HH24:MI:SS'));

    INSERT INTO RESOURCES_PARAM
    VALUES(v_resource_id,v_params,'POWERCARD',TO_DATE('2024-07-08 19:05:03', 'YYYY-MM-DD HH24:MI:SS'),'mgrUser',TO_DATE('2024-07-08 16:48:59', 'YYYY-MM-DD HH24:MI:SS'));
            v_resource_id:=LPAD( (NVL(v_resource_id+1,0)),6,'0');
        v_node_id :=  '0002' ;
        v_desc                      :=  substr(p_bank_code,1,3)  ||'_base1_02'    ;
        v_start_shl                 :=  'start_base1'||substr(p_bank_code ,1,3)|| '_02'   ;
        v_stop_shl                  :=  'stop_base1'||substr(p_bank_code ,1,3)|| '_02'   ;
        v_trace                        := 'BASE1_'||substr(p_bank_code ,1,3)|| '_02.TRC000'  ;
        v_index                        :=v_index+1;

    INSERT INTO    st_Architecture_Convergence
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,'VISA_BASE1');

    INSERT INTO resources
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,p_bank_wording,'PRIS','H','N','N','BASE1','$BIN',v_start_shl,'$SHL',v_stop_shl,'$SHL','Y','Y','03','01','001','000002',NULL,NULL,NULL,NULL,'Y','S',NULL,'10.100.76.18','6661',NULL,NULL,v_trace,4096,0,999,'6',5,2,5000,2000,30,NULL,'T',0,0,0,'N','OFF','009447392585594220054010',944739,1,'N',NULL,NULL,'0001','F','01','Manager','Manager',NULL,NULL,NULL,NULL,'76275000','76275','076','170',NULL,NULL,NULL,'X','INITIAL_LOAD',TO_DATE('2023-07-17 06:19:32', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    INSERT INTO p7_RESOURCES_SERVICES
    VALUES(v_index,v_resource_id,NULL,NULL,NULL,NULL,NULL,NULL,NULL,v_desc,p_bank_wording,'Y','POWERCARD',TO_DATE('2023-07-17 06:19:33', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    INSERT INTO P7_BANK_RESOURCE_PARAM
    VALUES(v_resource_id,p_bank_code,1,'N','N',TO_DATE('2021-10-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),2,'Y','Y','Y','Y','Y','Y','POWERCARD',TO_DATE('2021-10-08 19:45:30', 'YYYY-MM-DD HH24:MI:SS'),'POWERCARD',TO_DATE('2021-10-08 19:02:05', 'YYYY-MM-DD HH24:MI:SS'));

    INSERT INTO RESOURCES_PARAM
    VALUES(v_resource_id,v_params,'POWERCARD',TO_DATE('2024-07-08 19:05:03', 'YYYY-MM-DD HH24:MI:SS'),'mgrUser',TO_DATE('2024-07-08 16:48:59', 'YYYY-MM-DD HH24:MI:SS'));

    END IF;
    ------------------------------------------
    IF v_resources_rec.resource_wording = 'VISA_SMS'
    THEN

    select  LPAD( max(NVL(RESOURCE_id,0))+ 1,6,'0')
    into v_resource_id from resources where resource_code ='13' ;
        v_resource_id               :=  v_resource_id  ;
        v_resource_code             := '13' ;
        v_node_id                   :=  '0001' ;
         v_desc                      :=  substr(p_bank_code,1,3)  || '_SMS_01'    ;
        v_start_shl                 :=  'start_SMS'||substr(p_bank_code ,1,3)|| '_01'   ;
        v_stop_shl                  :=  'stop_SMS'||substr(p_bank_code ,1,3)|| '_01'   ;
        v_trace                        := 'SMS_'||substr(p_bank_code ,1,3)|| '_01.TRC000'  ;
        v_params                    :=  'B01006244211B02006244211B03003834B04003GRCB05002CMR06008CAMEROONB07001NB08001NB09001NB10001N'  ;
     v_index                        :=v_index+1;

    INSERT INTO    st_Architecture_Convergence
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,'VISA_SMS');
        INSERT INTO resources
        VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,p_bank_wording,'PRIS','H','N','N','SMS','$BIN',v_start_shl,'$SHL',v_stop_shl,'$SHL','Y','Y','03','01','001','000002',NULL,NULL,NULL,NULL,'Y','S',NULL,'10.100.76.18','6661',NULL,NULL,v_trace,4096,0,999,'6',5,2,5000,2000,30,NULL,'T',0,0,0,'N','OFF','009447392585594220054010',944739,1,'N',NULL,NULL,'0001','F','01','Manager','Manager',NULL,NULL,NULL,NULL,'76275000','76275','076','170',NULL,NULL,NULL,'X','INITIAL_LOAD',TO_DATE('2023-07-17 06:19:32', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);
        v_resource_id:=v_resource_id;

    INSERT INTO p7_RESOURCES_SERVICES
    VALUES(v_index,v_resource_id,NULL,NULL,NULL,NULL,NULL,NULL,NULL,v_desc,p_bank_wording,'Y','POWERCARD',TO_DATE('2023-07-17 06:19:33', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    INSERT INTO P7_BANK_RESOURCE_PARAM
    VALUES(v_resource_id,p_bank_code,1,'N','N',TO_DATE('2021-10-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),2,'Y','Y','Y','Y','Y','Y','POWERCARD',TO_DATE('2021-10-08 19:45:30', 'YYYY-MM-DD HH24:MI:SS'),'POWERCARD',TO_DATE('2021-10-08 19:02:05', 'YYYY-MM-DD HH24:MI:SS'));

    INSERT INTO RESOURCES_PARAM
    VALUES(v_resource_id,v_params,'POWERCARD',TO_DATE('2024-07-08 19:05:03', 'YYYY-MM-DD HH24:MI:SS'),'mgrUser',TO_DATE('2024-07-08 16:48:59', 'YYYY-MM-DD HH24:MI:SS'));

         v_resource_id:=LPAD( (NVL(v_resource_id+1,0)),6,'0');
        v_node_id:=  '0002';
         v_desc                      :=  substr(p_bank_code,1,3)  || '_SMS_02'    ;
        v_start_shl                 :=  'start_SMS'||substr(p_bank_code ,1,3)|| '_02'   ;
        v_stop_shl                  :=  'stop_SMS'||substr(p_bank_code ,1,3)|| '_02'   ;
        v_trace                        := 'SMS_'||substr(p_bank_code ,1,3)|| '_02.TRC000'  ;
            v_index:=v_index+1;

    INSERT INTO    st_Architecture_Convergence
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,'VISA_SMS');

    INSERT INTO resources
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,p_bank_wording,'PRIS','H','N','N','SMS','$BIN',v_start_shl,'$SHL',v_stop_shl,'$SHL','Y','Y','03','01','001','000002',NULL,NULL,NULL,NULL,'Y','S',NULL,'10.100.76.18','6661',NULL,NULL,v_trace,4096,0,999,'6',5,2,5000,2000,30,NULL,'T',0,0,0,'N','OFF','009447392585594220054010',944739,1,'N',NULL,NULL,'0001','F','01','Manager','Manager',NULL,NULL,NULL,NULL,'76275000','76275','076','170',NULL,NULL,NULL,'X','INITIAL_LOAD',TO_DATE('2023-07-17 06:19:32', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    INSERT INTO p7_RESOURCES_SERVICES
    VALUES(v_index,v_resource_id,NULL,NULL,NULL,NULL,NULL,NULL,NULL,v_desc,p_bank_wording,'Y','POWERCARD',TO_DATE('2023-07-17 06:19:33', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    INSERT INTO P7_BANK_RESOURCE_PARAM
    VALUES(v_resource_id,p_bank_code,1,'N','N',TO_DATE('2021-10-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),2,'Y','Y','Y','Y','Y','Y','POWERCARD',TO_DATE('2021-10-08 19:45:30', 'YYYY-MM-DD HH24:MI:SS'),'POWERCARD',TO_DATE('2021-10-08 19:02:05', 'YYYY-MM-DD HH24:MI:SS'));

    INSERT INTO RESOURCES_PARAM
    VALUES(v_resource_id,v_params,'POWERCARD',TO_DATE('2024-07-08 19:05:03', 'YYYY-MM-DD HH24:MI:SS'),'mgrUser',TO_DATE('2024-07-08 16:48:59', 'YYYY-MM-DD HH24:MI:SS'));
    END IF;
------------------------------------------


    IF v_resources_rec.resource_wording = 'SID'
    THEN

    select  LPAD( MAX(NVL(RESOURCE_id,0))+ 1,6,'0')
    into v_resource_id from resources where resource_code ='03' ;
        v_resource_id               :=  v_resource_id ;
        v_resource_code             := '03' ;
        v_node_id                   :=  '0001' ;
         v_desc                      :=  substr(p_bank_code,1,3)  || '_SID_01'    ;
        v_start_shl                 :=  'start_SID'||substr(p_bank_code ,1,3)|| '_01'   ;
        v_stop_shl                  :=  'stop_SID'||substr(p_bank_code ,1,3)|| '_01'   ;
        v_trace                        := 'SID_'||substr(p_bank_code ,1,3)|| '_01.TRC000'  ;
        v_params                    :=  'B01006244211B02006244211B03003834B04003GRCB05002CMR06008CAMEROONB07001NB08001NB09001NB10001N'  ;


    INSERT INTO    st_Architecture_Convergence
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,'SID');

        INSERT INTO resources
        VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,p_bank_wording,'PRIS','H','N','N','SID_BANK','$BIN',v_start_shl,'$SHL',v_stop_shl,'$SHL','Y','Y','03','01','001',p_bank_code ,NULL,NULL,NULL,NULL,'Y','S',NULL,'10.100.76.18','6661',NULL,NULL,v_trace,4096,0,999,'6',5,2,5000,2000,30,NULL,'T',0,0,0,'N','OFF','009447392585594220054010',944739,1,'N',NULL,NULL,'0001','F','01','Manager','Manager',NULL,NULL,NULL,NULL,'76275000','76275','076','170',NULL,NULL,NULL,'X','INITIAL_LOAD',TO_DATE('2023-07-17 06:19:32', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    INSERT INTO p7_RESOURCES_SERVICES
    VALUES(v_index,v_resource_id,NULL,NULL,NULL,NULL,NULL,NULL,NULL,v_desc,p_bank_wording,'Y','POWERCARD',TO_DATE('2023-07-17 06:19:33', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    INSERT INTO P7_BANK_RESOURCE_PARAM
    VALUES(v_resource_id,p_bank_code,1,'N','N',TO_DATE('2021-10-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),2,'Y','Y','Y','Y','Y','Y','POWERCARD',TO_DATE('2021-10-08 19:45:30', 'YYYY-MM-DD HH24:MI:SS'),'POWERCARD',TO_DATE('2021-10-08 19:02:05', 'YYYY-MM-DD HH24:MI:SS'));

    INSERT INTO RESOURCES_PARAM
    VALUES(v_resource_id,v_params,'POWERCARD',TO_DATE('2024-07-08 19:05:03', 'YYYY-MM-DD HH24:MI:SS'),'mgrUser',TO_DATE('2024-07-08 16:48:59', 'YYYY-MM-DD HH24:MI:SS'));

        v_resource_id:=LPAD( (NVL(v_resource_id+1,0)),6,'0');
     v_node_id:=  '0002';
         v_desc                      :=  substr(p_bank_code,1,3)  || '_SID_02'    ;
        v_start_shl                 :=  'start_SID'||substr(p_bank_code ,1,3)|| '_02'   ;
        v_stop_shl                  :=  'stop_SID'||substr(p_bank_code ,1,3)|| '_02'   ;
        v_trace                        := 'SID_'||substr(p_bank_code ,1,3)|| '_02.TRC000'  ;
            v_index:=v_index+1;
    INSERT INTO    st_Architecture_Convergence
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,'SID');

        INSERT INTO resources
        VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,p_bank_wording,'PRIS','H','N','N','SID_BANK','$BIN',v_start_shl,'$SHL',v_stop_shl,'$SHL','Y','Y','03','01','001',p_bank_code,NULL,NULL,NULL,NULL,'Y','S',NULL,'10.100.76.18','6661',NULL,NULL,v_trace,4096,0,999,'6',5,2,5000,2000,30,NULL,'T',0,0,0,'N','OFF','009447392585594220054010',944739,1,'N',NULL,NULL,'0001','F','01','Manager','Manager',NULL,NULL,NULL,NULL,'76275000','76275','076','170',NULL,NULL,NULL,'X','INITIAL_LOAD',TO_DATE('2023-07-17 06:19:32', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    INSERT INTO p7_RESOURCES_SERVICES
    VALUES(v_index,v_resource_id,NULL,NULL,NULL,NULL,NULL,NULL,NULL,v_desc,p_bank_wording,'Y','POWERCARD',TO_DATE('2023-07-17 06:19:33', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    INSERT INTO P7_BANK_RESOURCE_PARAM
    VALUES(v_resource_id,p_bank_code,1,'N','N',TO_DATE('2021-10-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),2,'Y','Y','Y','Y','Y','Y','POWERCARD',TO_DATE('2021-10-08 19:45:30', 'YYYY-MM-DD HH24:MI:SS'),'POWERCARD',TO_DATE('2021-10-08 19:02:05', 'YYYY-MM-DD HH24:MI:SS'));

    INSERT INTO RESOURCES_PARAM
    VALUES(v_resource_id,v_params,'POWERCARD',TO_DATE('2024-07-08 19:05:03', 'YYYY-MM-DD HH24:MI:SS'),'mgrUser',TO_DATE('2024-07-08 16:48:59', 'YYYY-MM-DD HH24:MI:SS'));
    END IF;
    ------------------------------------------


    IF v_resources_rec.resource_wording = 'HOST_BANK'
    THEN

    select  LPAD( MAX(NVL(RESOURCE_id,0))+ 1,6,'0')
    into v_resource_id from resources where resource_code ='02' ;
        v_resource_id               :=  v_resource_id ;
        v_resource_code             := '02' ;
        v_node_id                   :=  '0001' ;
         v_desc                      :=  substr(p_bank_code,1,3)  || '_HOST_01'    ;
        v_start_shl                 :=  'start_HOST'||substr(p_bank_code ,1,3)|| '_01'   ;
        v_stop_shl                  :=  'stop_HOST'||substr(p_bank_code ,1,3)|| '_01'   ;
        v_trace                        := 'HOST_'||substr(p_bank_code ,1,3)|| '_01.TRC000'  ;

    INSERT INTO    st_Architecture_Convergence
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,'HOST_BANK');


        INSERT INTO resources
        VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,p_bank_wording,'PRIS','H','N','N','SID_BANK','$BIN',v_start_shl,'$SHL',v_stop_shl,'$SHL','Y','Y','03','01','001',p_bank_code ,NULL,NULL,NULL,NULL,'Y','S',NULL,'10.100.76.18','6661',NULL,NULL,v_trace,4096,0,999,'6',5,2,5000,2000,30,NULL,'T',0,0,0,'N','OFF','009447392585594220054010',944739,1,'N',NULL,NULL,'0001','F','01','Manager','Manager',NULL,NULL,NULL,NULL,'76275000','76275','076','170',NULL,NULL,NULL,'X','INITIAL_LOAD',TO_DATE('2023-07-17 06:19:32', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    INSERT INTO p7_RESOURCES_SERVICES
    VALUES(v_index,v_resource_id,NULL,NULL,NULL,NULL,NULL,NULL,NULL,v_desc,p_bank_wording,'Y','POWERCARD',TO_DATE('2023-07-17 06:19:33', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    INSERT INTO P7_BANK_RESOURCE_PARAM
    VALUES(v_resource_id,p_bank_code,1,'N','N',TO_DATE('2021-10-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),2,'Y','Y','Y','Y','Y','Y','POWERCARD',TO_DATE('2021-10-08 19:45:30', 'YYYY-MM-DD HH24:MI:SS'),'POWERCARD',TO_DATE('2021-10-08 19:02:05', 'YYYY-MM-DD HH24:MI:SS'));

    INSERT INTO RESOURCES_PARAM
    VALUES(v_resource_id,v_params,'POWERCARD',TO_DATE('2024-07-08 19:05:03', 'YYYY-MM-DD HH24:MI:SS'),'mgrUser',TO_DATE('2024-07-08 16:48:59', 'YYYY-MM-DD HH24:MI:SS'));
               v_resource_id:=LPAD( (NVL(v_resource_id+1,0)),6,'0');
        v_node_id:=  '0002';
         v_desc                      :=  substr(p_bank_code,1,3)  || '_HOST_02'    ;
        v_start_shl                 :=  'start_HOST'||substr(p_bank_code ,1,3)|| '_02'   ;
        v_stop_shl                  :=  'stop_HOST'||substr(p_bank_code ,1,3)|| '_02'   ;
        v_trace                        := 'HOST_'||substr(p_bank_code ,1,3)|| '_02.TRC000'  ;
            v_index:=v_index+1;
    INSERT INTO    st_Architecture_Convergence
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,'HOST_BANK');

        INSERT INTO resources
        VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,p_bank_wording,'PRIS','H','N','N','SID_BANK','$BIN',v_start_shl,'$SHL',v_stop_shl,'$SHL','Y','Y','03','01','001',p_bank_code,NULL,NULL,NULL,NULL,'Y','S',NULL,'10.100.76.18','6661',NULL,NULL,v_trace,4096,0,999,'6',5,2,5000,2000,30,NULL,'T',0,0,0,'N','OFF','009447392585594220054010',944739,1,'N',NULL,NULL,'0001','F','01','Manager','Manager',NULL,NULL,NULL,NULL,'76275000','76275','076','170',NULL,NULL,NULL,'X','INITIAL_LOAD',TO_DATE('2023-07-17 06:19:32', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    INSERT INTO p7_RESOURCES_SERVICES
    VALUES(v_index,v_resource_id,NULL,NULL,NULL,NULL,NULL,NULL,NULL,v_desc,p_bank_wording,'Y','POWERCARD',TO_DATE('2023-07-17 06:19:33', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    INSERT INTO P7_BANK_RESOURCE_PARAM
    VALUES(v_resource_id,p_bank_code,1,'N','N',TO_DATE('2021-10-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),2,'Y','Y','Y','Y','Y','Y','POWERCARD',TO_DATE('2021-10-08 19:45:30', 'YYYY-MM-DD HH24:MI:SS'),'POWERCARD',TO_DATE('2021-10-08 19:02:05', 'YYYY-MM-DD HH24:MI:SS'));

    INSERT INTO RESOURCES_PARAM
    VALUES(v_resource_id,v_params,'POWERCARD',TO_DATE('2024-07-08 19:05:03', 'YYYY-MM-DD HH24:MI:SS'),'mgrUser',TO_DATE('2024-07-08 16:48:59', 'YYYY-MM-DD HH24:MI:SS'));

    END IF;

    ------------------------------------------


    IF v_resources_rec.resource_wording = 'MCD_MDS'
    THEN

    select  LPAD( MAX(NVL(RESOURCE_id,0))+ 1,6,'0')
    into v_resource_id from resources where resource_code ='22' ;
        v_resource_id               :=  v_resource_id ;
        v_resource_code             := '22' ;
        v_node_id                   :=  '0001' ;
         v_desc                      :=  substr(p_bank_code,1,3)  || '_MDS_01'    ;
        v_start_shl                 :=  'start_MDS'||substr(p_bank_code ,1,3)|| '_01'   ;
        v_stop_shl                  :=  'stop_MDS'||substr(p_bank_code ,1,3)|| '_01'   ;
        v_trace                        := 'MDS_'||substr(p_bank_code ,1,3)|| '_01.TRC000'  ;
     v_index                        :=v_index+1;
    INSERT INTO    st_Architecture_Convergence
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,'MCD_MDS');


        INSERT INTO resources
        VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,p_bank_wording,'PRIS','H','N','N','INT_MDS','$BIN',v_start_shl,'$SHL',v_stop_shl,'$SHL','Y','Y','03','01','001','000003' ,NULL,NULL,NULL,NULL,'Y','S',NULL,'10.100.76.18','6661',NULL,NULL,v_trace,4096,0,999,'6',5,2,5000,2000,30,NULL,'T',0,0,0,'N','OFF','009447392585594220054010',944739,1,'N',NULL,NULL,'0001','F','01','Manager','Manager',NULL,NULL,NULL,NULL,'76275000','76275','076','170',NULL,NULL,NULL,'X','INITIAL_LOAD',TO_DATE('2023-07-17 06:19:32', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    INSERT INTO p7_RESOURCES_SERVICES
    VALUES(v_index,v_resource_id,NULL,NULL,NULL,NULL,NULL,NULL,NULL,v_desc,p_bank_wording,'Y','POWERCARD',TO_DATE('2023-07-17 06:19:33', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    INSERT INTO P7_BANK_RESOURCE_PARAM
    VALUES(v_resource_id,p_bank_code,1,'N','N',TO_DATE('2021-10-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),2,'Y','Y','Y','Y','Y','Y','POWERCARD',TO_DATE('2021-10-08 19:45:30', 'YYYY-MM-DD HH24:MI:SS'),'POWERCARD',TO_DATE('2021-10-08 19:02:05', 'YYYY-MM-DD HH24:MI:SS'));

    INSERT INTO RESOURCES_PARAM
    VALUES(v_resource_id,v_params,'POWERCARD',TO_DATE('2024-07-08 19:05:03', 'YYYY-MM-DD HH24:MI:SS'),'mgrUser',TO_DATE('2024-07-08 16:48:59', 'YYYY-MM-DD HH24:MI:SS'));
               v_resource_id:=LPAD( (NVL(v_resource_id+1,0)),6,'0');
        v_node_id:=  '0002';
         v_desc                      :=  substr(p_bank_code,1,3)  || '_MDS_02'    ;
        v_start_shl                 :=  'start_MDS'||substr(p_bank_code ,1,3)|| '_02'   ;
        v_stop_shl                  :=  'stop_MDS'||substr(p_bank_code ,1,3)|| '_02'   ;
        v_trace                        := 'MDS_'||substr(p_bank_code ,1,3)|| '_02.TRC000'  ;
            v_index:=v_index+1;
    INSERT INTO    st_Architecture_Convergence
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,'MCD_MDS');

        INSERT INTO resources
        VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,p_bank_wording,'PRIS','H','N','N','INT_MDS','$BIN',v_start_shl,'$SHL',v_stop_shl,'$SHL','Y','Y','03','01','001','000003',NULL,NULL,NULL,NULL,'Y','S',NULL,'10.100.76.18','6661',NULL,NULL,v_trace,4096,0,999,'6',5,2,5000,2000,30,NULL,'T',0,0,0,'N','OFF','009447392585594220054010',944739,1,'N',NULL,NULL,'0001','F','01','Manager','Manager',NULL,NULL,NULL,NULL,'76275000','76275','076','170',NULL,NULL,NULL,'X','INITIAL_LOAD',TO_DATE('2023-07-17 06:19:32', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    INSERT INTO p7_RESOURCES_SERVICES
    VALUES(v_index,v_resource_id,NULL,NULL,NULL,NULL,NULL,NULL,NULL,v_desc,p_bank_wording,'Y','POWERCARD',TO_DATE('2023-07-17 06:19:33', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    INSERT INTO P7_BANK_RESOURCE_PARAM
    VALUES(v_resource_id,p_bank_code,1,'N','N',TO_DATE('2021-10-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),2,'Y','Y','Y','Y','Y','Y','POWERCARD',TO_DATE('2021-10-08 19:45:30', 'YYYY-MM-DD HH24:MI:SS'),'POWERCARD',TO_DATE('2021-10-08 19:02:05', 'YYYY-MM-DD HH24:MI:SS'));

    INSERT INTO RESOURCES_PARAM
    VALUES(v_resource_id,v_params,'POWERCARD',TO_DATE('2024-07-08 19:05:03', 'YYYY-MM-DD HH24:MI:SS'),'mgrUser',TO_DATE('2024-07-08 16:48:59', 'YYYY-MM-DD HH24:MI:SS'));

    END IF;

    ------------------------------------------


    IF v_resources_rec.resource_wording = 'MCD_CIS'
    THEN

    select  LPAD( MAX(NVL(RESOURCE_id,0))+ 1,6,'0')
    into v_resource_id from resources where resource_code ='40' ;
        v_resource_id               :=  v_resource_id ;
        v_resource_code             := '40' ;
        v_node_id                   :=  '0001' ;
         v_desc                      :=  substr(p_bank_code,1,3)  || '_CIS_01'    ;
        v_start_shl                 :=  'start_CIS'||substr(p_bank_code ,1,3)|| '_01'   ;
        v_stop_shl                  :=  'stop_CIS'||substr(p_bank_code ,1,3)|| '_01'   ;
        v_trace                        := 'CIS_'||substr(p_bank_code ,1,3)|| '_01.TRC000'  ;
     v_index                        :=v_index+1;
    INSERT INTO    st_Architecture_Convergence
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,'MCD_CIS');


        INSERT INTO resources
        VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,p_bank_wording,'PRIS','H','N','N','CIS','$BIN',v_start_shl,'$SHL',v_stop_shl,'$SHL','Y','Y','03','01','001','000003' ,NULL,NULL,NULL,NULL,'Y','S',NULL,'10.100.76.18','6661',NULL,NULL,v_trace,4096,0,999,'6',5,2,5000,2000,30,NULL,'T',0,0,0,'N','OFF','009447392585594220054010',944739,1,'N',NULL,NULL,'0001','F','01','Manager','Manager',NULL,NULL,NULL,NULL,'76275000','76275','076','170',NULL,NULL,NULL,'X','INITIAL_LOAD',TO_DATE('2023-07-17 06:19:32', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    INSERT INTO p7_RESOURCES_SERVICES
    VALUES(v_index,v_resource_id,NULL,NULL,NULL,NULL,NULL,NULL,NULL,v_desc,p_bank_wording,'Y','POWERCARD',TO_DATE('2023-07-17 06:19:33', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    INSERT INTO P7_BANK_RESOURCE_PARAM
    VALUES(v_resource_id,p_bank_code,1,'N','N',TO_DATE('2021-10-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),2,'Y','Y','Y','Y','Y','Y','POWERCARD',TO_DATE('2021-10-08 19:45:30', 'YYYY-MM-DD HH24:MI:SS'),'POWERCARD',TO_DATE('2021-10-08 19:02:05', 'YYYY-MM-DD HH24:MI:SS'));

    INSERT INTO RESOURCES_PARAM
    VALUES(v_resource_id,v_params,'POWERCARD',TO_DATE('2024-07-08 19:05:03', 'YYYY-MM-DD HH24:MI:SS'),'mgrUser',TO_DATE('2024-07-08 16:48:59', 'YYYY-MM-DD HH24:MI:SS'));
               v_resource_id:=LPAD( (NVL(v_resource_id+1,0)),6,'0');
        v_node_id:=  '0002';
         v_desc                      :=  substr(p_bank_code,1,3)  || '_CIS_02'    ;
        v_start_shl                 :=  'start_CIS'||substr(p_bank_code ,1,3)|| '_02'   ;
        v_stop_shl                  :=  'stop_CIS'||substr(p_bank_code ,1,3)|| '_02'   ;
        v_trace                        := 'CIS_'||substr(p_bank_code ,1,3)|| '_02.TRC000'  ;
            v_index:=v_index+1;
    INSERT INTO    st_Architecture_Convergence
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,'MCD_CIS');

        INSERT INTO resources
        VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,p_bank_wording,'PRIS','H','N','N','CIS','$BIN',v_start_shl,'$SHL',v_stop_shl,'$SHL','Y','Y','03','01','001','000003',NULL,NULL,NULL,NULL,'Y','S',NULL,'10.100.76.18','6661',NULL,NULL,v_trace,4096,0,999,'6',5,2,5000,2000,30,NULL,'T',0,0,0,'N','OFF','009447392585594220054010',944739,1,'N',NULL,NULL,'0001','F','01','Manager','Manager',NULL,NULL,NULL,NULL,'76275000','76275','076','170',NULL,NULL,NULL,'X','INITIAL_LOAD',TO_DATE('2023-07-17 06:19:32', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    INSERT INTO p7_RESOURCES_SERVICES
    VALUES(v_index,v_resource_id,NULL,NULL,NULL,NULL,NULL,NULL,NULL,v_desc,p_bank_wording,'Y','POWERCARD',TO_DATE('2023-07-17 06:19:33', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    INSERT INTO P7_BANK_RESOURCE_PARAM
    VALUES(v_resource_id,p_bank_code,1,'N','N',TO_DATE('2021-10-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),2,'Y','Y','Y','Y','Y','Y','POWERCARD',TO_DATE('2021-10-08 19:45:30', 'YYYY-MM-DD HH24:MI:SS'),'POWERCARD',TO_DATE('2021-10-08 19:02:05', 'YYYY-MM-DD HH24:MI:SS'));

    INSERT INTO RESOURCES_PARAM
    VALUES(v_resource_id,v_params,'POWERCARD',TO_DATE('2024-07-08 19:05:03', 'YYYY-MM-DD HH24:MI:SS'),'mgrUser',TO_DATE('2024-07-08 16:48:59', 'YYYY-MM-DD HH24:MI:SS'));

    END IF;


    ------------------------------------------


    IF v_resources_rec.resource_wording = 'UPI'
    THEN

    select 'CS'|| LPAD( MAX(NVL(SUBSTR(resource_id ,3,6),0))+ 1,4,'0')
    into v_resource_id from resources where resource_code ='CS' ;
        v_resource_id               :=  v_resource_id ;
        v_resource_code             := 'CS' ;
        v_node_id                   :=  '0001' ;
         v_desc                      :=  substr(p_bank_code,1,3)  || '_UPI_01'    ;
        v_start_shl                 :=  'start_UPI'||substr(p_bank_code ,1,3)|| '_01'   ;
        v_stop_shl                  :=  'stop_UPI'||substr(p_bank_code ,1,3)|| '_01'   ;
        v_trace                        := 'UPI_'||substr(p_bank_code ,1,3)|| '_01.TRC000'  ;
     v_index                        :=v_index+1;
    INSERT INTO    st_Architecture_Convergence
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,'UPI');


        INSERT INTO resources
        VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,p_bank_wording,'PRIS','H','N','N','UPI','$BIN',v_start_shl,'$SHL',v_stop_shl,'$SHL','Y','Y','03','01','001','000008' ,NULL,NULL,NULL,NULL,'Y','S',NULL,'10.100.76.18','6661',NULL,NULL,v_trace,4096,0,999,'6',5,2,5000,2000,30,NULL,'T',0,0,0,'N','OFF','009447392585594220054010',944739,1,'N',NULL,NULL,'0001','F','01','Manager','Manager',NULL,NULL,NULL,NULL,'76275000','76275','076','170',NULL,NULL,NULL,'X','INITIAL_LOAD',TO_DATE('2023-07-17 06:19:32', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    INSERT INTO p7_RESOURCES_SERVICES
    VALUES(v_index,v_resource_id,NULL,NULL,NULL,NULL,NULL,NULL,NULL,v_desc,p_bank_wording,'Y','POWERCARD',TO_DATE('2023-07-17 06:19:33', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    INSERT INTO P7_BANK_RESOURCE_PARAM
    VALUES(v_resource_id,p_bank_code,1,'N','N',TO_DATE('2021-10-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),2,'Y','Y','Y','Y','Y','Y','POWERCARD',TO_DATE('2021-10-08 19:45:30', 'YYYY-MM-DD HH24:MI:SS'),'POWERCARD',TO_DATE('2021-10-08 19:02:05', 'YYYY-MM-DD HH24:MI:SS'));

    INSERT INTO RESOURCES_PARAM
    VALUES(v_resource_id,v_params,'POWERCARD',TO_DATE('2024-07-08 19:05:03', 'YYYY-MM-DD HH24:MI:SS'),'mgrUser',TO_DATE('2024-07-08 16:48:59', 'YYYY-MM-DD HH24:MI:SS'));
               v_resource_id:='CS'|| LPAD( (NVL(SUBSTR(v_resource_id ,3,6),0))+ 1,4,'0');
        v_node_id:=  '0002';
         v_desc                      :=  substr(p_bank_code,1,3)  || '_UPI_02'    ;
        v_start_shl                 :=  'start_UPI'||substr(p_bank_code ,1,3)|| '_02'   ;
        v_stop_shl                  :=  'stop_UPI'||substr(p_bank_code ,1,3)|| '_02'   ;
        v_trace                        := 'UPI_'||substr(p_bank_code ,1,3)|| '_02.TRC000'  ;
            v_index:=v_index+1;
    INSERT INTO    st_Architecture_Convergence
    VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,'UPI');

        INSERT INTO resources
        VALUES(v_resource_id,v_resource_code,v_node_id,v_desc,p_bank_wording,'PRIS','H','N','N','UPI','$BIN',v_start_shl,'$SHL',v_stop_shl,'$SHL','Y','Y','03','01','001','000008',NULL,NULL,NULL,NULL,'Y','S',NULL,'10.100.76.18','6661',NULL,NULL,v_trace,4096,0,999,'6',5,2,5000,2000,30,NULL,'T',0,0,0,'N','OFF','009447392585594220054010',944739,1,'N',NULL,NULL,'0001','F','01','Manager','Manager',NULL,NULL,NULL,NULL,'76275000','76275','076','170',NULL,NULL,NULL,'X','INITIAL_LOAD',TO_DATE('2023-07-17 06:19:32', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    INSERT INTO p7_RESOURCES_SERVICES
    VALUES(v_index,v_resource_id,NULL,NULL,NULL,NULL,NULL,NULL,NULL,v_desc,p_bank_wording,'Y','POWERCARD',TO_DATE('2023-07-17 06:19:33', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    INSERT INTO P7_BANK_RESOURCE_PARAM
    VALUES(v_resource_id,p_bank_code,1,'N','N',TO_DATE('2021-10-08 19:00:00', 'YYYY-MM-DD HH24:MI:SS'),2,'Y','Y','Y','Y','Y','Y','POWERCARD',TO_DATE('2021-10-08 19:45:30', 'YYYY-MM-DD HH24:MI:SS'),'POWERCARD',TO_DATE('2021-10-08 19:02:05', 'YYYY-MM-DD HH24:MI:SS'));

    INSERT INTO RESOURCES_PARAM
    VALUES(v_resource_id,v_params,'POWERCARD',TO_DATE('2024-07-08 19:05:03', 'YYYY-MM-DD HH24:MI:SS'),'mgrUser',TO_DATE('2024-07-08 16:48:59', 'YYYY-MM-DD HH24:MI:SS'));


    END IF;

    END LOOP;

    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END RELOAD_RESOURCES_PARAM;


-----------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_branch_PARAMETERS           (  p_business_date                 IN                  DATE,
                                                 p_country_code           IN                  country.country_code%TYPE,
                                                 p_currency_code              IN                  CURRENCY_TABLE.currency_code%TYPE,
                                                 p_bank_code               IN                  BANK.bank_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_branch_code                       branch.branch_code%TYPE;
v_branch_wording                    control_verification_flags.WORDING%TYPE;
v_region_code                       region.region_code%TYPE;
v_region_wording                    control_verification_flags.WORDING%TYPE;
v_city_code                       city.city_code%TYPE;
v_city_wording                    control_verification_flags.WORDING%TYPE;
v_BRANCH_PARAM_rec                   branch%ROWTYPE :=  NULL;

v_sequence_id                       PLS_INTEGER := 0;

CURSOR CUR_BRANCH_PARAM IS
    SELECT  *
    FROM      st_pre_branch
    WHERE   bank_code = p_bank_code  ;
BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_branch_PARAMETERS';
    v_env_info_trace.lang           :=  global_vars.LANG;


    FOR v_BRANCH_PARAM_rec    IN  CUR_BRANCH_PARAM
    LOOP


        v_branch_code                    :=  TRIM(v_BRANCH_PARAM_rec.branch_code)  ;
        v_branch_wording                 :=  TRIM(v_BRANCH_PARAM_rec.branch_wording)  ;
        v_region_code                    :=  TRIM(v_BRANCH_PARAM_rec.region_code)  ;
        v_region_wording                 :=  TRIM(v_BRANCH_PARAM_rec.region_wording)  ;
        v_city_code                      :=  TRIM(v_BRANCH_PARAM_rec.city_code)  ;
        v_city_wording                   :=  TRIM(v_BRANCH_PARAM_rec.city_wording  )  ;


        select count(*)
        into v_sequence_id
         from   st_mig_region
        where region_code =v_region_code;

            IF v_sequence_id='0'
            THEN

                INSERT INTO   st_mig_REGION VALUES(p_country_code,v_region_code,v_region_wording,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,30,NULL,'POWERCARD',NULL,NULL,NULL);
            END IF;
        select count(*)
        into v_sequence_id
         from   st_mig_city
        where city_code =v_city_code;

            IF v_sequence_id='0'
            THEN
            INSERT INTO   st_mig_CITY VALUES(p_country_code,v_city_code,v_city_wording,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'DF','GMT',NULL,NULL,NULL,NULL);
            END IF;

    INSERT INTO   st_mig_BRANCH VALUES(p_bank_code,v_branch_code,v_branch_wording,NULL,'000',NULL,NULL,NULL,NULL,NULL,'Line 1','Line 2',NULL,NULL,NULL,v_city_code,v_region_code,v_region_wording,p_country_code,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,p_currency_code,'A',NULL,NULL,NULL,NULL,v_city_wording,'CONV_AUT',TO_DATE('2023-07-17 06:19:55', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);
    END LOOP;

    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_branch_PARAMETERS;


-----------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_CONTROL_VERIFICATION_PARAM           (  p_business_date                 IN                  DATE,
                                                            p_bank_code               IN                  BANK.bank_code%TYPE,
                                                            p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_index                             control_verification_flags.CONTROL_VERIFICATION_INDEX%TYPE;
v_desc                                 control_verification_flags.WORDING%TYPE;
v_mig_emv_keys_assignment_rec       EMV_KEYS_ASSIGNMENT%ROWTYPE :=  NULL;
v_sequence_id                       PLS_INTEGER := 0;

CURSOR CUR_BIN_RANGE_PLASTIC_PROD IS
    SELECT  *
    FROM      st_pre_bin_range_plastic_prod
    WHERE  product_code IS NOT NULL
    AND bank_code = p_bank_code
     ORDER BY product_code;
BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_CTRL_VERIF_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;


    FOR v_bin_range_plastic_prod_rec    IN  cur_BIN_RANGE_PLASTIC_PROD
    LOOP


        v_index                                 :=  TRIM(v_bin_range_plastic_prod_rec.product_code)  ;
        v_desc                                  :=  TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.description);

   INSERT INTO   st_mig_ctrl_verification_flags
    VALUES(p_bank_code,v_index,v_desc,'N','N','N','N','N','N','N','NCP','N','N','N','N','N','N','N','N',NULL,'N',NULL,NULL,'N','N','N',NULL,'N','N','N',NULL,NULL,NULL,'N','N','N','N','N','N','N','NCP','N','N','N','N','N','N','N','N',NULL,'N',NULL,NULL,'N','N','N','N','N',NULL,3,3,'N',NULL,NULL,NULL,NULL,'NAIHOS',TO_DATE('2023-11-01 10:51:35', 'YYYY-MM-DD HH24:MI:SS'),'PWCRUN',TO_DATE('2024-07-22 12:31:29', 'YYYY-MM-DD HH24:MI:SS'));
    END LOOP;

    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_CONTROL_VERIFICATION_PARAM;




-----------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_CARD_PRODUCT_PARAM             (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_card_product_rec              CARD_PRODUCT%ROWTYPE := NULL;
v_default_fees                      CARD_FEES.card_fees_code%TYPE;

v_network_card_type                 card_type.network_card_type%TYPE;

CURSOR CUR_BIN_RANGE_PLASTIC_PROD IS
    SELECT  *
    FROM      st_pre_bin_range_plastic_prod
    where  product_code IS NOT NULL
    AND bank_code = p_bank_code
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_CARD_PRODUCT_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_BIN_RANGE_PLASTIC_PROD_rec    IN  cur_BIN_RANGE_PLASTIC_PROD
    LOOP




                SELECT network_card_type
                INTO v_network_card_type
                FROM   st_mig_card_type
                WHERE ABRV_WORDING = substr(trim(v_bin_range_plastic_prod_rec.description),1,16)    ;
                v_mig_card_product_rec.initial_status_code                       := 'N';
                v_mig_card_product_rec.initial_status_reason                     := '33';
                v_mig_card_product_rec.old_card_plastic_mng                      := 'R';
                v_mig_card_product_rec.bank_code                                 := p_bank_code;
                v_mig_card_product_rec.product_code                              := TRIM(v_bin_range_plastic_prod_rec.product_code);
                v_mig_card_product_rec.abrv_wording                              := substr(TRIM(v_bin_range_plastic_prod_rec.description),1,16);
                v_mig_card_product_rec.wording                                   := substr(TRIM(v_bin_range_plastic_prod_rec.description),1,32);
                v_mig_card_product_rec.on_us_product_flag                        := 'Y';
                v_mig_card_product_rec.product_type                              := 'DC';
--              v_mig_card_product_rec.network_code                              := '01';
                v_mig_card_product_rec.network_card_type                         := v_network_card_type;
                v_mig_card_product_rec.service_code                              := TRIM(v_bin_range_plastic_prod_rec.service_code);
                v_mig_card_product_rec.services_setup_index                      := 'S'||v_bin_range_plastic_prod_rec.product_code;
                v_mig_card_product_rec.currency_code                             := p_currency_code;
                v_mig_card_product_rec.limits_indexes                            :='L'||v_bin_range_plastic_prod_rec.product_code;
                v_mig_card_product_rec.periodicity_code                          :=NULL;
                v_mig_card_product_rec.enable_card_limits_exception              := 'Y';
                v_mig_card_product_rec.prod_pin_offset_pvv                       := 'PVV';
                v_mig_card_product_rec.prod_cvv1                                 := 'Y';
                v_mig_card_product_rec.prod_cvv2                                 := 'Y';
                v_mig_card_product_rec.prod_ccd                                  := 'N';
                v_mig_card_product_rec.prod_telecode                             := 'N';
                v_mig_card_product_rec.prod_encod_iso_1                          := 'Y';
                v_mig_card_product_rec.prod_encod_iso_2                          := 'Y';
                v_mig_card_product_rec.prod_encod_iso_3                          := 'Y';
                v_mig_card_product_rec.prod_encod_ship                           := 'N';
                v_mig_card_product_rec.card_gen_procedure                        := '00';
                v_mig_card_product_rec.plastic_type                              := TRIM(v_bin_range_plastic_prod_rec.plastic_type);
                v_mig_card_product_rec.delivery_mode                             := 'B';
                v_mig_card_product_rec.delivery_flag                             := 'N';
                v_mig_card_product_rec.replacement_delivery_flag                 := 'N';
                v_mig_card_product_rec.embossing_option                          := 'A';
                v_mig_card_product_rec.renewal_option                            := TRIM(v_bin_range_plastic_prod_rec.renew);--SAQ09062020
                v_mig_card_product_rec.activation_flag                           := 'P';
                v_mig_card_product_rec.replacement_activation_flag               := 'Y';
                v_mig_card_product_rec.delivery_pin_mailer_flag                  := 'PY';
                v_mig_card_product_rec.supplementary_card_exp_flag               := 'N';
                v_mig_card_product_rec.card_carrier_option                       := 'N';--SAQ09062020
                v_mig_card_product_rec.advice_option                             := 'Y';
                v_mig_card_product_rec.advice_renewal_option                     := 'Y';
                v_mig_card_product_rec.pin_management_option                     := 'BC';
                v_mig_card_product_rec.validity_code_first                       := TRIM(v_bin_range_plastic_prod_rec.EXPIRATION);--SAQ06022020
                v_mig_card_product_rec.validity_code_renewal                     := TRIM(v_bin_range_plastic_prod_rec.EXPIRATION);--SAQ06022020
                v_mig_card_product_rec.minimum_validity                          := '0';
                v_mig_card_product_rec.prior_expiry_date                         := TRIM(v_bin_range_plastic_prod_rec.prior_exp);--SAQ09062020
                v_mig_card_product_rec.production_flag                           := 'I';
                v_mig_card_product_rec.card_fees_ind_prim                        :=  TRIM(v_bin_range_plastic_prod_rec.product_code);
                v_mig_card_product_rec.card_fees_ind_sec                         :=  TRIM(v_bin_range_plastic_prod_rec.product_code);
                v_mig_card_product_rec.card_fees_bus_prim                        :=  TRIM(v_bin_range_plastic_prod_rec.product_code);
                v_mig_card_product_rec.card_fees_bus_sec                         :=  TRIM(v_bin_range_plastic_prod_rec.product_code);
                v_mig_card_product_rec.card_fees_stf_prim                        :=  TRIM(v_bin_range_plastic_prod_rec.product_code);
                v_mig_card_product_rec.card_fees_stf_sec                         :=  TRIM(v_bin_range_plastic_prod_rec.product_code);
                v_mig_card_product_rec.settlement_period                         := 'I';
                v_mig_card_product_rec.settlement_period_cash                    := 'I';
                v_mig_card_product_rec.markup_code                               := TRIM(v_bin_range_plastic_prod_rec.product_code);
                v_mig_card_product_rec.default_language_code                     := 'FRE';
                v_mig_card_product_rec.control_verification_index                := TRIM(v_bin_range_plastic_prod_rec.product_code);
                v_mig_card_product_rec.private_tlv_data                          := NULL;
                v_mig_card_product_rec.loy_entity_level_flag                     := 'C';
                v_mig_card_product_rec.loy_auto_enrollment_flag                  := 'A';
                v_mig_card_product_rec.load_trans_activation_flag                := 'N';
                v_mig_card_product_rec.multi_account_flag                        := 'N';
                v_mig_card_product_rec.acs_enrollment_status                     := 'N';
                v_mig_card_product_rec.catalogue_pi_product                     :=  'PAN'||TRIM(v_bin_range_plastic_prod_rec.product_code);
                v_mig_card_product_rec.catalogue_pi_version                :=  '1';
--START SAQ19062020
                IF  substr(v_bin_range_plastic_prod_rec.service_code,1,1) not in ('1','5','7') --SAQ19062020
                    THEN
                v_mig_card_product_rec.icc_application_index                     := '0001';
                END IF;
--END SAQ19062020


                IF      TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='VISA'
                    THEN
                        v_mig_card_product_rec.network_code             :=  '01'    ;

                ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='PRIVATIVE'
                    THEN
                        v_mig_card_product_rec.network_code             :=  '00'    ;
                ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='GIMN'
                    THEN
                        v_mig_card_product_rec.network_code             :=  '21'    ;
                ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='AMEX'
                    THEN
                        v_mig_card_product_rec.network_code             :=  '04'    ;
                ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='MCRD'
                    THEN
                        v_mig_card_product_rec.network_code             :=  '02'    ;
                ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='EUROPAY'
                    THEN
                        v_mig_card_product_rec.network_code             :=  '03'    ;
                ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='TAG-YUP'
                    THEN
                        v_mig_card_product_rec.network_code             :=  '07'    ;
                ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='DINERS'
                    THEN
                        v_mig_card_product_rec.network_code             :=  '05'    ;
                ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='GMAC'
                    THEN
                        v_mig_card_product_rec.network_code             :=  '40'    ;
                ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='TAG-CONNECT'
                    THEN
                        v_mig_card_product_rec.network_code             :=  '09'    ;
                END IF;


        INSERT INTO   st_mig_CARD_PRODUCT VALUES v_mig_card_product_rec;

    END LOOP;
    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_CARD_PRODUCT_PARAM;
-----------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_CARD_RANGE_PARAM               (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_card_range_rec                CARD_RANGE%ROWTYPE :=NULL;
v_network_card_type                 card_type.network_card_type%TYPE;

CURSOR CUR_BIN_RANGE_PLASTIC_PROD IS
    SELECT  *
    FROM      st_pre_bin_range_plastic_prod
    WHERE  product_code is not null
    AND bank_code = p_bank_code
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_CARD_RANGE_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_bin_range_plastic_prod_rec    IN  CUR_BIN_RANGE_PLASTIC_PROD
    LOOP







-----end seq KEYS


        SELECT network_card_type
        INTO v_network_card_type
        FROM   st_mig_card_type
        WHERE ABRV_WORDING = substr(trim(v_bin_range_plastic_prod_rec.description),1,16)    ;


        v_mig_card_range_rec.min_card_range                                 :=TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.tranche_min);
        v_mig_card_range_rec.max_card_range                                 :=TRIM(v_bin_range_plastic_prod_rec.tranche_max);
        v_mig_card_range_rec.issuing_bank_code                              :=P_bank_code;
        v_mig_card_range_rec.issuer_bin                                     :=TRIM(v_bin_range_plastic_prod_rec.bin);
 --       v_mig_card_range_rec.network_code                                   := '01';
        v_mig_card_range_rec.card_number_length_min                         :=length (TRIM(v_bin_range_plastic_prod_rec.tranche_min));
        v_mig_card_range_rec.card_number_length_max                         :=length(TRIM(v_bin_range_plastic_prod_rec.tranche_max));
        v_mig_card_range_rec.card_file_option                               :='N';
        v_mig_card_range_rec.get_product_data_level                         :='N';
        v_mig_card_range_rec.get_card_data_level                            :='N';
        v_mig_card_range_rec.single_product_flag                            :='Y';
        v_mig_card_range_rec.product_code                                   :=TRIM(v_bin_range_plastic_prod_rec.product_code);
        v_mig_card_range_rec.services_setup_index                           :='S'||v_bin_range_plastic_prod_rec.product_code;
        v_mig_card_range_rec.vip_response_translation                       :='1';
        v_mig_card_range_rec.service_code                                   :=TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.service_code);
        v_mig_card_range_rec.currency_code                                  := p_currency_code ;
        v_mig_card_range_rec.limits_indexes                                 :='L'||v_bin_range_plastic_prod_rec.product_code;
        v_mig_card_range_rec.periodicity_code                                 :=NULL;
        v_mig_card_range_rec.network_card_type                              := v_network_card_type;
        v_mig_card_range_rec.primary_pin_key_number                         :='001';--test
        v_mig_card_range_rec.alternate_pin_key_number                       :='001';--test
        v_mig_card_range_rec.start_pin_alternate_key                        :=to_date('6/19/2018 00:00:00','');
        v_mig_card_range_rec.start_cvv_alternate_key                        :=to_date('6/19/2018 00:00:00','');
        v_mig_card_range_rec.exception_cvv_key_valdate                      :=to_date('3/30/2019 23:00:00','');
        v_mig_card_range_rec.pvki                                           :=TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.index_pvk);
        v_mig_card_range_rec.KEY_SET_NUMBER_1                               :='001';
        v_mig_card_range_rec.KEY_SET_NUMBER_2                               :='001';
        v_mig_card_range_rec.primary_cvv_key_number                         :='001';
        v_mig_card_range_rec.pin_retry_max                                  :='3';
        v_mig_card_range_rec.pin_length                                     :='4';
        v_mig_card_range_rec.language_code                                  :='FRE';
        v_mig_card_range_rec.control_verification_index                     :=TRIM(v_bin_range_plastic_prod_rec.product_code);


        IF      TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='VISA'
            THEN
                v_mig_card_range_rec.network_code               :=  '01'    ;

        ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='PRIVATIVE'
            THEN
                v_mig_card_range_rec.network_code               :=  '00'    ;
        ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='GIMN'
            THEN
                v_mig_card_range_rec.network_code               :=  '21'    ;
        ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='AMEX'
            THEN
                v_mig_card_range_rec.network_code               :=  '04'    ;
        ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='MCRD'
            THEN
                v_mig_card_range_rec.network_code               :=  '02'    ;
        ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='EUROPAY'
            THEN
                v_mig_card_range_rec.network_code               :=  '03'    ;
        ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='TAG-YUP'
            THEN
                v_mig_card_range_rec.network_code               :=  '07'    ;
        ELSIF   TRIM(v_BIN_RANGE_PLASTIC_PROD_rec.network) ='DINERS'
            THEN
                v_mig_card_range_rec.network_code               :=  '05'    ;

        END IF;


        INSERT INTO   st_mig_CARD_RANGE VALUES v_mig_card_range_rec;

    END LOOP;

    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_CARD_RANGE_PARAM;



-----------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_RANGE_KEY_PARAM               (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_range_key_rec                card_range_key%ROWTYPE :=NULL;


CURSOR CUR_RANGE_KEY_PROD IS
    SELECT  *
    FROM      st_mig_CARD_RANGE
    WHERE issuing_bank_code = p_bank_code
    ORDER BY min_card_range;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_RANGE_KEY_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_RANGE_KEY_rec    IN  CUR_RANGE_KEY_PROD
    LOOP


-----end seq KEYS



        v_mig_range_key_rec.min_card_range                                     :=TRIM(v_RANGE_KEY_rec.min_card_range);
        v_mig_range_key_rec.max_card_range                                     :=TRIM(v_RANGE_KEY_rec.max_card_range);
        v_mig_range_key_rec.issuing_bank_code                                  :=P_bank_code;
        v_mig_range_key_rec.key_code                                          :='PVK';
        v_mig_range_key_rec.key_index                                          :='001';
        v_mig_range_key_rec.key_seq                                          :='001';
        v_mig_range_key_rec.start_val_date                                  :=to_date ('03/04/2020','DD/MM/YYYY');
        v_mig_range_key_rec.end_val_date                                      :=to_date ('03/04/2099','DD/MM/YYYY');
        INSERT INTO   st_mig_RANGE_KEY VALUES v_mig_range_key_rec;
        v_mig_range_key_rec.min_card_range                                     :=TRIM(v_RANGE_KEY_rec.min_card_range);
        v_mig_range_key_rec.max_card_range                                     :=TRIM(v_RANGE_KEY_rec.max_card_range);
        v_mig_range_key_rec.issuing_bank_code                                  :=P_bank_code;
        v_mig_range_key_rec.key_code                                          :='CVK';
        v_mig_range_key_rec.key_index                                          :='001';
        v_mig_range_key_rec.key_seq                                          :='001';
        v_mig_range_key_rec.start_val_date                                  :=to_date ('03/04/2020','DD/MM/YYYY');
        v_mig_range_key_rec.end_val_date                                      :=to_date ('03/04/2099','DD/MM/YYYY');
        INSERT INTO   st_mig_RANGE_KEY VALUES v_mig_range_key_rec;
    END LOOP;

    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_RANGE_KEY_PARAM;


-----------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_CARD_GEN_COUNTERS_PARAM        (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_card_gen_counters_rec         CARD_GEN_COUNTERS%ROWTYPE :=NULL;
v_sequence_id                       PLS_INTEGER := 0;

CURSOR CUR_BIN_RANGE_PLASTIC_PROD IS
    SELECT  *
    FROM      st_pre_bin_range_plastic_prod
    WHERE  product_code IS NOT NULL
    AND bank_code = p_bank_code
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_CARD_GEN_COUNTERS_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    SELECT  NVL(MAX(SEQUENCE_ID),0) + 1
    INTO    v_sequence_id
    FROM    CARD_GEN_COUNTERS;

    FOR v_bin_range_plastic_prod_rec    IN  cur_BIN_RANGE_PLASTIC_PROD
    LOOP

        v_mig_card_gen_counters_rec.sequence_id                                 :=  v_sequence_id;
        v_mig_card_gen_counters_rec.card_gen_procedure                          :=  '00'                                               ;
        v_mig_card_gen_counters_rec.issuer_bin                                  :=  v_bin_range_plastic_prod_rec.bin        ;
        v_mig_card_gen_counters_rec.bank_code                                   :=  p_bank_code;
        v_mig_card_gen_counters_rec.network_code                                :=  NULL;
        v_mig_card_gen_counters_rec.card_product_code                           :=  v_bin_range_plastic_prod_rec.product_code                          ;
        v_mig_card_gen_counters_rec.card_type                                   :=  NULL;
        v_mig_card_gen_counters_rec.owner_code                                  :=  NULL;
        v_mig_card_gen_counters_rec.basic_card_flag                             :=  NULL;
        v_mig_card_gen_counters_rec.branch_code                                 :=  NULL;
        v_mig_card_gen_counters_rec.length_min                                  :=  length (v_bin_range_plastic_prod_rec.tranche_min);
        v_mig_card_gen_counters_rec.length_max                                  :=  length(v_bin_range_plastic_prod_rec.tranche_max);
        v_mig_card_gen_counters_rec.range_min                                   :=  v_bin_range_plastic_prod_rec.tranche_min    ;
        v_mig_card_gen_counters_rec.range_max                                   :=  v_bin_range_plastic_prod_rec.tranche_max    ;
        v_mig_card_gen_counters_rec.random_option                               :=  'R';
        v_mig_card_gen_counters_rec.counters_indicator                          :=  '0';
        v_mig_card_gen_counters_rec.last_counter_used                           :=  '1';
        v_mig_card_gen_counters_rec.issuer_bin_offset_start                     :=  '1';
        v_mig_card_gen_counters_rec.issuer_bin_offset_end                       :=  length(v_bin_range_plastic_prod_rec.bin);
        v_mig_card_gen_counters_rec.counter_offset_start                        :=  length(v_bin_range_plastic_prod_rec.bin)+1;
        v_mig_card_gen_counters_rec.counter_offset_end                          :=  length(v_bin_range_plastic_prod_rec.tranche_max)-1;

        INSERT INTO   st_mig_CARD_GEN_COUNTERS VALUES v_mig_card_gen_counters_rec;

        v_sequence_id :=v_sequence_id+1;
    END LOOP;

    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_CARD_GEN_COUNTERS_PARAM;



-----------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_ROUTING_CRITERIA_PARAM             (  p_business_date            IN                  DATE,
                                                        p_bank_code               IN                  BANK.bank_code%TYPE,
                                                        p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_routing_criteria_rec          P7_ROUTING_CRITERIA%ROWTYPE :=  NULL;
v_sequence_id                       P7_RANGE_SWITCH.sequence_id%TYPE;
v_Routing_id_1                           resources.resource_id%TYPE;
v_Routing_id_2                           resources.resource_id%TYPE;
v_resource_host                     RESOURCES.resource_id%TYPE;
v_description                       CARD_PRODUCT.wording%TYPE;

CURSOR CUR_CARD_RANGE IS
    SELECT  *
    FROM      st_mig_CARD_RANGE
    where  product_code IS NOT NULL
    AND issuing_bank_code = p_bank_code
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_ROUTING_CRITERIA_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    SELECT  LPAD( MAX(NVL(RESOURCE_id,0))- 1,6,'0')
    INTO v_Routing_id_1
    FROM  RESOURCES
    WHERE  resource_code ='03' ;

v_Routing_id_1:=  LPAD(v_Routing_id_1, 6, '0') ;
v_Routing_id_2:=    LPAD(v_Routing_id_1+1, 6, '0') ;
    SELECT   MAX(NVL(sequence_id,0))+ 1
    INTO v_sequence_id
    FROM p7_routing_criteria;

    FOR v_card_range_rec    IN  CUR_CARD_RANGE
    LOOP

---------------------------------------------



        v_sequence_id   :=  v_sequence_id   +   1;
        v_mig_routing_criteria_rec.sequence_id                                  :=v_sequence_id;
        v_mig_routing_criteria_rec.bank_code                                    :=p_bank_code;
        v_mig_routing_criteria_rec.PRIORITY                                     :='1';
        v_mig_routing_criteria_rec.CARD_PRODUCT_TYPE                            :='D';
        v_mig_routing_criteria_rec.ISSUER_BANK                                    :=p_bank_code;
        v_mig_routing_criteria_rec.min_card_range                                   :=TRIM(v_card_range_rec.min_card_range);
        v_mig_routing_criteria_rec.max_card_range                                     :=TRIM(v_card_range_rec.max_card_range);
        v_mig_routing_criteria_rec.processing_code                              :=NULL;
        v_mig_routing_criteria_rec.abrv_wording                                 :='ALL';
        v_mig_routing_criteria_rec.wording                                      :='ALL Transactions';
        v_mig_routing_criteria_rec.ORIGIN                                       :='111110';
        v_mig_routing_criteria_rec.CARD_NETWORK                                 :='01';
        v_mig_routing_criteria_rec.resource_id_1                                  :=TRIM(LPAD(v_Routing_id_1, 6, '0'));
        v_mig_routing_criteria_rec.resource_code_1                                :='03';
        v_mig_routing_criteria_rec.resource_priority_1                            :='1';
        v_mig_routing_criteria_rec.resource_id_2                                  :=TRIM(LPAD(v_Routing_id_2, 6, '0'));
        v_mig_routing_criteria_rec.resource_code_2                                 :='03';
        v_mig_routing_criteria_rec.resource_priority_2                            :='2';
        v_mig_routing_criteria_rec.alt_routing                                   :='C';
        INSERT INTO   st_mig_RANGE_SWITCH VALUES v_mig_routing_criteria_rec;


    END LOOP;

    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_ROUTING_CRITERIA_PARAM;




-----------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_RENEWAL_CRITERIA_PARAM         (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_batch_renewal_cr_rec          BATCH_RENEWAL_CRITERIA%ROWTYPE :=   NULL;

CURSOR CUR_BIN_RANGE_PLASTIC_PROD IS
    SELECT  *
    FROM      st_pre_bin_range_plastic_prod
    WHERE  product_code IS NOT NULL
    AND bank_code = p_bank_code
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_RENEWAL_CRITERIA_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;
    FOR v_bin_range_plastic_prod_rec    IN  CUR_BIN_RANGE_PLASTIC_PROD
    LOOP
        v_mig_batch_renewal_cr_rec.bank_code                        :=  p_bank_code ;
        v_mig_batch_renewal_cr_rec.product_code                     :=  TRIM(v_bin_range_plastic_prod_rec.product_code)                        ;
        v_mig_batch_renewal_cr_rec.nbr_cards_to_be_renewed          :=  NULL;
        v_mig_batch_renewal_cr_rec.nbr_cards_per_batch              :=  NULL;

        INSERT INTO   st_mig_BATCH_RENEWAL_CRITERIA VALUES v_mig_batch_renewal_cr_rec;
------  ----------------------------------------
    END LOOP;

    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_RENEWAL_CRITERIA_PARAM;
-----------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_PCRD_CARD_PROD_PARAM           (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_pcrd_card_prod_param_rec      pcrd_card_prod_param%ROWTYPE := NULL;
v_sequence_id                       PLS_INTEGER := 0;

CURSOR CUR_BIN_RANGE_PLASTIC_PROD IS
    SELECT  *
    FROM      st_pre_bin_range_plastic_prod
    WHERE  product_code is not null
    AND bank_code = p_bank_code
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_PCRD_CARD_PROD_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    SELECT  NVL(MAX(pcrd_card_prod_param_id),0) + 1
    INTO    v_sequence_id
    FROM    PCRD_CARD_PROD_PARAM;

    FOR v_bin_range_plastic_prod_rec    IN  cur_BIN_RANGE_PLASTIC_PROD
    LOOP

        v_mig_pcrd_card_prod_param_rec.pcrd_card_prod_param_id                              :=  v_sequence_id;
        v_mig_pcrd_card_prod_param_rec.bank_code                                            :=  p_bank_code ;
        v_mig_pcrd_card_prod_param_rec.card_product_code                                    :=  TRIM(v_bin_range_plastic_prod_rec.product_code);
        v_mig_pcrd_card_prod_param_rec.plastic_code                                         :=  TRIM(v_bin_range_plastic_prod_rec.plastic_type)  ;
        v_mig_pcrd_card_prod_param_rec.description                                          :=  SUBSTR(TRIM('FILE_'|| v_bin_range_plastic_prod_rec.description),1,16)     ;
        v_mig_pcrd_card_prod_param_rec.pin_mailer_on_hsm                                    :=  'F';--'H'
        v_mig_pcrd_card_prod_param_rec.pin_format_send_flag                                 :=  NULL;--'N'
        v_mig_pcrd_card_prod_param_rec.format_pin_mailer_code                               :=  NULL;-- '001'
        v_mig_pcrd_card_prod_param_rec.file_name_prod                                       :=  SUBSTR(TRIM('FILE_'|| v_bin_range_plastic_prod_rec.description),1,16);
        v_mig_pcrd_card_prod_param_rec.prefix_prod                                          :=  NULL;
        v_mig_pcrd_card_prod_param_rec.suffix_prod                                          :=  NULL;
        v_mig_pcrd_card_prod_param_rec.save_prod_file                                       :=  'Y';
        v_mig_pcrd_card_prod_param_rec.file_name_pin                                        :=  SUBSTR(TRIM('FILE_'|| v_bin_range_plastic_prod_rec.description),1,16);
        v_mig_pcrd_card_prod_param_rec.prefix_pin                                           :=  NULL;
        v_mig_pcrd_card_prod_param_rec.suffix_pin                                           :=  NULL;
        v_mig_pcrd_card_prod_param_rec.save_pin_file                                        :=  'Y';
        v_mig_pcrd_card_prod_param_rec.catalogue_product_code                                :=  'PAN'||TRIM(v_bin_range_plastic_prod_rec.product_code);
        v_mig_pcrd_card_prod_param_rec.catalogue_product_version                            :=  '1';
        INSERT INTO   st_mig_PCRD_CARD_PROD_PARAM VALUES v_mig_pcrd_card_prod_param_rec;
        v_sequence_id :=v_sequence_id+1;
    END LOOP;
    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_PCRD_CARD_PROD_PARAM;


--------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_Product_domain_PARAM           (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_P7_limits_rec                 P7_limits%ROWTYPE :=    NULL;
v_index                                card_product.product_code%TYPE;

CURSOR CUR_LIMIT_STAND IS
    SELECT  *
    FROM      st_pre_service_PROD
    where  product_code is not null
    AND bank_code = p_bank_code
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_Product_domain_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_P7_limits_rec   IN  cur_limit_stand
    LOOP
        v_index:=  TRIM(v_P7_limits_rec.product_code);




INSERT INTO   st_mig_product_domain
VALUES(p_bank_code,v_index,'begin  if :1 = :1 then null; end if; :2 := ''4''; if :3 = :3 then null; end if; :4 := ''4''; if :5 = :5 then null; end if; :6 := ''4''; if :7 = :7 then null; end if; :8 := ''4''; if :9 = :9 then null; end if; :10 := ''4''; if :11 = :11 then null; end if; :12 := ''4''; end;',NULL,NULL,NULL,NULL,NULL,NULL,'begin  if :1 = :1 then null; end if; :2 := ''4''; if :3 = :3 then null; end if; :4 := ''4''; if :5 = :5 then null; end if; :6 := ''4''; if :7 = :7 then null; end if; :8 := ''4''; if :9 = :9 then null; end if; :10 := ''4''; if :11 = :11 then null; end if; :12 := ''4''; end;',0,NULL,NULL,NULL,NULL,NULL,NULL,'begin  if :1 = :1 then null; end if; :2 := ''4''; if :3 = :3 then null; end if; :4 := ''4''; if :5 = :5 then null; end if; :6 := ''4''; if :7 = :7 then null; end if; :8 := ''4''; if :9 = :9 then null; end if; :10 := ''4''; if :11 = :11 then null; end if; :12 := ''4''; end;',0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'mgrUser',TO_DATE('2023-11-23 11:32:47', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

------
    END LOOP;
    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_Product_domain_PARAM;



--------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_Entity_event_PARAM           (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_P7_limits_rec                 P7_limits%ROWTYPE :=    NULL;
v_index                                card_product.product_code%TYPE;

CURSOR CUR_LIMIT_STAND IS
    SELECT  *
    FROM      st_pre_service_PROD
    where  product_code is not null
    AND bank_code = p_bank_code
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_Entity_event_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_P7_limits_rec   IN  cur_limit_stand
    LOOP
        v_index:=  TRIM(v_P7_limits_rec.product_code);


INSERT INTO   st_mig_Entity_event
VALUES(v_index,p_bank_code,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'mgrUser',TO_DATE('2023-11-23 11:32:48', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    END LOOP;
    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_Entity_event_PARAM;



 --------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_markup_calcul           (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_P7_limits_rec                 P7_limits%ROWTYPE :=    NULL;
v_index                                card_product.product_code%TYPE;

CURSOR CUR_LIMIT_STAND IS
    SELECT  *
    FROM      st_pre_service_PROD
    where  product_code is not null
    AND bank_code = p_bank_code
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_markup_calcul';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_P7_limits_rec   IN  cur_limit_stand
    LOOP
          v_index:=  TRIM(v_P7_limits_rec.product_code);

    INSERT INTO   st_mig_markup_calcul
    VALUES(p_bank_code,v_index,1,'Markup DBT ','IN',6,0,0,9999999999,6,6,0,0,9999999999,6,6,0,0,9999999999,6,6,0,0,9999999999,6,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'STD','E',0,NULL,'NAIHOS',TO_DATE('2024-08-09 17:06:49', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

  ----
    END LOOP;
    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_markup_calcul;

 ------------------------------------------------------------------------------------------------------------------------------

 --------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_markup_index           (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_P7_limits_rec                 P7_limits%ROWTYPE :=    NULL;
v_index                                card_product.product_code%TYPE;

CURSOR CUR_LIMIT_STAND IS
    SELECT  *
    FROM      st_pre_service_PROD
    where  product_code is not null
    AND bank_code = p_bank_code
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_markup_index';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_P7_limits_rec   IN  cur_limit_stand
    LOOP
          v_index:=  TRIM(v_P7_limits_rec.product_code);
INSERT INTO   st_mig_markup_index
VALUES(p_bank_code,v_index,'DF MARK','DF DBT MRKUP','firstUser',TO_DATE('2024-08-09 17:06:49', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);

    END LOOP;
    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_markup_index;

 ------------------------------------------------------------------------------------------------------------------------------


 --------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_markup_el_cur          (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_P7_limits_rec                 P7_limits%ROWTYPE :=    NULL;
v_index                                card_product.product_code%TYPE;

CURSOR CUR_LIMIT_STAND IS
    SELECT  *
    FROM      st_pre_service_PROD
    where  product_code is not null
    AND bank_code = p_bank_code
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_markup_el_cur';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_P7_limits_rec   IN  cur_limit_stand
    LOOP
          v_index:=  TRIM(v_P7_limits_rec.product_code);
        INSERT INTO   st_mig_markup_elligible_currencies
        VALUES(p_bank_code,v_index,1,p_currency_code,'MGR',TO_DATE('2024-08-09 17:06:49', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);
        INSERT INTO   st_mig_markup_elligible_currencies
        VALUES(p_bank_code,v_index,1,'840','MGR',TO_DATE('2024-08-09 17:06:49', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);
        INSERT INTO   st_mig_markup_currency_index
        VALUES(p_bank_code,v_index,p_currency_code,'2,5',NULL,NULL,NULL,NULL,'2,5',NULL,NULL,NULL,NULL,'2,5',NULL,NULL,NULL,NULL,'2,5',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'N','firstUser',TO_DATE('2019-09-11 14:16:36', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);
        INSERT INTO   st_mig_markup_currency_index
        VALUES(p_bank_code,v_index,'840','2,5',NULL,NULL,NULL,NULL,'2,5',NULL,NULL,NULL,NULL,'2,5',NULL,NULL,NULL,NULL,'2,5',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'N','firstUser',TO_DATE('2019-09-11 14:16:36', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);
  ----
    END LOOP;
    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_markup_el_cur;

 ------------------------------------------------------------------------------------------------------------------------------


 --------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_icc_application_PARAM           (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_P7_limits_rec                 P7_limits%ROWTYPE :=    NULL;
v_index                                card_product.product_code%TYPE;

CURSOR CUR_LIMIT_STAND IS
    SELECT  *
    FROM      st_pre_service_PROD
    where  product_code is not null
    AND bank_code = p_bank_code
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_icc_application_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_P7_limits_rec   IN  cur_limit_stand
    LOOP
          v_index:=  TRIM(v_P7_limits_rec.product_code);

INSERT INTO   st_mig_icc_application_par_index
VALUES(p_bank_code,'0001',v_index,'VSDC','VSDC','VSDC','POWERCARD',TO_DATE('2024-08-09 17:06:58', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);


    END LOOP;


 INSERT INTO   st_mig_ICC_CARD_VERIFICATION_DETAIL
VALUES(p_bank_code,'0001',1,'0',NULL,'000001',NULL,'firstUser',TO_DATE('2020-10-01 15:21:03', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);
    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_icc_application_PARAM;

 ------------------------------------------------------------------------------------------------------------------------------

  --------------------------------------------------------------------------------------------------------------------------------
FUNCTION    LOAD_Fleet_ctrl_PARAM           (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE,
                                                   p_currency_code           IN                  CURRENCY_TABLE.currency_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_mig_P7_limits_rec                 P7_limits%ROWTYPE :=    NULL;
v_index                                card_product.product_code%TYPE;

CURSOR CUR_LIMIT_STAND IS
    SELECT  *
    FROM      st_pre_service_PROD
    where  product_code is not null
    AND bank_code = p_bank_code
    ORDER BY product_code;

BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'LOAD_Fleet_ctrl_PARAM';
    v_env_info_trace.lang           :=  global_vars.LANG;

    FOR v_P7_limits_rec   IN  cur_limit_stand
    LOOP
          v_index:=  TRIM(v_P7_limits_rec.product_code);


INSERT INTO   st_mig_Fleet_ctrl
VALUES(p_bank_code,v_index,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'mgrUser',TO_DATE('2023-11-23 11:24:43', 'YYYY-MM-DD HH24:MI:SS'),NULL,NULL);
 ----
    END LOOP;
    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END LOAD_Fleet_ctrl_PARAM;



-----------------------------------------------------------------------------------------------------------------------------------
FUNCTION    MOVE_PARAMETERS_LOADED              (  p_business_date           IN                  DATE,
                                                   p_bank_code               IN                  BANK.bank_code%TYPE)
                                                    RETURN  PLS_INTEGER is
Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
v_sequence_id                       PLS_INTEGER;
v_name  VARCHAR2(256) ;
BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'MOVE_PARAMETERS_LOADED';
    v_env_info_trace.lang           :=  global_vars.LANG;


--Globalparam


        INSERT INTO region                                   SELECT * FROM   st_mig_region  ;
        INSERT INTO city                                     SELECT * FROM   st_mig_city  ;
        INSERT INTO branch                                   SELECT * FROM   st_mig_branch  ;
        INSERT INTO markup_index                            SELECT * FROM   st_mig_markup_index                      ;
        INSERT INTO markup_currency_index                   SELECT * FROM   st_mig_markup_currency_index             ;
        INSERT INTO markup_calcul                            SELECT * FROM   st_mig_markup_calcul                     ;
        INSERT INTO markup_elligible_currencies             SELECT * FROM   st_mig_markup_elligible_currencies       ;
        INSERT INTO hsm_key_member                          SELECT * FROM st_new_hsm_key_member            ;
        INSERT INTO chargeback_reason_code                  SELECT * FROM st_new_chargeback_reason_code            ;
        INSERT INTO auth_ctrl_value_param                   SELECT * FROM st_new_auth_ctrl_value_param             ;
        INSERT INTO p7_services_definition                  SELECT * FROM st_new_p7_services_definition            ;
        INSERT INTO P7_SERVICES_criteria                    SELECT * FROM st_new_P7_SERVICES_criteria              ;
        INSERT INTO BANK_CONTEXT_VALUE                      SELECT * FROM st_new_BANK_CONTEXT_VALUE                ;
        INSERT INTO owner_list                               SELECT * FROM st_new_owner_list  ;
        INSERT INTO client_activity_set                       SELECT * FROM st_new_client_activity_set  ;
        INSERT INTO socioprof_list                           SELECT * FROM st_new_socioprof_list ;
        INSERT INTO customer_segment                          SELECT * FROM st_new_customer_segment ;
        INSERT INTO bank_case_param                          SELECT * FROM st_new_bank_case_param ;
        INSERT INTO bank_network                               SELECT * FROM st_new_bank_network  ;
        INSERT INTO clearing_partner                        SELECT * FROM st_new_clearing_partner  ;
        INSERT INTO vip_list                                  SELECT * FROM st_new_vip_list ;
        INSERT INTO department                              SELECT * FROM st_new_department ;
        INSERT INTO group_reporting_def                      SELECT * FROM st_new_group_reporting_def ;
        INSERT INTO trans_reason_code                          SELECT * FROM st_new_trans_reason_code ;
        INSERT INTO trans_mv_linkup                           SELECT * FROM st_new_trans_mv_linkup  ;
        INSERT INTO trans_mv_batch                           SELECT * FROM st_new_trans_mv_batch  ;
        INSERT INTO addresses_type_list                       SELECT * FROM st_new_addresses_type_list  ;
        INSERT INTO status_list                               SELECT * FROM st_new_status_list  ;
        INSERT INTO status_reason_list                       SELECT * FROM st_new_status_reason_list  ;
        INSERT INTO status_reason_trans_source               SELECT * FROM st_new_status_reason_trans_source;
        INSERT INTO Status_reason_transition                   SELECT * FROM st_new_Status_reason_transition  ;

        INSERT INTO working_days                               SELECT * FROM st_new_working_days  ;
        INSERT INTO stop_list_reason_code                    SELECT * FROM st_new_stop_list_reason_code  ;
        INSERT INTO withdrawal_reason_code                    SELECT * FROM st_new_withdrawal_reason_code  ;
        INSERT INTO replacement_reason_code                    SELECT * FROM st_new_replacement_reason_code  ;
        INSERT INTO trans_bank_param                           SELECT * FROM st_new_trans_bank_param ;
        INSERT INTO emv_script_description                  SELECT * FROM st_new_emv_script_description ;
        INSERT INTO pwc_bank_report_parameters              SELECT * FROM st_new_pwc_bank_report_parameters ;
        INSERT INTO conversion_rate                          SELECT * FROM st_new_conversion_rate ;
        INSERT INTO trans_reject_param                      SELECT * FROM st_new_trans_reject_param ;
        INSERT INTO TRANS_CONTROL_PARAM                      SELECT * FROM st_new_TRANS_CONTROL_PARAM ;
        INSERT INTO case_type                                  SELECT * FROM st_new_case_type ;
        INSERT INTO action_table                              SELECT * FROM st_new_action_table ;
        INSERT INTO queue                                      SELECT * FROM st_new_queue ;
        INSERT INTO scenario_table                          SELECT * FROM st_new_scenario_table ;
        INSERT INTO link_scenario_action                      SELECT * FROM st_new_link_scenario_action ;
        INSERT INTO priority_table                          SELECT * FROM st_new_priority_table ;
        INSERT INTO case_reason                              SELECT * FROM st_new_case_reason ;
        INSERT INTO queue_profile                              SELECT * FROM st_new_queue_profile ;
        INSERT INTO email_parameter                          SELECT * FROM st_new_email_parameter ;
        INSERT INTO sms_parameter                              SELECT * FROM st_new_sms_parameter ;
        INSERT INTO queue_case_reason_link                   SELECT * FROM st_new_queue_case_reason_link  ;
        INSERT INTO scenario_case_reason_link                  SELECT * FROM st_new_scenario_case_reason_link ;
        INSERT INTO queue_case_type                          SELECT * FROM st_new_queue_case_type ;
        INSERT INTO p7_action_when_event                      SELECT * FROM st_new_p7_action_when_event ;
        INSERT INTO pcrd_trans_ctrl_param                      SELECT * FROM st_new_pcrd_trans_ctrl_param ;
        INSERT INTO emv_icc_application_param                SELECT * FROM st_new_emv_icc_application_param  ;
        INSERT INTO emv_fallback_risk_mng                      SELECT * FROM st_new_emv_fallback_risk_mng ;
        INSERT INTO TRANS_CTRL_VALUE_PARAM                  SELECT * FROM st_new_TRANS_CTRL_VALUE_PARAM ;
        INSERT INTO BANK_APPLICATION_PARAM                  SELECT * FROM st_new_BANK_APPLICATION_PARAM ;
        INSERT INTO mer_services_list                        SELECT * FROM st_new_mer_services_list ;
        INSERT INTO POWERCARD_GLOBALS_BANK                    SELECT * FROM st_new_POWERCARD_GLOBALS_BANK ;
        INSERT INTO PCRD_CONTACT_POSITION_LIST              SELECT * FROM st_new_PCRD_CONTACT_POSITION_LIST ;
        INSERT INTO ACCOUNT_LANG_LIST                         SELECT * FROM st_new_ACCOUNT_LANG_LIST             ;
        INSERT INTO ACCOUNT_TYPE_LIST                       SELECT * FROM st_new_ACCOUNT_TYPE_LIST          ;--
        INSERT INTO APPLICATION_EVENT                        SELECT * FROM st_new_APPLICATION_EVENT   ;
        INSERT INTO APPLICATION_REASON_FORCING              SELECT * FROM st_new_APPLICATION_REASON_FORCING ;
        INSERT INTO APPLICATION_REJECT_REASON                 SELECT * FROM st_new_APPLICATION_REJECT_REASON;
        INSERT INTO APPLICATION_TYPE                         SELECT * FROM st_new_APPLICATION_TYPE        ;
        INSERT INTO APPLICATION_WORK_STATUS                 SELECT * FROM st_new_APPLICATION_WORK_STATUS    ;
        INSERT INTO BANK_ACCOUNT_TYPE_LIST                    SELECT * FROM st_new_BANK_ACCOUNT_TYPE_LIST  ;
        INSERT INTO CHANNEL_TYPE_LIST                       SELECT * FROM st_new_CHANNEL_TYPE_LIST      ;
        INSERT INTO DATA_ACCESS                               SELECT * FROM st_new_DATA_ACCESS                  ;
        INSERT INTO DOCUMENT_LIST                              SELECT * FROM st_new_DOCUMENT_LIST            ;
        INSERT INTO ERSB_REASON_CODE                           SELECT * FROM st_new_ERSB_REASON_CODE          ;
        INSERT INTO EVENT_PARAM_TABLE                          SELECT * FROM st_new_EVENT_PARAM_TABLE         ;
        INSERT INTO pcard_report_param                      SELECT * FROM st_new_pcard_report_param            ;
        INSERT INTO EXHIBIT_REPORT                             SELECT * FROM st_new_EXHIBIT_REPORT            ;
        INSERT INTO EXTERNAL_ID_GEN_MODE                      SELECT * FROM st_new_EXTERNAL_ID_GEN_MODE     ;
        INSERT INTO HOLD_STATEMENT_REASON_PARAM              SELECT * FROM st_new_HOLD_STATEMENT_REASON_PARAM ;
        INSERT INTO M_EDUCATION_LIST                           SELECT * FROM st_new_M_EDUCATION_LIST           ;
        INSERT INTO NATIONAL_INTERCHANGE_PAR                   SELECT * FROM st_new_NATIONAL_INTERCHANGE_PAR   ;
        INSERT INTO P7_REASON_CODE_MAPPING                   SELECT * FROM st_new_P7_REASON_CODE_MAPPING      ;
        INSERT INTO POTENTIAL_CHGBK_REASON_CODE               SELECT * FROM st_new_POTENTIAL_CHGBK_REASON_CODE  ;
        INSERT INTO PWC_REPORTS_USER_SETUP                   SELECT * FROM st_new_PWC_REPORTS_USER_SETUP      ;
        INSERT INTO QUEUE_CRITERIA                             SELECT * FROM st_new_QUEUE_CRITERIA           ;
        INSERT INTO REMITTANCE_SEQ                           SELECT * FROM st_new_REMITTANCE_SEQ          ;
        INSERT INTO RET_REQ_REASON_CODE                        SELECT * FROM st_new_RET_REQ_REASON_CODE       ;
        INSERT INTO STK_INVENTORY_ITEM_DESC                 SELECT * FROM st_new_STK_INVENTORY_ITEM_DESC    ;
        INSERT INTO STOP_LIST_VERSIONS                        SELECT * FROM st_new_STOP_LIST_VERSIONS             ;
        INSERT INTO TITLE_LIST                                 SELECT * FROM st_new_TITLE_LIST            ;
        INSERT INTO TRANS_REJECT_FLAG_DEF                     SELECT * FROM st_new_TRANS_REJECT_FLAG_DEF    ;
        INSERT INTO VISA_INTERCHANGE_PAR                    SELECT * FROM st_new_VISA_INTERCHANGE_PAR       ;
        INSERT INTO bank_switch_cut_off                     SELECT * FROM st_new_bank_switch_cut_off       ;
----- Staging param

        INSERT INTO PLASTIC_LIST                               SELECT * FROM   st_mig_PLASTIC_LIST;
        INSERT INTO CARD_TYPE                                  SELECT * FROM   st_mig_CARD_TYPE;
        INSERT INTO CARD_FEES                                  SELECT * FROM   st_mig_CARD_FEES ;
        INSERT INTO P7_SERVICES_SETUP_NAME                     SELECT * FROM   st_mig_SERVICES_NAME;
        INSERT INTO P7_SERVICES_SETUP                          SELECT * FROM   st_mig_SERVICES_SETUP;
        INSERT INTO P7_SA_LIMITS_SETUP                         SELECT * FROM   st_mig_SA_LIMITS_SETUP;
        INSERT INTO P7_LIMITS                                  SELECT * FROM   st_mig_P7_LIMITS;
        INSERT INTO control_verification_flags                 SELECT * FROM   st_mig_ctrl_verification_flags;
        INSERT INTO P7_SPEC_TRANS_LIMITS                       SELECT * FROM   st_mig_SPEC_TRANS_LIMITS;
        INSERT INTO P7_EMV_LIMIT_SETUP                         SELECT * FROM   st_mig_EMV_LIMIT_SETUP;

        INSERT INTO EMV_KEYS_ASSIGNMENT                        SELECT * FROM   st_mig_EMV_KEYS_ASSIGNMENT;
        INSERT INTO CARD_PRODUCT                               SELECT * FROM   st_mig_CARD_PRODUCT;
        INSERT INTO CARD_RANGE                                 SELECT * FROM   st_mig_CARD_RANGE;
        INSERT INTO card_range_key                             SELECT * FROM   st_mig_RANGE_KEY;
        INSERT INTO emv_icc_appl_definition                    SELECT * FROM   st_mig_emv_icc_appl_definition;
        INSERT INTO CARD_GEN_COUNTERS                          SELECT * FROM   st_mig_CARD_GEN_COUNTERS;
        INSERT INTO P7_ROUTING_CRITERIA                        SELECT * FROM   st_mig_RANGE_SWITCH;
        INSERT INTO BATCH_RENEWAL_CRITERIA                     SELECT * FROM   st_mig_BATCH_RENEWAL_CRITERIA;
        INSERT INTO PCRD_CARD_PROD_PARAM                       SELECT * FROM   st_mig_PCRD_CARD_PROD_PARAM;
        INSERT INTO Product_domain_setup                       SELECT * FROM   st_mig_product_domain;
        INSERT INTO Entity_event_grouping                      SELECT * FROM   st_mig_Entity_event;
        INSERT INTO Fleet_ctrl_verif_flags                     SELECT * FROM   st_mig_Fleet_ctrl;
        INSERT INTO icc_application_par_index                  SELECT * FROM   st_mig_icc_application_par_index ;
        INSERT INTO ICC_CARD_VERIFICATION_DETAIL               SELECT * FROM   st_mig_ICC_CARD_VERIFICATION_DETAIL;

    RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
END MOVE_PARAMETERS_LOADED;

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
END pcrd_st_board_conv_iss_par;
/