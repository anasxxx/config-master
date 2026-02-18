package com.hps.configmaster_backend.dao;

import org.springframework.data.jpa.repository.JpaRepository;

import com.hps.configmaster_backend.entity.MigResources;


public interface IMigResourcesRepositry extends JpaRepository<MigResources, String> {

}
