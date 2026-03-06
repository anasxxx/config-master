
  CREATE OR REPLACE 
  PACKAGE  PCRD_ST_BOARD_CONV_MAIN
  IS
------------------------------------------------------------------------------------------------
-- MODIFICATION HISTORY
-- Person        Version  Ref               Date           Comments
-- -----------   ------   -------------     -----------    -------------------------------------
-- A.SARA     1.0.0                         24/07/2024     Initial version
--------------------------------------------------------------------------------------------------------


FUNCTION    MAIN_BOARD_CONV_PARAM               (  p_business_date                       IN                  DATE,
                                                    p_bank_code                            IN                  BANK.bank_code%TYPE,
                                                    p_bank_wording               IN                     BANK.bank_name%TYPE,
                                                    p_currency_code              IN                  CURRENCY_TABLE.currency_code%TYPE,
                                                    p_country_code                 IN                 COUNTRY.country_code%TYPE,
                                                    p_action_flag                         IN                  CHAR default '1'   )

                                                        RETURN  PLS_INTEGER;


END pcrd_st_board_conv_main;
/
CREATE OR REPLACE 
PACKAGE BODY PCRD_ST_BOARD_CONV_MAIN  
IS
------------------------------------------------------------------------------------------------
-- MODIFICATION HISTORY
-- Person        Version  Ref               Date           Comments
-- -----------   ------   -------------     -----------    -------------------------------------
-- A.SARA     1.0.0                         24/07/2024     Initial version
-------------------------------------------------------------------------------------------------------------------
FUNCTION    MAIN_BOARD_CONV_PARAM      ( p_business_date                   IN                  DATE,
                                            p_bank_code                  IN                  BANK.bank_code%TYPE,
                                            p_bank_wording               IN                     BANK.bank_name%TYPE,
                                            p_currency_code              IN                  CURRENCY_TABLE.currency_code%TYPE,
                                            p_country_code                 IN                 COUNTRY.country_code%TYPE,
                                            p_action_flag               IN                  CHAR default '1'                 )
                                    RETURN  PLS_INTEGER IS


Return_Status                       PLS_INTEGER;
v_env_info_trace                    global_vars.env_info_trace_type;
p_currency_record                       currency_table%ROWTYPE;
p_country_record                       country%ROWTYPE;
p_currency_code_alpha                   CURRENCY_TABLE.currency_code_alpha%TYPE;
p_country_code_alpha                    country.iso_country_alpha%TYPE;


BEGIN
    v_env_info_trace.user_name      :=  global_vars.USER_NAME;
    v_env_info_trace.module_code    :=  global_vars.ML_ADMINISTRATION;
    v_env_info_trace.package_name   :=  $$PLSQL_UNIT;
    v_env_info_trace.function_name  :=  'pcrd_st_board_conv_main';
    v_env_info_trace.lang           :=  global_vars.LANG;

       Return_Status   :=  PCRD_GET_PARAM_GENERAL_ROWS.GET_CURRENCY_TABLE    ( p_currency_code,
                                                                            p_currency_record);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY PCRD_GET_PARAM_GENERAL_ROWS.GET_CURRENCY_TABLE :'||p_currency_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;
    p_currency_code_alpha         := p_currency_record.currency_code_alpha;

    Return_Status   :=  PCRD_GET_PARAM_GENERAL_ROWS.GET_COUNTRY    (   p_country_code,
                                                                    p_country_record);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY PCRD_GET_PARAM_GENERAL_ROWS.GET_COUNTRY :'||p_country_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;
    p_country_code_alpha         := p_country_record.iso_country_alpha;

        Return_Status   :=  pcrd_st_board_conv_com.Sequence_ajustment      ;
        IF Return_Status <> declaration_cst.OK
        THEN
            v_env_info_trace.user_message := ':ERROR RETURNED BY PCRD_ST_CONV_CLEAN.AUT_CONV_DATA_ROLLBACK :'||p_bank_code;
            PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
            ROLLBACK;
            RETURN (Return_Status);
        END IF;

        COMMIT;
    IF (NVL(p_action_flag,'X') = '0')
        THEN
