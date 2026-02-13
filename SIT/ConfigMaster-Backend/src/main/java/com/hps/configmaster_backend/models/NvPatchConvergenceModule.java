package com.hps.configmaster_backend.models;

import java.sql.Date;

public class NvPatchConvergenceModule {



	    private String idPatch;
	    private String description;
	    private String codeBancaire;
	    private String proprietaire;
	    private Date dateCreate;

	    // Constructeurs
	  

	    // Getters et Setters
	    public String getIdPatch() {
	        return idPatch;
	    }

	    public void setIdPatch(String idPatch) {
	        this.idPatch = idPatch;
	    }

	    public String getDescription() {
	        return description;
	    }

	    public void setDescription(String description) {
	        this.description = description;
	    }

	    public String getCodeBancaire() {
	        return codeBancaire;
	    }

	    public void setCodeBancaire(String codeBancaire) {
	        this.codeBancaire = codeBancaire;
	    }

	    public String getProprietaire() {
	        return proprietaire;
	    }

	    public void setProprietaire(String proprietaire) {
	        this.proprietaire = proprietaire;
	    }

	    public Date getDateCreate() {
	        return dateCreate;
	    }

	    public void setDateCreate(Date dateCreate) {
	        this.dateCreate = dateCreate;
	    }
	}
