package com.hps.configmaster_backend.service;

public interface IGoldenCopyVersionService {

	
	public String saveGoldenCopyVersion(String description);
	public byte[] exportAsZip(String description );

}
