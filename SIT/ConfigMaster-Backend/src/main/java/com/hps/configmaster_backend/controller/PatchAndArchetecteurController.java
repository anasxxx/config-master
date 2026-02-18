package com.hps.configmaster_backend.controller;

import java.util.*;

import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.hps.configmaster_backend.entity.ArchitectureConvergence;
import com.hps.configmaster_backend.entity.NvPatchConvergence;
import com.hps.configmaster_backend.models.ArchetecteurModule;
import com.hps.configmaster_backend.models.ContextBankModule;
import com.hps.configmaster_backend.models.NvPatchConvergenceModule;
import com.hps.configmaster_backend.service.IArchitectureConvergenceService;
import com.hps.configmaster_backend.service.IContextBankService;
import com.hps.configmaster_backend.service.INvPatchConvergenceService;

@RestController
@RequestMapping("/v1/api/PatchArchetContext")
public class PatchAndArchetecteurController {


    @Autowired
    private INvPatchConvergenceService nvPatchConvergenceService;
    @Autowired
    private IArchitectureConvergenceService architectureConvergenceService;
    @Autowired
    private IContextBankService contextBankService;

// la récupération du niveau de patch
    
    @GetMapping("/patch")
    public ResponseEntity<List<NvPatchConvergenceModule>> getNiveauPatch() {

    	List<NvPatchConvergence> patches = nvPatchConvergenceService.getAllNvPatchConvergence();

        if (patches == null || patches.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NO_CONTENT).build();
        }

        List<NvPatchConvergenceModule> list = new ArrayList<>();
        for (NvPatchConvergence patch : patches) {
            NvPatchConvergenceModule p = new NvPatchConvergenceModule();
            BeanUtils.copyProperties(patch, p);
            list.add(p);
        }

        return ResponseEntity.ok(list); // 200 OK avec la liste transformée
    }@GetMapping("/ArchitectureNode1/{codeBank}")
    public ResponseEntity<?> getArchitectureNode1(@PathVariable String codeBank) {
        List<ArchetecteurModule> architectes = architectureConvergenceService.getArchitectureNode1(codeBank);

        if (architectes.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                                 .body("Aucun architecte trouvé pour le node 1.");
        }

        return ResponseEntity.ok(architectes);
    }

    @GetMapping("/ArchitectureNode2/{codeBank}")
    public ResponseEntity<?> getArchitectureNode2(@PathVariable String codeBank) {
        List<ArchetecteurModule> architectes = architectureConvergenceService.getArchitectureNode2(codeBank);

        if (architectes.isEmpty()) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                                 .body("Aucun architecte trouvé pour le node 2.");
        }

        return ResponseEntity.ok(architectes);
    }
    
    @GetMapping("/ContextBank/{codeBank}")
    public ResponseEntity<?> getContextBank(@PathVariable String codeBank) {
        
        ContextBankModule result = contextBankService.getContextBnaque(codeBank);

        if (result == null) {
            return ResponseEntity
                    .status(HttpStatus.NOT_FOUND)
                    .body("Aucun contexte trouvé pour la banque : " + codeBank);
        }

        return ResponseEntity.ok(result);
    }

    
    
    
    
    
    
}