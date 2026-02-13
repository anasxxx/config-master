package com.hps.configmaster_backend.entity;

import java.time.LocalDateTime;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "st_Goldencopy_Version") // <- guillemets doubles pour forcer le nom exact
public class GoldenCopyVersion {

	@Id
	@Column(name="VERSION_ID")
	private String version_id;
	@Column(name="DATE_CREATE")
	private LocalDateTime date;
	@Column(name="DESCRIPTION")

	private String description;
	@Column(name="EXTENSION_NAME")
	private String extension_name;
	public String getVersion_id() {
		return version_id;
	}
	public void setVersion_id(String version_id) {
		this.version_id = version_id;
	}
	public LocalDateTime getDate() {
		return date;
	}
	public void setDate(LocalDateTime date) {
		this.date = date;
	}
	public String getExtension_name() {
		return extension_name;
	}
	public void setExtension_name(String extension_name) {
		this.extension_name = extension_name;
	}
	public String getDescription() {
		return description;
	}
	public void setDescription(String description) {
		this.description = description;
	}
	
	
	
	
	
}




