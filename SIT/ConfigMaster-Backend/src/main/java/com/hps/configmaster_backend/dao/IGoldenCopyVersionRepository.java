package com.hps.configmaster_backend.dao;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import com.hps.configmaster_backend.entity.GoldenCopyVersion;

@Repository
public interface IGoldenCopyVersionRepository  extends JpaRepository<GoldenCopyVersion, String> {

	
	@Query(value = """
		    SELECT *
		    FROM st_goldencopy_version
		    WHERE REGEXP_LIKE(TRIM(version_id), '^V[0-9]+$')
		    ORDER BY TO_NUMBER(SUBSTR(TRIM(version_id), 2)) DESC
		    FETCH FIRST 1 ROWS ONLY
		    """, nativeQuery = true)
	Optional<GoldenCopyVersion> findTopByOrderByIdDesc();
	


	
	

}
