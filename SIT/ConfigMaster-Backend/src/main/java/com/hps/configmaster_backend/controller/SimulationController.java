package com.hps.configmaster_backend.controller;

import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.hps.configmaster_backend.models.BankReq;
import com.hps.configmaster_backend.models.BatchOfCampagneModule;
import com.hps.configmaster_backend.models.CampagneModule;
import com.hps.configmaster_backend.models.SimulationResultModule;
import com.hps.configmaster_backend.models.TraceBatchModel;
import com.hps.configmaster_backend.service.IBatchOfCampagneService;
import com.hps.configmaster_backend.service.ICampagneService;
import com.hps.configmaster_backend.service.IGoldenCopyVersionService;
import com.hps.configmaster_backend.service.ISimulationResulService;
import com.hps.configmaster_backend.service.ITNRScriptService;
import com.hps.configmaster_backend.service.ITraceBatchService;

@RestController
@RequestMapping("/v1/api/simulation")
public class SimulationController {

    @Autowired
    private ITNRScriptService tnrScriptService;
    @Autowired
    private ISimulationResulService  simulationResulService;
    @Autowired
    private IBatchOfCampagneService batchOfCampagneService;

    @Autowired
    private ICampagneService  campagneService;
    @Autowired

    private ITraceBatchService traceBatchService;
    
    @Autowired

    private IGoldenCopyVersionService goldenCopyService;
    
    // Exécution du script Unix pour l'option "offline"
    @GetMapping("/ITNRScript/offline/{campagne}")
    public ResponseEntity<String> runOfflineSimulation(@PathVariable("campagne") String campagne) {
        String result = tnrScriptService.runUnixScriptOffline(campagne);
        return ResponseEntity.ok(result);
    }

    // Exécution du script Unix pour le "back-office"
    @GetMapping("/ITNRScript/backOffice/{campagne}")
    public ResponseEntity<String> runBackOfficeSimulation(@PathVariable("campagne") String campagne) {
        String result = tnrScriptService.runUnixScriptBackOffice(campagne);
        return ResponseEntity.ok(result);
    }
    
    @GetMapping("/SimulationResult/{campagne}")
    public ResponseEntity<SimulationResultModule> SimulationResultBackOffics(@PathVariable("campagne") String campagne) {

        try {
            SimulationResultModule results = simulationResulService.parseLogFile(campagne);
            return ResponseEntity.ok(results);
        } catch (IOException e) {
            return ResponseEntity.status(500).build();
        }
    }
    
    @GetMapping("/download/{campagne}/{batchName}")
    public ResponseEntity<byte[]> downloadResultFile(@PathVariable("campagne") String campagne,@PathVariable("batchName") String batchName) {
        byte[] fileData = simulationResulService.downloadFileFromSftp(campagne,batchName);
        
        if (fileData == null) {
            return ResponseEntity.noContent().build(); // HTTP 204
        }


        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_OCTET_STREAM);
        headers.setContentDisposition(ContentDisposition.attachment().filename(batchName).build());

        return new ResponseEntity<>(fileData, headers, HttpStatus.OK);
    }

    
    @GetMapping("/trace/{campagne}/{batchName}")
    public ResponseEntity<List<TraceBatchModel>> traceBatch(@PathVariable("campagne") String campagne,@PathVariable("batchName") String batchName) {
       
    	
    	 try {
             List<TraceBatchModel> results = traceBatchService.getTraceOfBatch(campagne, batchName);
             return ResponseEntity.ok(results);
         } catch (IOException e) {
             return ResponseEntity.status(500).build();
         }
    	
    	
    }

  
    @GetMapping("/batches/{campagne}")
    public ResponseEntity<List<BatchOfCampagneModule>> batchOfCampagne(@PathVariable("campagne") String campagne) {
        try {
            List<BatchOfCampagneModule> results = batchOfCampagneService.getUsecasOfCampaign(campagne);
            return ResponseEntity.ok(results);
        } catch (Exception e) {
            e.printStackTrace(); // Pour débogage en console
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    
    
    @GetMapping("/campagneFull/{profile}")
    public ResponseEntity<List<CampagneModule>> getAllCampagnes(@PathVariable("profile") String profile) {
        
    	 try {
             List<CampagneModule> results = campagneService.getAllCampagne(profile);
             return ResponseEntity.ok(results);
         } catch (Exception e) {
             e.printStackTrace(); // Pour débogage en console
             return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
         }        
    }
    
    
    @PostMapping("/golden-copy/download")
    public ResponseEntity<byte[]> downloadGoldenCopy(@RequestBody String description) {
        byte[] zipBytes = goldenCopyService.exportAsZip(description);

        return ResponseEntity.ok()
            .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=golden-copy.zip")
            .contentType(MediaType.APPLICATION_OCTET_STREAM)
            .body(zipBytes);
    }

    
    
    
    
}
