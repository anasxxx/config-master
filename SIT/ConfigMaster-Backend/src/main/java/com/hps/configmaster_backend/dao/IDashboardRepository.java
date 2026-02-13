package com.hps.configmaster_backend.dao;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import com.hps.configmaster_backend.entity.V_auth_activity_view;
@Repository
public interface IDashboardRepository extends JpaRepository<V_auth_activity_view, String>  {
	
	@Query(value = """ 
		    SELECT 
		        trunc(v.internal_transmission_time) AS transaction_date,
		        v.issuing_bank,
		        
		        COUNT(1) AS totalTransaction,
		        TO_CHAR(ROUND(
		            COUNT(CASE WHEN action_code = '000' AND message_type <> '1420' AND reversal_flag = 'N' THEN 1 END) * 100.0 / COUNT(1), 3), 'FM99990.0') || '%' AS perApproved,
		        TO_CHAR(ROUND(
		            COUNT(CASE WHEN (action_code = '000' AND reversal_flag = 'F') OR (action_code = '480' AND message_type = '1420') THEN 1 END) * 100.0 / COUNT(1), 3), 'FM99990.0') || '%' AS perCancellationApproved,
		        TO_CHAR(ROUND(
		            COUNT(CASE WHEN action_code <> '480' AND message_type = '1420' THEN 1 END) * 100.0 / COUNT(1), 3), 'FM99990.0') || '%' AS perCancellationRejected,
		        TO_CHAR(ROUND(
		            COUNT(CASE 
		                WHEN action_code NOT IN (
		                    '000','104','115','118','122','199','302','304','305','306','307','308','309','381',
		                    '383','483','484','485','486','482','501','503','582','800','880','898','899',
		                    '902','903','908','909','911','912','992','993','994','995')
		                AND message_type <> '1420' 
		                THEN 1 
		            END) * 100.0 / COUNT(1), 3), 'FM99990.0') || '%' AS perDeclinedFonc,
		        TO_CHAR(ROUND(
		            COUNT(CASE 
		                WHEN action_code IN (
		                    '104','115','118','122','199','302','304','305','306','307','308','309','381',
		                    '383','483','484','485','486','482','501','503','582','800','880','898','899',
		                    '902','903','908','909','911','912','992','993','994','995')
		                AND message_type <> '1420' 
		                THEN 1 
		            END) * 100.0 / COUNT(1), 3), 'FM99990.0') || '%' AS perDeclinedTech
		    FROM v_autho_activity_view v
		    WHERE trunc(v.internal_transmission_time) =  TO_DATE(:p_date_selected, 'DD/MM/YYYY')
		      AND v.issuing_bank = :p_bank_code
		    GROUP BY trunc(v.internal_transmission_time), v.issuing_bank
		    ORDER BY transaction_date DESC, v.issuing_bank DESC
		    """, nativeQuery = true)
		List<Object[]> getTransactionStats(@Param("p_date_selected") String pDateSelected, 
		                                   @Param("p_bank_code") String pBankCode);
	
	
	
	
	
	
}