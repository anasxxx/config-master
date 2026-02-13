package com.hps.configmaster_backend.service.Imp;

import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.service.IConnexionSSHService;
import com.jcraft.jsch.ChannelExec;
import com.jcraft.jsch.JSch;
import com.jcraft.jsch.Session;
import org.slf4j.Logger;

@Service
public class ConnexionSSHServiceImp implements IConnexionSSHService  {
		

    private static final Logger logger = LoggerFactory.getLogger(ConnexionSSHServiceImp.class);

    

    @Override
    public Session openSession(String user,String host,String password) {
        try {
            JSch jsch = new JSch();
            Session session = jsch.getSession(user, host, 22);
            session.setPassword(password);
         session.setConfig("StrictHostKeyChecking", "no");
            session.connect();
            logger.info("Connexion SSH établie avec {}@{}", user, host);
            return session;
        } catch (Exception e) {
            logger.error("Erreur lors de la connexion SSH à {}@{} : {}", user, host, e.getMessage(), e);
            return null;
        }
    }

    
    
    
    
    @Override
    public void closeSession(Session session,String user, String host) {
        if (session != null && session.isConnected()) {
            session.disconnect();
            logger.info("Session SSH fermée pour {}@{}", user, host);
        }
    }
}
