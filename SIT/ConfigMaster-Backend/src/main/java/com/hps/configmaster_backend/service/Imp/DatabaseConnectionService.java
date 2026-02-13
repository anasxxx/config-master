package com.hps.configmaster_backend.service.Imp;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.concurrent.TimeUnit;

public class DatabaseConnectionService {

    @Value("${spring.datasource.url}")
    private String jdbcUrl;
    
    @Value("${spring.datasource.username}")
    private String username;
    
    @Value("${spring.datasource.password}")
    private String password;
    
    @Value("${app.db.connection-script}")
    private String connectionScriptPath;
    
    @Value("${app.db.oracle-server}")
    private String oracleServer;
    
    @Value("${app.db.oracle-port}")
    private int oraclePort;
    
    @jakarta.annotation.PostConstruct
    public void initializeConnection() {
        if (!isDatabaseAccessible()) {
            try {
                System.out.println("La base de données n'est pas accessible. Exécution du script de connexion...");
                executeConnectionScript();
                
                // Attendre que la connexion soit établie
                int maxRetries = 5;
                int retryCount = 0;
                boolean connected = false;
                
                while (!connected && retryCount < maxRetries) {
                    System.out.println("Tentative de connexion à la base de données... (" + (retryCount + 1) + "/" + maxRetries + ")");
                    Thread.sleep(5000); // Attendre 5 secondes entre les tentatives
                    connected = isDatabaseAccessible();
                    retryCount++;
                }
                
                if (connected) {
                    System.out.println("Connexion à la base de données établie avec succès !");
                } else {
                    System.err.println("Impossible d'établir la connexion à la base de données après " + maxRetries + " tentatives.");
                    System.err.println("Veuillez vérifier vos paramètres de connexion et le script de connexion.");
                }
            } catch (Exception e) {
                System.err.println("Erreur lors de l'établissement de la connexion : " + e.getMessage());
                e.printStackTrace();
            }
        } else {
            System.out.println("Base de données déjà accessible.");
        }
    }
    
    private boolean isDatabaseAccessible() {
        // Vérifier d'abord si le serveur et le port sont accessibles
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress(oracleServer, oraclePort), 3000); // Timeout de 3 secondes
            System.out.println("Serveur Oracle accessible à " + oracleServer + ":" + oraclePort);
            
            // Ensuite, essayer d'établir une connexion JDBC
            try (Connection conn = DriverManager.getConnection(jdbcUrl, username, password)) {
                return conn.isValid(5); // Vérifier si la connexion est valide avec un timeout de 5 secondes
            } catch (SQLException e) {
                System.out.println("Serveur accessible mais connexion JDBC impossible : " + e.getMessage());
                return false;
            }
        } catch (IOException e) {
            System.out.println("Serveur Oracle inaccessible à " + oracleServer + ":" + oraclePort + " : " + e.getMessage());
            return false;
        }
    }
    
    private void executeConnectionScript() throws IOException {
        ProcessBuilder processBuilder = new ProcessBuilder("cmd.exe", "/c", connectionScriptPath);
        processBuilder.redirectErrorStream(true);
        Process process = processBuilder.start();
        
        // Lire la sortie du processus
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println("Script: " + line);
            }
        }
        
        // Attendre que le processus se termine avec un timeout
        try {
            if (!process.waitFor(60, TimeUnit.SECONDS)) {
                process.destroyForcibly();
                System.err.println("L'exécution du script a été interrompue après 60 secondes (timeout).");
            } else {
                int exitCode = process.exitValue();
                System.out.println("Le script s'est terminé avec le code : " + exitCode);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            System.err.println("L'exécution du script a été interrompue : " + e.getMessage());
        }
    }
}