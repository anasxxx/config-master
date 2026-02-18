package com.hps.configmaster_backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "Country")
public class Country {

    @Id
    @Column(name = "COUNTRY_CODE", length = 3)
    private String countryCode;

    @Column(name = "WORDING", length = 32)
    private String wording;

    @Column(name = "ABRV_WORDING", length = 16)
    private String abrvWording;

    // Constructeur par défaut
    public Country() {
    }

    // Getters et Setters
    public String getCountryCode() {
        return countryCode;
    }

    public void setCountryCode(String countryCode) {
        this.countryCode = countryCode;
    }

    public String getWording() {
        return wording;
    }

    public void setWording(String wording) {
        this.wording = wording;
    }

    public String getAbrvWording() {
        return abrvWording;
    }

    public void setAbrvWording(String abrvWording) {
        this.abrvWording = abrvWording;
    }
}
