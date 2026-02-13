package com.hps.configmaster_backend.service.Imp;

import com.hps.configmaster_backend.models.BatchOfCampagneModule;
import com.hps.configmaster_backend.service.IBatchOfCampagneService;
import com.hps.configmaster_backend.service.IConnexionSSHService;
import com.jcraft.jsch.ChannelShell;
import com.jcraft.jsch.Session;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

@Service
public class BatchOfCampagneServiceImp implements IBatchOfCampagneService {

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
    public List<BatchOfCampagneModule> getUsecasOfCampaign(String campagne) {
        Session session = connexionSSHService.openSession(boUser, boHost, boPassword);
        List<BatchOfCampagneModule> result = new ArrayList<>();

        if (session == null) {
            System.err.println("Erreur : Impossible d'établir une session SSH.");
            return result;
        }

        try {
            String output = executeInteractiveScript(session,campagne);
            System.out.println("== OUTPUT ==\n" + output);

            for (String line : output.split("\n")) {
                if (line.contains("-batch:")) {
                    int index = line.indexOf("-batch:") + 7; // 7 = longueur de "-batch:"
                    String remaining = line.substring(index).trim(); // récupère ce qui vient après "-batch:"
                    String batchName = remaining.split("\\s+")[0]; // prend le premier mot (jusqu’à l’espace)

                    BatchOfCampagneModule module = new BatchOfCampagneModule();
                    if(!batchName.equals("NULL"))
                    {   module.setBatchName(batchName);
                    result.add(module);
                }
            }}

            
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            session.disconnect();
        }

        return result;
    }

    private String executeInteractiveScript(Session session ,String campagne) throws Exception {
        ChannelShell channel = (ChannelShell) session.openChannel("shell");
        InputStream inputStream = channel.getInputStream();
        OutputStream outputStream = channel.getOutputStream();
        
        channel.connect();
        
        BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
        BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(outputStream));
        
        try {
            // Envoyer les commandes interactives
        	String path = pathCompagneTestBackOffice + campagne + "/tools_ptt_cnv";
        	writer.write("cd " + path + "\n");
            writer.flush();
            Thread.sleep(500);
            
            writer.write("./PWC_campagne_CNV.sh -s -q\n");
            writer.flush();
            Thread.sleep(1000);
            
            writer.write("l 1\n");
            writer.flush();
            Thread.sleep(1000);
            
            writer.write("q\n");
            writer.flush();
            Thread.sleep(500);
            
            // AJOUT CRUCIAL : Fermer le shell après les commandes
            writer.write("exit\n");
            writer.flush();
            
            // Lire la sortie avec TIMEOUT au lieu de boucle infinie
            StringBuilder output = new StringBuilder();
            boolean endDetected = false;
            long startTime = System.currentTimeMillis();
            long timeoutMs = 3600 * 1000; // 30 secondes de timeout
            
            while (System.currentTimeMillis() - startTime < timeoutMs) {
                // VERIFICATION CRUCIALE : vérifier si des données sont disponibles
                if (reader.ready()) {
                    char[] buffer = new char[1024];
                    int charsRead = reader.read(buffer);
                    if (charsRead > 0) {
                        String chunk = new String(buffer, 0, charsRead);
                        output.append(chunk);
                        System.out.print(chunk); // Affichage en temps réel
                        
                        // Vérifier les conditions de fin dans le chunk complet
                        String currentOutput = output.toString();
                        if (currentOutput.contains("End of script") || 
                            currentOutput.contains("Goodbye") ||
                            currentOutput.contains("logout") ||
                            currentOutput.contains("Connection closed") ||
                            channel.isClosed()) {
                            endDetected = true;
                            System.out.println("\n>> Condition de fin détectée");
                            break;
                        }
                    }
                } else {
                    // Pas de données disponibles, attendre un peu
                    Thread.sleep(100);
                    
                    // Vérifier si le channel est fermé
                    if (channel.isClosed()) {
                        System.out.println("\n>> Channel fermé");
                        break;
                    }
                }
            }
            
            // Si timeout atteint
            if (System.currentTimeMillis() - startTime >= timeoutMs) {
                System.out.println("\n>> Timeout atteint (" + (timeoutMs/1000) + "s)");
            }
            
            return output.toString();
            
        } finally {
            // Nettoyage garanti
            try {
                if (writer != null) {
                    writer.close();
                }
            } catch (Exception e) {
                System.err.println("Erreur fermeture writer: " + e.getMessage());
            }
            
            try {
                if (reader != null) {
                    reader.close();
                }
            } catch (Exception e) {
                System.err.println("Erreur fermeture reader: " + e.getMessage());
            }
            
            if (channel != null && channel.isConnected()) {
                channel.disconnect();
            }
        }
    }

    
}
