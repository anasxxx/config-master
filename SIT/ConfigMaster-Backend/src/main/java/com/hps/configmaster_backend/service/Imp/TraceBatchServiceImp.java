package com.hps.configmaster_backend.service.Imp;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.models.SimulationResultModule;
import com.hps.configmaster_backend.models.TraceBatchModel;
import com.hps.configmaster_backend.service.IConnexionSSHService;
import com.hps.configmaster_backend.service.ITraceBatchService;
import com.jcraft.jsch.ChannelShell;
import com.jcraft.jsch.Session;
@Service
public class TraceBatchServiceImp implements ITraceBatchService{

	
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
    private String expectedPromptTNR;
    @Value("${unix.server.promptSt}")
    private String expectedPromptSIT;

    private static final Pattern BATCH_PATTERN = Pattern.compile("Batch\\s*:\\s*(\\S+)", Pattern.CASE_INSENSITIVE);
    private static final Pattern STATUS_PATTERN = Pattern.compile("return\\s+code\\s*=\\s*\\d+.*?={6,}>\\s*\\x1B\\[[0-9;]*m(OK|NOK)", Pattern.CASE_INSENSITIVE | Pattern.DOTALL);
    private static final Pattern TASK_ID_PATTERN = Pattern.compile("Task\\s+id\\s*\\.{3,}\\s*:\\s*(\\d+)", Pattern.CASE_INSENSITIVE);
    private static final Pattern BUSINESS_DATE_PATTERN = Pattern.compile("Business\\s+Date\\s*\\.{3,}\\s*:\\s*(\\d{8})", Pattern.CASE_INSENSITIVE);
    private static final Pattern SYSTEM_DATE_PATTERN = Pattern.compile("System\\s+Date\\s*\\.{3,}\\s*:\\s*(\\d{8})", Pattern.CASE_INSENSITIVE);
    private static final Pattern POWERCARD_RETURN_CODE_PATTERN = Pattern.compile("PowerCARD\\s+return\\s+code.*?\\|\\s*([^|]+)\\s*\\|\\s*([^|]+)\\s*\\|", Pattern.DOTALL | Pattern.CASE_INSENSITIVE);
    private static final Pattern SHELL_RETURN_CODE_PATTERN = Pattern.compile("Shell\\s+return\\s+code.*?\\|\\s*([^|]+)\\s*\\|\\s*([^|]+)\\s*\\|", Pattern.DOTALL | Pattern.CASE_INSENSITIVE);

    private static final Pattern CARDHOLDER_PROCESSED_PATTERN = Pattern.compile("Cardholder\\s+Processed\\s*\\|\\s*(\\d+)\\s*\\|\\s*([^|]+)\\s*\\|", Pattern.CASE_INSENSITIVE | Pattern.DOTALL);

    private static final Pattern CARDHOLDER_PASSED_PATTERN = Pattern.compile("Cardholder\\s+Passed\\s*\\|\\s*(\\d+)\\s*\\|\\s*([^|]+)\\s*\\|", Pattern.CASE_INSENSITIVE | Pattern.DOTALL);

    private static final Pattern CARDHOLDER_REJECTED_PATTERN = Pattern.compile("Cardholder\\s+Rejected\\s*\\|\\s*(\\d+)\\s*\\|\\s*([^|]+)\\s*\\|", Pattern.CASE_INSENSITIVE | Pattern.DOTALL);

