package com.hps.configmaster_backend.entity;

import java.util.List;

import com.fasterxml.jackson.annotation.JsonIgnore;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.OneToOne;
import jakarta.persistence.Table;

@Entity
@Table(name="Resources")

public class Resources {
    @Id
	@Column(name="RESOURCE_ID", length=6)
	private String  resource_id;
	
    
    @Column(name="PRIS_BANK_CODE")
    private String codeBank;
   @Column(name="RESOURCE_CODE")
   private String resource_code;
	
	@Column(name="NODE_ID", length=4)
	private String node_id;
	
	@Column(name="ABRV_WORDING", length=16)
	private String abrv_wording;
	
   @Column(name="RESOURCE_LIVE", length=1)
	 private String resourceLive;
   
   @Column(name="PRIS_PROCESSING_STEP", length=3)
	 private String prisProcessingStep;
   @Column(name="PRIS_CONNECT_MODE", length=1)

	 private String prisConnectMode;

   @Column(name="WORDING", length=16)
	private String wording;
	
   
   @OneToOne(mappedBy = "resource")
   private RessourceParam ressourceParam;

	public String getResource_id() {
		return resource_id;
	}
	

	public void setResource_id(String resource_id) {
		this.resource_id = resource_id;
	}

	

	public String getNode_id() {
		return node_id;
	}

	public void setNode_id(String node_id) {
		this.node_id = node_id;
	}

	public String getAbrv_wording() {
		return abrv_wording;
	}

	public void setAbrv_wording(String abrv_wording) {
		this.abrv_wording = abrv_wording;
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

	@OneToMany(mappedBy = "resource")
    private List<ArchitectureConvergence> architectures;

	public String getResource_code() {
		return resource_code;
	}

	public void setResource_code(String resource_code) {
		this.resource_code = resource_code;
	}

	public String getCodeBank() {
		return codeBank;
	}

	public void setCodeBank(String codeBank) {
		this.codeBank = codeBank;
	}


	public String getWording() {
		return wording;
	}


	public void setWording(String wording) {
		this.wording = wording;
	}

	
	
	
	
	
	
}
