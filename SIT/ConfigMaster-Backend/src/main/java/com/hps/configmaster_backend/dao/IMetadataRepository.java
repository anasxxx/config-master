package com.hps.configmaster_backend.dao;

import java.util.List;

import com.hps.configmaster_backend.models.PackageModule;

public interface IMetadataRepository {

	 public List<PackageModule> getFilteredPackages() ;
}
