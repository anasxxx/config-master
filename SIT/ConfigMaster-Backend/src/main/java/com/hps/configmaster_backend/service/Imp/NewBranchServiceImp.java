package com.hps.configmaster_backend.service.Imp;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.dao.INewBranchRepositry;
import com.hps.configmaster_backend.entity.NewBranch;
import com.hps.configmaster_backend.service.NewBranchServiceI;
@Service
public class NewBranchServiceImp implements NewBranchServiceI {

	
	@Autowired
	INewBranchRepositry newBranchRepositry;
	@Override
	public NewBranch addNewBranch(NewBranch branch) {
		return newBranchRepositry.save(branch);
	}

	@Override

	public void deletNewBranch(String branchId)
{
		newBranchRepositry.deleteById(branchId);
	}

}
