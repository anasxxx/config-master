package com.hps.configmaster_backend.entity;



import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;

@Entity(name="v_autho_activity_view")
public class V_auth_activity_view {
@Id
	@Column(name="REFERENCE_NUMBER")
	private String REFERENCE_NUMBER;
	
	
	

	
}
