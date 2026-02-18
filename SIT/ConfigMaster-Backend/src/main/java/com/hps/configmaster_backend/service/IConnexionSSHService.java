package com.hps.configmaster_backend.service;

import com.jcraft.jsch.Session;

public interface IConnexionSSHService {

	
    public Session openSession(String user,String host,String password) ;
    public void closeSession(Session session,String user,String host) ;

	}
