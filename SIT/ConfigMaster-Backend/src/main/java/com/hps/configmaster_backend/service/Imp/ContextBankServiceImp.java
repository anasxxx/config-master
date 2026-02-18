package com.hps.configmaster_backend.service.Imp;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Optional;

import com.hps.configmaster_backend.dao.IContextBankRepositry;
import com.hps.configmaster_backend.entity.ContextBank;
import com.hps.configmaster_backend.models.ContextBankModule;
import com.hps.configmaster_backend.service.IContextBankService;

@Service
public class ContextBankServiceImp implements IContextBankService {

    @Autowired
    private IContextBankRepositry contextBankRepositry;

    @Override
    public ContextBankModule getContextBnaque(String codeBank) {
        Optional<ContextBank> contextBankOpt = contextBankRepositry.findById(codeBank);

        if (contextBankOpt.isPresent()) {
            ContextBank contextBnaque = contextBankOpt.get();

            ContextBankModule module = new ContextBankModule();
            module.setBankCode(contextBnaque.getBankCode());
            module.setDescription(contextBnaque.getDescription()); 

            return module;
        }

        return null;
    }
}
