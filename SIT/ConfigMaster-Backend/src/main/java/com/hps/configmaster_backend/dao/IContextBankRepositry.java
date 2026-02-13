package com.hps.configmaster_backend.dao;

import org.springframework.data.jpa.repository.JpaRepository;

import com.hps.configmaster_backend.entity.ContextBank;
import com.hps.configmaster_backend.entity.Country;

public interface IContextBankRepositry extends JpaRepository<ContextBank, String> {

}
