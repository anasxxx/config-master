package com.hps.configmaster_backend.dao;

import org.springframework.data.jpa.repository.JpaRepository;

import com.hps.configmaster_backend.entity.Country;
import com.hps.configmaster_backend.entity.Resources;

public interface IResourcesRepository extends  JpaRepository<Resources, String> {

}
