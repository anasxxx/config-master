package com.hps.configmaster_backend.entity;

import java.util.ArrayList;
import java.util.List;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.IdClass;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.JoinColumns;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.Table;


@Entity

@Table(name="st_Architecture_Convergence")
public class ArchitectureConvergence {

    @Id
    @Column(name = "RESOURCE_ID", length = 6)
    private String resourceId;

    @Column(name = "RESOURCE_CODE", length = 2)
    private String codeRessource;

    @Column(name = "NODE_ID", length = 4)
    private String nodeId;

    @Column(name = "ABRV_WORDING", length = 16)
    private String abrvWording;

    @Column(name = "WORDING", length = 32)
    private String libelle;
    
    @ManyToOne
   
        @JoinColumn(name = "resource_id", referencedColumnName = "resource_id", insertable = false, updatable = false)
    
    private Resources resource;
 
    public ArchitectureConvergence() {
    }
    
  

	public String getResourceId() {
		return resourceId;
	}

	public void setResourceId(String resourceId) {
		this.resourceId = resourceId;
	}

	public String getCodeRessource() {
		return codeRessource;
	}

	public void setCodeRessource(String codeRessource) {
		this.codeRessource = codeRessource;
	}

	public String getNodeId() {
		return nodeId;
	}

	public void setNodeId(String nodeId) {
		this.nodeId = nodeId;
	}

	public String getAbrvWording() {
		return abrvWording;
	}

	public void setAbrvWording(String abrvWording) {
		this.abrvWording = abrvWording;
	}

	public String getLibelle() {
		return libelle;
	}

	public void setLibelle(String libelle) {
		this.libelle = libelle;
	}

	public ArchitectureConvergence(String resourceId, String codeRessource, String nodeId, String abrvWording,
			String libelle) {
		super();
		this.resourceId = resourceId;
		this.codeRessource = codeRessource;
		this.nodeId = nodeId;
		this.abrvWording = abrvWording;
		this.libelle = libelle;
	}
    
    
    
}