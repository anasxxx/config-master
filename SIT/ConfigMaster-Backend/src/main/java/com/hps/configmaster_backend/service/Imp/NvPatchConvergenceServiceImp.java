package com.hps.configmaster_backend.service.Imp;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.dao.INvPatchConvergenceRepository;
import com.hps.configmaster_backend.entity.NvPatchConvergence;
import com.hps.configmaster_backend.service.INvPatchConvergenceService;

import jakarta.transaction.Transactional;

@Service
@Transactional
public class NvPatchConvergenceServiceImp implements INvPatchConvergenceService{

    @Autowired
	INvPatchConvergenceRepository nvPatchConvergenceRepository;
	
	
	@Override
	public List<NvPatchConvergence> getAllNvPatchConvergence() {

		
		return nvPatchConvergenceRepository.getAllNvPatchConvergence();
	}
	

}
