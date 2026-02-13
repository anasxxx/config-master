package com.hps.configmaster_backend.service.Imp;

import com.hps.configmaster_backend.service.IConnexionSSHService;
import com.hps.configmaster_backend.service.ITNRScriptService;
import com.jcraft.jsch.ChannelShell;
import com.jcraft.jsch.Session;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.*;

@Service
public class TNRScriptService implements ITNRScriptService {

    @Autowired
    private IConnexionSSHService connexionSSHService;

    @Value("${unix.serverbo.host}")
    private String boHost;

    @Value("${unix.serverbo.user}")
    private String boUser;

    @Value("${unix.serverbo.password}")
    private String boPassword;

    @Value("${unix.serverof.host}")
    private String ofHost;

    @Value("${unix.serverof.user}")
    private String ofUser;

    @Value("${unix.serverof.password}")
    private String ofPassword;

    @Value("${unix.server.pathBackOffice}")
    private String pathCompagneTestBackOffice;

    @Value("${unix.server.pathOffline}")
    private String pathCompagneTestOffline;

    @Value("${unix.server.promptTn}")
    private String expectedPrompt;

    @Override
    public String runUnixScriptBackOffice(String compagne) {
        Session session = connexionSSHService.openSession(boUser, boHost, boPassword);
        if (session == null) {
            return "Erreur : Impossible d'établir une session SSH.";
        }

        try {
            return executeInteractiveScript(session, compagne);
        } catch (Exception e) {
            e.printStackTrace();
            return " Erreur d'exécution du script : " + e.getMessage();
        }
    }

    @Override
    public String runUnixScriptOffline(String campagne) {
        Session session = connexionSSHService.openSession(ofUser, ofHost, ofPassword);
        if (session == null) {
            return " Erreur : Impossible d'établir une session SSH.";
        }

        try {
            return executeInteractiveScript(session, campagne);
        } catch (Exception e) {
            e.printStackTrace();
            return " Erreur d'exécution du script : " + e.getMessage();
        }
    }

    private String executeInteractiveScript(Session session, String campagne) throws Exception {
        ChannelShell channel = (ChannelShell) session.openChannel("shell");
        InputStream inputStream = channel.getInputStream();
        OutputStream outputStream = channel.getOutputStream();
        String message;

        channel.connect();

        BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
        BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(outputStream));

        // Variables pour stocker les stats extraites
        String runningTime = null;
        Integer executedActions = null;
        Integer errorActions = null;
        Integer skippedActions = null;

        try {
            String path = pathCompagneTestBackOffice + campagne + "/tools_ptt_cnv";
            String pathR = pathCompagneTestBackOffice + campagne + "/tools_ptt_cnv/RESULT_TEST";

            writer.write("cd " + pathR + "\n");
            writer.flush();
            Thread.sleep(500);

            writer.write("find . -mindepth 1 -type d -exec rm -rf {} +\r\n");
            writer.flush();
            Thread.sleep(500);

            writer.write("cd ../../../../\n");
            writer.flush();
            Thread.sleep(500);

            writer.write("cd " + path + "\n");
            writer.flush();
            Thread.sleep(500);

            writer.write("./PWC_campagne_CNV.sh -s -q\n");
            writer.flush();
            Thread.sleep(1000);

            writer.write("1\n"); // si requis
            writer.flush();

            writer.write("q\n"); // si requis
            writer.flush();
            writer.write("exit\n");
            writer.flush();

            long startTime = System.currentTimeMillis();
            long timeoutMs = 3600 * 1000; // 1 heure = 3600000 ms
            boolean promptDetected = false;

            String line;
            StringBuilder output = new StringBuilder();

            while ((System.currentTimeMillis() - startTime < timeoutMs) && (line = reader.readLine()) != null) {
                output.append(line).append("\n");
                System.out.println(line); // affichage console

                // Detecte fin session
                if (line.trim().equals("logout")) {
                    promptDetected = true;
                    System.out.println(">> Prompt détecté, fin de l'exécution.");
                    break;
                }

                // --- Parsing des stats dans la sortie ---
                if (line.contains("Campaign running time")) {
                    runningTime = line.substring(line.indexOf(":") + 1).trim();
                } else if (line.contains("Number of executed actions")) {
                    executedActions = extractIntFromLine(line);
                } else if (line.contains("Number of actions in error")) {
                    errorActions = extractIntFromLine(line);
                } else if (line.contains("Number of actions skipped")) {
                    skippedActions = extractIntFromLine(line);
                }

                if (channel.isClosed()) {
                    break;
                }
            }

            // Construire le message final avec les stats détectées
            StringBuilder msgBuilder = new StringBuilder();
            if (errorActions == null || errorActions > 0 ) {
                msgBuilder.append("\n Le lancement de votre campagne s'est terminé avec des erreurs.\n");
            } else {
                msgBuilder.append("\n Le lancement de votre campagne s'est terminé avec succès.\n");
            }            if (runningTime != null) {
                msgBuilder.append("Campaign running time .....: ").append(runningTime).append("\n");
            }
            if (executedActions != null) {
                msgBuilder.append("Number of executed actions : ").append(executedActions).append("\n");
            }
            if (errorActions != null) {
                msgBuilder.append("Number of actions in error : ").append(errorActions).append("\n");
            }
            if (skippedActions != null) {
                msgBuilder.append("Number of actions skipped .: ").append(skippedActions).append("\n");
            }

            message = msgBuilder.toString();

            return message;

        } finally {
            try { writer.close(); } catch (Exception ignored) {}
            try { reader.close(); } catch (Exception ignored) {}
            if (channel.isConnected()) channel.disconnect();
        }
    }
    
    private Integer extractIntFromLine(String line) {
        String num = line.replaceAll("[^0-9]", "");
        if (num.isEmpty()) return null;
        try {
            return Integer.parseInt(num);
        } catch (NumberFormatException e) {
            return null;
        }



}
}