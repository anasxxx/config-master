package com.hps.configmaster_backend.service;

import com.hps.configmaster_backend.entity.NewBranch;

public interface NewBranchServiceI {
	public NewBranch addNewBranch(NewBranch branch);
	public void deletNewBranch(String branchId);

}
