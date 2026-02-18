package com.hps.configmaster_backend.dao;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import com.hps.configmaster_backend.entity.NvPatchConvergence;


public interface INvPatchConvergenceRepository  extends JpaRepository<NvPatchConvergence,String> {

    @Query("SELECT n FROM NvPatchConvergence n")
	 
	 public List<NvPatchConvergence> getAllNvPatchConvergence();


	
}
