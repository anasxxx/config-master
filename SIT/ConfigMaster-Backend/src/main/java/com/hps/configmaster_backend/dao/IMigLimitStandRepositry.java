package com.hps.configmaster_backend.dao;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import com.hps.configmaster_backend.entity.MigLimitStand;
import com.hps.configmaster_backend.entity.MigLimitStandId;

import org.springframework.transaction.annotation.Transactional;

public interface IMigLimitStandRepositry extends JpaRepository<MigLimitStand, MigLimitStandId>{


	
	 @Modifying
	 @Transactional
	 @Query(value = "DELETE FROM st_pre_limit_stand WHERE TRIM(product_code) = TRIM(:productCode) AND TRIM(limits_id) = TRIM(:id)", nativeQuery = true)
	 void deleteByProductCodeAndLimitId(@Param("productCode") String productCode, @Param("id") String id);
	


}
