package com.hps.configmaster_backend.service.Imp;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.dao.IArchitectureConvergenceRepository;
import com.hps.configmaster_backend.entity.ArchitectureConvergence;
import com.hps.configmaster_backend.models.ArchetecteurModule;
import com.hps.configmaster_backend.service.IArchitectureConvergenceService;

@Service
public class ImpArchitectureConvergenceService implements IArchitectureConvergenceService {
	
	 @Autowired
	    private IArchitectureConvergenceRepository repository;

	    public List<ArchetecteurModule> getArchitectureNode1(String codeBanque) {
	         return  repository.findArchitectureNode1(codeBanque);
	        
	    }
	    public List<ArchetecteurModule> getArchitectureNode2(String codeBanque) {
	         return  repository.findArchitectureNode2(codeBanque);
	        
	    }

}

