@echo off
echo Établissement des connexions pour accéder à la base de données...

REM Configuration - Modifiez ces valeurs
set CISCO_EXE="C:\Program Files (x86)\Cisco\Cisco AnyConnect Secure Mobility Client\vpncli.exe"
set VPN_SERVER=adresse_ip_du_vpn
set VPN_USERNAME=votre_nom_utilisateur_vpn
set VPN_PASSWORD=votre_mot_de_passe_vpn
set RDP_SERVER=adresse_ip_du_rdp
set RDP_USERNAME=votre_nom_utilisateur_rdp
set RDP_PASSWORD=votre_mot_de_passe_rdp
set ORACLE_SERVER=adresse_ip_serveur_oracle
set ORACLE_PORT=1521

REM Vérifier si le VPN est déjà connecté
%CISCO_EXE% status | findstr "Connected"
if %errorlevel% NEQ 0 (
    echo Connexion au VPN Cisco...
    echo %VPN_PASSWORD% | %CISCO_EXE% -s connect %VPN_SERVER% -u %VPN_USERNAME%
    
    REM Attendre que la connexion soit établie
    timeout /t 5
    
    REM Vérifier si la connexion a réussi
    %CISCO_EXE% status | findstr "Connected"
    if %errorlevel% NEQ 0 (
        echo Échec de la connexion VPN
        exit /b 1
    ) else (
        echo VPN connecté avec succès
    )
) else (
    echo VPN déjà connecté
)

REM Tester si on peut accéder à l'adresse de la base de données
ping -n 1 %ORACLE_SERVER% > nul
if %errorlevel% NEQ 0 (
    echo Impossible d'accéder au serveur Oracle. Vérifiez votre connexion VPN.
    exit /b 1
)

echo Le serveur Oracle est accessible via le VPN à l'adresse %ORACLE_SERVER%