package com.hps.configmaster_backend.dao;

import org.springframework.data.jpa.repository.JpaRepository;

import com.hps.configmaster_backend.entity.MigServiceProd;

public interface IMigServiceProdRepositry extends JpaRepository<MigServiceProd, String> {

}
