package com.hps.configmaster_backend.service.Imp;

import com.hps.configmaster_backend.models.BatcheResultModule;
import com.hps.configmaster_backend.models.RapportResultModule;
import com.hps.configmaster_backend.models.SimulationResultModule;
import com.hps.configmaster_backend.service.IConnexionSSHService;
import com.hps.configmaster_backend.service.ISimulationResulService;
import com.jcraft.jsch.ChannelSftp;
import com.jcraft.jsch.ChannelShell;
import com.jcraft.jsch.Session;
import com.jcraft.jsch.SftpATTRS;
import com.jcraft.jsch.SftpException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class SimulationResulServiceImp implements ISimulationResulService {

    private static final Logger logger = LoggerFactory.getLogger(SimulationResulServiceImp.class);

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

    @Value("${unix.server.promptTn}")
    private String expectedPrompt;

    // Patterns corrigés
    private static final Pattern BATCH_PATTERN = Pattern.compile("Batch\\s*:\\s*(\\S+)", Pattern.CASE_INSENSITIVE);
    private static final Pattern STATUS_PATTERN = Pattern.compile("return\\s+code\\s*=\\s*\\d+.*?={6,}>\\s*\\x1B\\[[0-9;]*m(OK|NOK)", Pattern.CASE_INSENSITIVE | Pattern.DOTALL);
   
    // Patterns pour les rapports
    private static final Pattern COMMENT_PATTERN = Pattern.compile("Comment\\s*:\\s*(.+)");
    private static final Pattern BLOCK_START_PATTERN = Pattern.compile("Report_-_X\\d+");
    private static final Pattern STATUS_REPORT_PATTERN = Pattern.compile("successfully.*?=>\\s+\\x1B\\[92m(\\w+)\\x1B\\[0m");
    private static final Pattern CLEAN_ANSI = Pattern.compile("\\x1B\\[[0-9;]*[mK]");

    @Override
    public SimulationResultModule parseLogFile(String campagne) throws IOException {
        SimulationResultModule results = new SimulationResultModule();
        BatcheResultModule currentResult = null;
        RapportResultModule rapportResult = null;
        
        Session session = connexionSSHService.openSession(boUser, boHost, boPassword);
        if (session == null) {
            logger.error("Erreur : Impossible d'établir une session SSH.");
            return results;
        }

        ChannelShell channel = null;
        BufferedReader reader = null;
        BufferedWriter writer = null;

        try {
            channel = (ChannelShell) session.openChannel("shell");
            InputStream inputStream = channel.getInputStream();
            OutputStream outputStream = channel.getOutputStream();

            channel.connect();

            reader = new BufferedReader(new InputStreamReader(inputStream));
            writer = new BufferedWriter(new OutputStreamWriter(outputStream));

            String path = pathCompagneTestBackOffice + campagne + "/tools_ptt_cnv/RESULT_TEST";
            logger.info("Campagne path: {}", path);

            // Envoi des commandes shell
            writer.write("cd " + path + "\n");
            writer.flush();
            Thread.sleep(300);

            writer.write("dir=$(ls -d cnv_main_*/ | head -n1)\n");
            writer.flush();
            Thread.sleep(300);

            writer.write("cd \"$dir\"\n");
            writer.flush();
            Thread.sleep(300);

            writer.write("cat Synthese_de_campagne.log\n");
            writer.flush();
            Thread.sleep(1000);

            String line;
            int lineNumber = 0;
            long timeoutMs = 60_000; // 1 minute max
            long startTime = System.currentTimeMillis();

            boolean fileContentStarted = false;
            boolean fileContentEnded = false;

            while ((line = reader.readLine()) != null && (System.currentTimeMillis() - startTime < timeoutMs)) {
                lineNumber++;
                logger.info("UNIX OUTPUT >> {}", line);

                // Ignorer les lignes vides ou la commande elle-même
                if (line.trim().isEmpty() || line.contains("cat Synthese_de_campagne.log")) {
                    continue;
                }

                // Début du contenu
                if (!fileContentStarted && line.contains("launch_campaign")) {
                    fileContentStarted = true;
                    logger.info("Début du contenu du fichier détecté (ligne {})", lineNumber);
                }

                // Détection de la fin : retour au prompt ou chemin complet
                if (fileContentStarted && (line.contains("/tools_ptt_cnv/RESULT_TEST") || line.contains(" cat: Synthese_de_campagne.log: No such file or directory"))) {
                    
                	fileContentEnded = true;
                    logger.info("Fin du contenu détectée (ligne {})", lineNumber);
                    break;
                }

                if (fileContentStarted && !fileContentEnded) {
                    // Traitement des batches
                    Matcher batchMatcher = BATCH_PATTERN.matcher(line);
                    if (batchMatcher.find()) {
                        // Ajouter le batch précédent s'il existe
                        if (currentResult != null) {
                            results.getBatcheResultModule().add(currentResult);
                        }
                        currentResult = new BatcheResultModule();
                        currentResult.setBatchName(batchMatcher.group(1).trim());
                        logger.info("Batch trouvé : {}", currentResult.getBatchName());
                    }

                    // Traitement des rapports
                    Matcher reportMatcher = BLOCK_START_PATTERN.matcher(line);
                    if (reportMatcher.find()) {
                        // Ajouter le rapport précédent s'il existe
                        if (rapportResult != null) {
                            results.getFailedReports().add(rapportResult);
                        }
                        rapportResult = new RapportResultModule();
                        rapportResult.setRapportName(reportMatcher.group());
                        logger.info("Rapport trouvé : {}", rapportResult.getRapportName());
                    }

                    // Parsing des données pour le batch actuel
                    if (currentResult != null) {
                        parseStatus(line, currentResult);
                      
                    }
                    
                    // Parsing des données pour le rapport actuel
                    if (rapportResult != null) {
                        parseStatusPattern(line, rapportResult);
                       
                    }
                }

                if (channel.isClosed()) {
                    logger.warn("Channel SSH fermé prématurément.");
                    break;
                }
            }

            // Ajout des derniers résultats
            if (currentResult != null) {
                results.getBatcheResultModule().add(currentResult);
                logger.debug("Dernier batch ajouté : {}", currentResult.getBatchName());
            }
            
            if (rapportResult != null) {
                results.getFailedReports().add(rapportResult);
                logger.debug("Dernier rapport ajouté : {}", rapportResult.getRapportName());
            }

            // Exit SSH proprement
            if (!channel.isClosed()) {
                writer.write("exit\n");
                writer.flush();
                Thread.sleep(300);
            }

            logger.info("Parsing terminé avec {} batch(es) et {} rapport(s).", 
                       results.getBatcheResultModule().size(), 
                       results.getFailedReports().size());
            return results;

        } catch (Exception e) {
            logger.error("Erreur pendant le parsing : {}", e.getMessage(), e);
            throw new IOException("Erreur de parsing", e);
        } finally {
            closeResources(reader, writer, channel, session);
        }
    }

    @Override
    public byte[] downloadFileFromSftp(String campagne, String batchName) {
        Session session = connexionSSHService.openSession(boUser, boHost, boPassword);
        if (session == null) {
            logger.error("Erreur : Impossible d'établir une session SSH.");
            return null;
        }
        
        ChannelSftp sftpChannel = null;
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        
        try {
            sftpChannel = (ChannelSftp) session.openChannel("sftp");
            sftpChannel.connect();
            
            String targetFileName = navigateAndFindFile(sftpChannel, campagne, batchName);
            if (targetFileName == null) {
                logger.error("Fichier cible non trouvé pour la campagne {} et le batch {}", campagne, batchName);
                return null;
            }
            
            // Télécharger le fichier
            logger.info("Début du téléchargement du fichier : {}", targetFileName);
            sftpChannel.get(targetFileName, outputStream);
            
            logger.info("Fichier téléchargé avec succès. Taille : {} octets", outputStream.size());
            return outputStream.toByteArray();
            
        } catch (Exception e) {
            logger.error("Erreur lors du téléchargement SFTP du fichier {} : {}", batchName, e.getMessage(), e);
            return null;
        } finally {
            closeResources(outputStream, sftpChannel, session);
        }
    }

    private String navigateAndFindFile(ChannelSftp sftpChannel, String campagne, String batchName) {
        try {
            // Naviguer vers le répertoire RESULT_TEST
            String resultTestPath = pathCompagneTestBackOffice + campagne + "/tools_ptt_cnv/RESULT_TEST";
            logger.info("Navigation vers : {}", resultTestPath);
            
            sftpChannel.cd(resultTestPath);
            
            // Trouver le dossier cnv_main_*
            String dynamicDirName = findDirectory(sftpChannel, "cnv_main_");
            if (dynamicDirName == null) {
                logger.error("Aucun dossier commençant par 'cnv_main_' trouvé");
                return null;
            }
            
            // Gestion spéciale pour les rapports
            if (batchName.matches("^Report.*")) {
                return handleReportBatch(sftpChannel, dynamicDirName, batchName);
            } else {
                return handleRegularBatch(sftpChannel, dynamicDirName, batchName);
            }
            
        } catch (SftpException e) {
            logger.error("Erreur de navigation SFTP : {}", e.getMessage());
            return null;
        }
    }

    private String handleReportBatch(ChannelSftp sftpChannel, String dynamicDirName, String batchName) throws SftpException {
        // Extraire le numéro du rapport
        String numberPart = batchName.replaceAll("^Report(\\d+).*", "$1");
        if (numberPart.equals(batchName)) {
            logger.error("Impossible d'extraire le numéro du rapport de : {}", batchName);
            return null;
        }
        
        // Naviguer vers PWC_REPORTS
        String pathRapport = dynamicDirName + "/PWC_REPORTS";
        logger.info("Navigation vers le répertoire des rapports : {}", pathRapport);
        sftpChannel.cd(pathRapport);
        
        // Trouver le dossier correspondant au numéro
        String dynamicDirRapport = findDirectory(sftpChannel, numberPart);
        if (dynamicDirRapport == null) {
            logger.error("Aucun dossier commençant par '{}' trouvé dans PWC_REPORTS", numberPart);
            return null;
        }
        
        // Naviguer vers le dossier du rapport et chercher dans data
        sftpChannel.cd(dynamicDirRapport + "/data");
        return findFirstFile(sftpChannel);
    }

    private String handleRegularBatch(ChannelSftp sftpChannel, String dynamicDirName, String batchName) throws SftpException {
        // Naviguer vers END_OF_DAY
        String endOfDayPath = dynamicDirName + "/END_OF_DAY";
        logger.info("Navigation vers : {}", endOfDayPath);
        sftpChannel.cd(endOfDayPath);
        
        // Trouver le dossier batch
        String batchDirName = findDirectory(sftpChannel, batchName.toUpperCase());
        if (batchDirName == null) {
            logger.error("Aucun dossier commençant par '{}' trouvé", batchName.toUpperCase());
            return null;
        }
        
        // Naviguer vers le dossier data
        sftpChannel.cd(batchDirName + "/data");
        return findFirstFile(sftpChannel);
    }

    private String findDirectory(ChannelSftp sftpChannel, String prefix) throws SftpException {
        Vector<ChannelSftp.LsEntry> fileList = sftpChannel.ls(".");
        for (ChannelSftp.LsEntry entry : fileList) {
            if (entry.getAttrs().isDir() && 
                !entry.getFilename().equals(".") && 
                !entry.getFilename().equals("..") &&
                entry.getFilename().startsWith(prefix)) {
                logger.info("Dossier trouvé : {}", entry.getFilename());
                return entry.getFilename();
            }
        }
        logger.warn("Aucun dossier trouvé avec le préfixe : {}", prefix);
        return null;
    }

    private String findFirstFile(ChannelSftp sftpChannel) throws SftpException {
        Vector<ChannelSftp.LsEntry> fileList = sftpChannel.ls(".");
        for (ChannelSftp.LsEntry entry : fileList) {
            if (!entry.getAttrs().isDir() && 
                !entry.getFilename().equals(".") && 
                !entry.getFilename().equals("..")) {
                logger.info("Fichier trouvé : {}", entry.getFilename());
                return entry.getFilename();
            }
        }
        logger.warn("Aucun fichier trouvé dans le répertoire courant");
        return null;
    }
    // Méthodes de parsing
    private void parseStatus(String line, BatcheResultModule result) {
        Matcher m = STATUS_PATTERN.matcher(line);
        if (m.find()) {
            result.setBatchStatu(cleanAnsiCodes(m.group(1).trim()));
            logger.debug("Statut pour {} : {}", result.getBatchName(), result.getBatchStatu());
        }
    }
    
   

    
    private void parseStatusPattern(String line, RapportResultModule result) {
        Matcher m = STATUS_REPORT_PATTERN.matcher(line);
        if (m.find()) {
            result.setStatu(cleanAnsiCodes(m.group(1).trim()));
            logger.debug("Statut rapport pour {} : {}", result.getRapportName(), result.getStatu());
        }
    }
    
   

    private String cleanAnsiCodes(String text) {
        return text != null ? CLEAN_ANSI.matcher(text).replaceAll("") : null;
    }
    
    // Méthodes utilitaires pour fermer les ressources
    private void closeResources(BufferedReader reader, BufferedWriter writer, ChannelShell channel, Session session) {
        try { if (reader != null) reader.close(); } catch (IOException ignored) {}
        try { if (writer != null) writer.close(); } catch (IOException ignored) {}
        if (channel != null && channel.isConnected()) channel.disconnect();
        if (session != null && session.isConnected()) session.disconnect();
    }
    
    private void closeResources(ByteArrayOutputStream outputStream, ChannelSftp sftpChannel, Session session) {
        try { if (outputStream != null) outputStream.close(); } catch (IOException ignored) {}
        if (sftpChannel != null && sftpChannel.isConnected()) sftpChannel.disconnect();
        if (session != null && session.isConnected()) session.disconnect();
    }
}