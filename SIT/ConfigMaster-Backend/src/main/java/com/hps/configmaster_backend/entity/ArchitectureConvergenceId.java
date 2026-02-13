package com.hps.configmaster_backend.entity;

import java.io.Serializable;

import jakarta.persistence.Column;
import jakarta.persistence.Embeddable;

@Embeddable
public class ArchitectureConvergenceId implements Serializable {
    
    @Column(name = "RESOURCE_ID", length = 6)
    private String resourceId;

    @Column(name = "NODE_ID", length = 4)
    private String nodeId;

	public String getResourceId() {
		return resourceId;
	}

	public void setResourceId(String resourceId) {
		this.resourceId = resourceId;
	}

	public String getNodeId() {
		return nodeId;
	}

	public void setNodeId(String nodeId) {
		this.nodeId = nodeId;
	}


}

