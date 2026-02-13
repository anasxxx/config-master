package com.hps.configmaster_backend.service.Imp;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.models.BatchOfCampagneModule;
import com.hps.configmaster_backend.models.CampagneModule;
import com.hps.configmaster_backend.service.ICampagneService;
import com.hps.configmaster_backend.service.IConnexionSSHService;
import com.jcraft.jsch.ChannelExec;
import com.jcraft.jsch.ChannelShell;
import com.jcraft.jsch.Session;

@Service
public class CampagneServiceImp implements ICampagneService {

	
	
	@Autowired
    private IConnexionSSHService connexionSSHService;

    @Value("${unix.serverbo.host}")
    private String boHost;

    @Value("${unix.serverbo.user}")
    private String boUser;

    @Value("${unix.serverbo.password}")
    private String boPassword;

    @Value("${unix.server.pathBackOffice}")
    private String pathCompagneTestBackOffice;

    @Override
    public List<CampagneModule> getAllCampagne(String profile) {
        Session session = connexionSSHService.openSession(boUser, boHost, boPassword);
        List<CampagneModule> result = new ArrayList<>();

        if (session == null) {
            System.err.println("Erreur : Impossible d'établir une session SSH.");
            return result;
        }

        BufferedReader reader = null;
        ChannelExec channel = null;

        try {
            String command = "cd " + pathCompagneTestBackOffice + " && ls -d Campagne_*/";

            channel = (ChannelExec) session.openChannel("exec");
            channel.setCommand(command);
            channel.setInputStream(null);
            channel.setErrStream(System.err);

            InputStream in = channel.getInputStream();
            reader = new BufferedReader(new InputStreamReader(in));

            channel.connect();

            String line;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (!line.isEmpty()) {
                    String[] folders = line.split("\\s+"); 
                    for (String folder : folders) {
                        folder = folder.replace("/", ""); 
                        if (!folder.isEmpty()) {
                            CampagneModule campagne = new CampagneModule();
                            
                            if (!("full".equals(profile) && "Campagne_Light".equals(folder))) {
                                campagne.setCampagneName(folder);
                                result.add(campagne);
                            }

                        }
                    }
                }
            }

        }
        catch (Exception e) {
            e.printStackTrace();
        } finally {
            try {
                if (reader != null) reader.close();
            } catch (Exception ignored) {}
            if (channel != null && channel.isConnected()) channel.disconnect();
            session.disconnect();
        }

        return result;
    }

}