---Staging a remplir
         Return_Status   :=  PCRD_ST_CONV_CLEAN.AUT_CONV_DATA_ROLLBACK          (     p_bank_code,
                                                                                p_bank_wording );
        IF Return_Status <> declaration_cst.OK
        THEN
            v_env_info_trace.user_message := ':ERROR RETURNED BY PCRD_ST_CONV_CLEAN.AUT_CONV_DATA_ROLLBACK :'||p_bank_code;
            PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
            ROLLBACK;
            RETURN (Return_Status);
        END IF;
        Return_Status   :=  PCRD_ST_CONV_CLEAN.AUT_CONV_FINALPARAM_ROLLBACK          (     p_bank_code,
                                                                            p_bank_wording,
                                                                            p_country_code );
        IF Return_Status <> declaration_cst.OK
        THEN
            v_env_info_trace.user_message := ':ERROR RETURNED BY PCRD_ST_CONV_CLEAN.AUT_CONV_FINALPARAM_ROLLBACK :'||p_bank_code;
            PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
            ROLLBACK;
            RETURN (Return_Status);
        END IF;
        IF Return_Status = declaration_cst.OK
        THEN
        v_env_info_trace.user_message := ':Cest Supprime :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);

        COMMIT;
           Return_Status   :=  PCRD_ST_CONV_CLEAN.BANK_PARAM_CLEAN          (     p_bank_code,
                                                                                p_bank_wording,
                                                                               p_country_code );
            IF Return_Status <> declaration_cst.OK
            THEN
                v_env_info_trace.user_message := ':ERROR RETURNED BY PCRD_ST_CONV_CLEAN.BANK_PARAM_CLEAN :'||p_bank_code;
                PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
                ROLLBACK;
                RETURN (Return_Status);
            END IF;

            IF Return_Status = declaration_cst.OK
            THEN
            v_env_info_trace.user_message := ':Cest Supprime 2 :'||p_bank_code;
            PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);

            COMMIT;
            END IF;
        END IF;
    END IF;

    IF (NVL(p_action_flag,'X') = '1')
    THEN


        Return_Status   :=  PCRD_ST_CONV_CLEAN.AUT_CONV_GLB_TEMP_ROLLBACK          (     p_bank_code,
                                                                            p_bank_wording,
                                                                            p_country_code );
        IF Return_Status <> declaration_cst.OK
        THEN
            v_env_info_trace.user_message := ':ERROR RETURNED BY PCRD_ST_CONV_CLEAN.AUT_CONV_GLB_TEMP_ROLLBACK :'||p_bank_code;
            PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
            ROLLBACK;
            RETURN (Return_Status);
        END IF;

        Return_Status   :=  PCRD_ST_CONV_CLEAN.AUT_CONV_PRODUCT_TEMP_ROLLBACK          (     p_bank_code,
                                                                            p_bank_wording,
                                                                            p_country_code );
        IF Return_Status <> declaration_cst.OK
        THEN
            v_env_info_trace.user_message := ':ERROR RETURNED BY PCRD_ST_CONV_CLEAN.AUT_CONV_PRODUCT_TEMP_ROLLBACK :'||p_bank_code;
            PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
            ROLLBACK;
            RETURN (Return_Status);
        END IF;

        Return_Status   :=  pcrd_st_board_conv_com.LOAD_BANK_PARAMETERS          (  p_business_date,
                                                                                        p_bank_code,
                                                                                        p_bank_wording,
                                                                                        p_currency_code,
                                                                                        p_currency_code_alpha,
                                                                                        p_country_code,
                                                                                        p_country_code_alpha);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_com.LOAD_BANK_PARAMETERS :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;

 END IF;

    IF (NVL(p_action_flag,'X') = '2')
        THEN
---Staging a remplir
            Return_Status   :=  PCRD_ST_CONV_CLEAN.MAIN_AUT_CLEAN          (     p_bank_code,
                                                                            p_bank_wording,
                                                                            p_country_code );
        IF Return_Status <> declaration_cst.OK
        THEN
            v_env_info_trace.user_message := ':ERROR RETURNED BY PCRD_ST_CONV_CLEAN.MAIN_AUT_CLEAN :'||p_bank_code;
            PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
            ROLLBACK;
            RETURN (Return_Status);
        END IF;
    END IF;


    IF (NVL(p_action_flag,'X') = '1') OR (NVL(p_action_flag,'X') = '2')
    THEN
    Return_Status   :=  pcrd_st_board_conv_com.LOAD_BANK_CONV_COM_PARAM ( p_business_date,
                                                                                    p_bank_code,
                                                                                    p_bank_wording,
                                                                                    p_currency_code,

                                                                                    p_country_code);
    IF Return_Status <> declaration_cst.OK
    THEN
        v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_com.LOAD_BANK_CONV_COM_PARAM :'||p_bank_code;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        ROLLBACK;
        RETURN (Return_Status);
    END IF;



---Staging a remplir
        Return_Status   :=  pcrd_st_board_conv_iss_par.LOAD_BANK_CONV_ISS_PARAM      (  p_business_date,
                                                                                        p_bank_code,
                                                                                        p_bank_wording,
                                                                                        p_currency_code,
                                                                                        p_currency_code_alpha,
                                                                                        p_country_code,
                                                                                        p_country_code_alpha);
        IF Return_Status <> declaration_cst.OK
        THEN
            v_env_info_trace.user_message := ':ERROR RETURNED BY pcrd_st_board_conv_iss_par.LOAD_BANK_CONV_COM_PARAM :'||p_bank_code;
            PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
            ROLLBACK;
            RETURN (Return_Status);
        END IF;
    END IF;

        RETURN (declaration_cst.OK);

    EXCEPTION WHEN OTHERS
    THEN
        v_env_info_trace.user_message   :=  NULL;
        PCRD_GENERAL_TOOLS.PUT_TRACES (v_env_info_trace,$$PLSQL_LINE);
        RETURN (declaration_cst.ERROR);
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
END MAIN_BOARD_CONV_PARAM;


END pcrd_st_board_conv_main;
/