package com.hps.configmaster_backend.service;

import java.util.List;

import com.hps.configmaster_backend.entity.ArchitectureConvergence;
import com.hps.configmaster_backend.models.ArchetecteurModule;

public interface IArchitectureConvergenceService {

	
	public List<ArchetecteurModule> getArchitectureNode1(String codeBanque);
public List<ArchetecteurModule> getArchitectureNode2(String codeBanque);
}
