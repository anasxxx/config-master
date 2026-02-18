package com.hps.configmaster_backend.dao;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import com.hps.configmaster_backend.entity.MigLimitStand;

import org.springframework.transaction.annotation.Transactional;

public interface IMigLimitStandRepositry extends JpaRepository<MigLimitStand, String>{


	
	 @Modifying
	 @Transactional
	 @Query(value = "DELETE FROM st_pre_limit_stand WHERE limits_id = RPAD(:id, 3, ' ')", nativeQuery = true)
	 void deleteByTrimmedId(@Param("id") String id);
	


}