    private static final Pattern ANSI_VALUE_PATTERN = Pattern.compile("(\\d+|PWC-\\d+)\\s*\\x1B\\[[0-9;]*m([^\\x1B]*)\\x1B\\[[m]", Pattern.CASE_INSENSITIVE);

    
    
    
	@Override
	public List<TraceBatchModel> getTraceOfBatch(String campagne, String batch) throws IOException {

		  List<TraceBatchModel> results = new ArrayList<>();
		  TraceBatchModel currentResult = null;

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
	            System.out.println("Campagne: " + campagne);

	            writer.write("cd " + path + "\n");
	            writer.flush();
	            Thread.sleep(500);

	            writer.write("dir=$(ls -d cnv_main_*/ | head -n1)\n");
	            writer.flush();
	            Thread.sleep(500);

	            writer.write("cd \"$dir\"\n");
	            writer.flush();
	            Thread.sleep(500);
	            writer.write("cd \"END_OF_DAY\"\n");  // Fixed: added opening quote
	            writer.flush();
	            Thread.sleep(500);
	            
	            writer.write("dir=$(ls -d *" + batch.toUpperCase() + "*/ | head -n1)\n");
	            writer.flush();
	            Thread.sleep(500);
	            
	            writer.write("cd \"$dir\"\n");
	            writer.flush();
	            Thread.sleep(500);
	            writer.write("pwd\n");
	            writer.flush();
	            Thread.sleep(500);
	            
	            writer.write("cat Synthese_Action.log\n");
	            writer.flush();
	            Thread.sleep(10000); // attendre un peu avant de commencer la lecture
	           
	            String line;
	            int lineNumber = 0;
	            long timeoutMs = 3600 * 1000;
	            long startTime = System.currentTimeMillis();
	            String expectedPath = "pwrtnrbo:mlbappuat1:/pwrcard/pwrcarbo/usr/" + campagne + "/tools_ptt_cnv/RESULT_TEST";
	            boolean fileContentStarted = false;
	            boolean fileContentEnded = false;
	            
	            while ((line = reader.readLine()) != null && System.currentTimeMillis() - startTime < timeoutMs) {
	                lineNumber++;

	                // Affiche la sortie du terminal dans la console/logs
	                logger.info("UNIX OUTPUT >> {}", line);

	                try {
	                    // Détecter le début du contenu du fichier (après la commande cat)
	                    if (line.trim().isEmpty() || line.contains("cat Synthese_de_campagne.log")) {
	                        continue;
	                    }
	                    
	                    // Détecter la fin du fichier (retour au prompt)
	                    if (line.contains(expectedPromptTNR)|| line.contains(expectedPromptSIT) || line.matches(".*\\$\\s*$")) {
	                        if (fileContentStarted) {
	                            fileContentEnded = true;
	                            logger.info("Fin du contenu du fichier détectée");
	                            break;
	                        }
	                        continue;
	                    }
	                    
	                    // Marquer le début du contenu du fichier
	                    if (!fileContentStarted && (line.contains("Batch") || line.contains("Task") || 
	                        line.contains("Business Date") || line.contains("System Date"))) {
	                        fileContentStarted = true;
	                        logger.info("Début du contenu du fichier détecté");
	                    }
	                    
	                    // Ne traiter que si on est dans le contenu du fichier
	                    if (fileContentStarted && !fileContentEnded) {
	                        Matcher batchMatcher = BATCH_PATTERN.matcher(line);
	                        if (batchMatcher.find()) {
	                            if (currentResult != null) {
	                                results.add(currentResult);
	                            }
	                            currentResult = new TraceBatchModel();
	                            currentResult.setBatchName(batchMatcher.group(1).trim());
	                            logger.info("Nouveau batch trouvé: {}", currentResult.getBatchName());
	                            continue;
	                        }

	                        if (currentResult != null) {
	                            parseStatus(line, currentResult);
	                            parseTaskId(line, currentResult);
	                            parseBusinessDate(line, currentResult);
	                            parseSystemDate(line, currentResult);
	                            parsePowerCardReturnCode(line,currentResult);
	                            parseShellReturnCode(line,currentResult);
	                            parseCardholderProcessed(line, currentResult);
	                            parseCardholderPassed(line, currentResult);
	                            parseCardholderRejected(line, currentResult);
	                            
	                        }
	                    }
	                } catch (Exception e) {
	                    logger.warn("Erreur à la ligne {}: {}", lineNumber, e.getMessage());
	                }

	                // Sortir si le fichier a été entièrement lu
	                if (fileContentEnded) {
	                    break;
	                }

	                if (channel.isClosed()) {
	                    logger.info(">> Channel fermé");
	                    break;
	                }
	            }

	            // Envoyer exit seulement après avoir lu tout le fichier
	            if (!channel.isClosed()) {
	                writer.write("exit\n");
	                writer.flush();
	                Thread.sleep(500);
	            }

	            if (currentResult != null) {
	                results.add(currentResult);
	                logger.debug("Dernier batch ajouté : {}", currentResult.getBatchName());
	            }

	            logger.info("Parsing terminé. Total : {} batches", results.size());
	            return results;

	        } catch (Exception e) {
	            logger.error("Erreur pendant le parsing : {}", e.getMessage(), e);
	            throw new IOException("Erreur de parsing", e);
	        } finally {
	            try { if (reader != null) reader.close(); } catch (IOException ignored) {}
	            try { if (writer != null) writer.close(); } catch (IOException ignored) {}
	            if (channel != null && channel.isConnected()) channel.disconnect();
	            if (session != null && session.isConnected()) session.disconnect();
	        }

	}
	 private void parseStatus(String line, TraceBatchModel result) {
	        Matcher m = STATUS_PATTERN.matcher(line);
	        if (m.find()) {
	            result.setBatchStatus(cleanAnsiCodes(m.group(1).trim()));
	            logger.debug("Statut pour {} : {}", result.getBatchName(), result.getBatchStatus());
	        }
	    }
	  private void parseTaskId(String line, TraceBatchModel result) {
	        Matcher m = TASK_ID_PATTERN.matcher(line);
	        if (m.find()) result.setTaskId(m.group(1).trim());
	    }

	    private void parseBusinessDate(String line, TraceBatchModel result) {
	        Matcher m = BUSINESS_DATE_PATTERN.matcher(line);
	        if (m.find()) result.setBusinessDate(m.group(1).trim());
	    }

	    private void parseSystemDate(String line, TraceBatchModel result) {
	        Matcher m = SYSTEM_DATE_PATTERN.matcher(line);
	        if (m.find()) result.setSystemDate(m.group(1).trim());
	    }

	    
	    // Méthodes commentées - à décommenter et corriger selon la structure de SimulationResultModule
	    private void parsePowerCardReturnCode(String line, TraceBatchModel result) {
	        Matcher m = POWERCARD_RETURN_CODE_PATTERN.matcher(line);
	        if (m.find()) {
	            result.getPowerCardReturnCodes().add(cleanAnsiCodes(m.group(1).trim()));
	            result.getPowerCardReturnCodes().add(cleanAnsiCodes(m.group(2).trim()));
	        }
	    }

	    private void parseShellReturnCode(String line, TraceBatchModel result) {
	        Matcher m = SHELL_RETURN_CODE_PATTERN.matcher(line);
	        if (m.find()) {
	            result.getShellReturnCodes().add(cleanAnsiCodes(m.group(1).trim()));
	            result.getShellReturnCodes().add(cleanAnsiCodes(m.group(2).trim()));
	        }
	    }
	    private void parseCardholderProcessed(String line, TraceBatchModel result) {
	        Matcher m = CARDHOLDER_PROCESSED_PATTERN.matcher(line);
	        if (m.find()) {
	            String expected = cleanAnsiCodes(m.group(1).trim());
	            String obtained = cleanAnsiCodes(m.group(2).trim());
	            
	            // Supposons que TraceBatchModel a des méthodes pour les cardholder data
	             result.getCardholder_Processed().add(expected);
	             result.getCardholder_Processed().add(obtained);
	            
	            logger.debug("Cardholder Processed - Expected: {}, Obtained: {}", expected, obtained);
	        }
	    }

	    private void parseCardholderPassed(String line, TraceBatchModel result) {
	        Matcher m = CARDHOLDER_PASSED_PATTERN.matcher(line);
	        if (m.find()) {
	            String expected = cleanAnsiCodes(m.group(1).trim());
	            String obtained = cleanAnsiCodes(m.group(2).trim());
	            
	             result.getCardholder_Passed().add(expected);
	             result.getCardholder_Passed().add(obtained);
	            
	            logger.debug("Cardholder Passed - Expected: {}, Obtained: {}", expected, obtained);
	        }
	    }

	    private void parseCardholderRejected(String line, TraceBatchModel result) {
	        Matcher m = CARDHOLDER_REJECTED_PATTERN.matcher(line);
	        if (m.find()) {
	            String expected = cleanAnsiCodes(m.group(1).trim());
	            String obtained = cleanAnsiCodes(m.group(2).trim());
	            
	             result.getCardholder_Rejected().add(expected);
	             result.getCardholder_Rejected().add(obtained);
	            
	            logger.debug("Cardholder Rejected - Expected: {}, Obtained: {}", expected, obtained);
	        }
	    }
	    
	    private String cleanAnsiCodes(String text) {
	        return text != null ? text.replaceAll("\\x1B\\[[0-9;]*m", "") : null;
	    }
	
	
	
}

