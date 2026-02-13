package com.hps.configmaster_backend.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;

@Entity
@Table(name = "P7_BANK_RESOURCE_PARAM")
public class RessourceParam {

    @Id
    @Column(name = "RESOURCE_ID", length = 6)
    private String resource_id;

    @ManyToOne
    @JoinColumn(name = "ACQUIRER_BANK_CODE", referencedColumnName = "BANK_CODE")
    @JsonIgnore
    private Bank bank;

    @OneToOne
    @JoinColumn(name = "RESOURCE_ID", referencedColumnName = "RESOURCE_ID", insertable = false, updatable = false)
    private Resources resource;

    // Getters & Setters

    public String getResource_id() {
        return resource_id;
    }

    public void setResource_id(String resource_id) {
        this.resource_id = resource_id;
    }

    public Bank getBank() {
        return bank;
    }

    public void setBank(Bank bank) {
        this.bank = bank;
    }

    public Resources getResource() {
        return resource;
    }

    public void setResource(Resources resource) {
        this.resource = resource;
    }
}
