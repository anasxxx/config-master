package com.hps.configmaster_backend.entity;

import jakarta.persistence.*;
import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonIgnore;


public class ServiceSetupName {

    @Column(name = "BANK_CODE")
    private String codeBank;

    @Id
    @Column(name = "SERVICES_SETUP_INDEX")
    private String serviceSetupIndex;

    @OneToMany(mappedBy = "serviceSetupName", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<ServiceSetup> serviceSetup = new ArrayList<>();

    @OneToOne(mappedBy = "serviceSetupName")
    @JsonIgnore  // Ignore la sérialisation de cette propriété
    private CardProduct cardProduct;
    
   

    public ServiceSetupName() {}

    
    public List<ServiceSetup> getServiceSetup() {
        return serviceSetup;
    }

    public void setServiceSetup(List<ServiceSetup> serviceSetup) {
        this.serviceSetup = serviceSetup;
    }

    public CardProduct getCardProduct() {
        return cardProduct;
    }

    public void setCardProduct(CardProduct cardProduct) {
        this.cardProduct = cardProduct;
    }
    
}
