package com.hps.configmaster_backend.entity;

import java.sql.Date;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import jakarta.persistence.Temporal;
import jakarta.persistence.TemporalType;

@Entity
@Table(name = "st_nv_Patch_Convergence")
public class NvPatchConvergence {
	 @Id
	    @Column(name = "ID_PATCH", length = 6, nullable = false)
	    private String idPatch;

	    @Column(name = "DESCRIPTION", length = 2, nullable = false)
	    private String description;

	    @Column(name = "BANK_CODE", length = 6, nullable = false)
	    private String codeBancaire;

	    @Column(name = "OWNER", length = 16, nullable = false)
	    private String proprietaire;

	    @Temporal(TemporalType.DATE)
	    @Column(name = "DATE_CREATE", nullable = false)
	    private Date dateCreate;

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