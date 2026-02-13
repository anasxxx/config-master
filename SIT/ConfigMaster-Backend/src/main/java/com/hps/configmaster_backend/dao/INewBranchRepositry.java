package com.hps.configmaster_backend.dao;

import org.springframework.data.jpa.repository.JpaRepository;

import com.hps.configmaster_backend.entity.NewBranch;


public interface INewBranchRepositry extends JpaRepository<NewBranch,String>  {

}
