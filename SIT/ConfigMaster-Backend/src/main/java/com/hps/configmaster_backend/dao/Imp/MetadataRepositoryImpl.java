package com.hps.configmaster_backend.dao.Imp;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import com.hps.configmaster_backend.dao.IMetadataRepository;
import com.hps.configmaster_backend.models.PackageModule;

@Repository
public class MetadataRepositoryImpl implements IMetadataRepository {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Override
    public List<PackageModule> getFilteredPackages() {
    	String sql = """
    		    SELECT 
    		        OBJECT_NAME, 
    		        OBJECT_TYPE, 
    		        DBMS_METADATA.GET_DDL(OBJECT_TYPE, OBJECT_NAME) AS DDL
    		    FROM USER_OBJECTS
    		    WHERE OBJECT_TYPE IN ('PACKAGE', 'PROCEDURE', 'FUNCTION')
    		      AND OBJECT_NAME IN (
    		        'PCRD_ST_BOARD_CONV_MAIN',
    		        'PCRD_ST_BOARD_CONV_ISS_PAR',
    		        'PCRD_ST_CONV_CATALOGUE',
    		        'PCRD_ST_CONV_CLEAN',
    		        'PCRD_ST_BOARD_CONV_COM'
    		    )
    		""";

        return jdbcTemplate.query(sql, (rs, rowNum) -> new PackageModule(
            rs.getString("OBJECT_NAME"),
            rs.getString("OBJECT_TYPE"),
            rs.getString("DDL")
        ));
    }
}
