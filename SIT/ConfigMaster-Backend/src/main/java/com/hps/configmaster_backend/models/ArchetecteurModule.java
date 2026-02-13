package com.hps.configmaster_backend.models;

public class ArchetecteurModule {
    private String resourceId;
    private String libelle;
    private String resourceLive;
    private String prisProcessingStep;
    private String prisConnectMode;
    
    // Constructeur vide nécessaire pour JPA
    public ArchetecteurModule() {
    }
    
    // Constructeur utilisé dans la requête JPQL
    public ArchetecteurModule(String resourceId, String libelle, String resourceLive, 
                             String prisProcessingStep, String prisConnectMode) {
        this.resourceId = resourceId;
        this.libelle = libelle;
        this.resourceLive = resourceLive;
        this.prisProcessingStep = prisProcessingStep;
        this.prisConnectMode = prisConnectMode;
    }

	public String getResourceId() {
		return resourceId;
	}

	public void setResourceId(String resourceId) {
		this.resourceId = resourceId;
	}

	public String getLibelle() {
		return libelle;
	}

	public void setLibelle(String libelle) {
		this.libelle = libelle;
	}

	public String getResourceLive() {
		return resourceLive;
	}

	public void setResourceLive(String resourceLive) {
		this.resourceLive = resourceLive;
	}

	public String getPrisProcessingStep() {
		return prisProcessingStep;
	}

	public void setPrisProcessingStep(String prisProcessingStep) {
		this.prisProcessingStep = prisProcessingStep;
	}

	public String getPrisConnectMode() {
		return prisConnectMode;
	}

	public void setPrisConnectMode(String prisConnectMode) {
		this.prisConnectMode = prisConnectMode;
	}
    
    // Getters et setters
    // ...
}