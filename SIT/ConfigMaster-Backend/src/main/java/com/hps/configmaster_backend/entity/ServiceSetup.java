package com.hps.configmaster_backend.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.*;

@Entity
@Table(name="p7_services_setup")
public class ServiceSetup {

	@Id
    @Column(name = "SEQUENCE_ID")
    private Integer sequenceId;

    
    @ManyToOne
    @JoinColumns({

        @JoinColumn(name = "bank_code", referencedColumnName = "bank_code", insertable = false, updatable = false),
        @JoinColumn(name = "SERVICE_SETUP_INDEX", referencedColumnName = "SERVICES_SETUP_INDEX", insertable = false, updatable = false)
    })
    @JsonIgnore  // Ignore la sérialisation de cette propriété

    private CardProduct cardProduct;
    


    @Column(name = "WORDING")
    private String wording;

    public ServiceSetup() {}

 

    public String getWording() {
        return wording;
    }

    public void setWording(String wording) {
        this.wording = wording;
    }
    
}
