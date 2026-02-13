package com.hps.configmaster_backend.models;

public class PackageModule {

	 private String name;
	    private String type;
	    private String ddl;
		
	    
		public PackageModule(String name, String type, String ddl) {
			super();
			this.name = name;
			this.type = type;
			this.ddl = ddl;
		}
		public String getType() {
			return type;
		}
		public void setType(String type) {
			this.type = type;
		}
		public String getDdl() {
			return ddl;
		}
		public void setDdl(String ddl) {
			this.ddl = ddl;
		}
		public void setName(String name) {
			this.name = name;
		}
		public String getName() {
			return name;
		}
		
}