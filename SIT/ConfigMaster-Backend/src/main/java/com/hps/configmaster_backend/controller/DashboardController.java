package com.hps.configmaster_backend.controller;
import java.math.BigDecimal;
import java.sql.Date;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.hps.configmaster_backend.models.TransactionModel;
import com.hps.configmaster_backend.service.IDashboardervice;
@RestController
@RequestMapping("/v1/api/dashboard")
public class DashboardController {
    @Autowired
    private IDashboardervice dashboardService;
    @GetMapping("/transactions/{codeBank}/{date}")
    public ResponseEntity<List<TransactionModel>> getStats(
            @PathVariable("codeBank") String codeBank,
            @PathVariable("date") @DateTimeFormat(pattern = "dd-MM-yyyy") LocalDate date) {
        
        // On formate la date au format DD/MM/YYYY comme requis par la requête SQL
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd/MM/yyyy");
        String formattedDate = date.format(formatter);
        System.out.println("Date formatée: " + formattedDate);
        
        // On passe la chaîne formatée à la méthode du service qui l'attend dans ce format
        List<Object[]> results = dashboardService.getTransactionStats(formattedDate, codeBank);
        
        List<TransactionModel> models = new ArrayList<>();
        for (Object[] row : results) {
            TransactionModel model = new TransactionModel();
            if (row[0] instanceof Date) {
                LocalDate transactionDate = ((Date) row[0]).toLocalDate();
                model.setTransactionDate(transactionDate.format(formatter));
            } else {
                model.setTransactionDate(row[0].toString()); // fallback
            }
            model.setIssuingBank((String) row[1]);
            model.setTotalTransaction(((BigDecimal) row[2]).longValue());
            model.setPerApproved((String) row[3]);
            model.setPerCancellationApproved((String) row[4]);
            model.setPerCancellationRejected((String) row[5]);
            model.setPerDeclinedFonc((String) row[6]);
            model.setPerDeclinedTech((String) row[7]);
            models.add(model);
        }
        return ResponseEntity.ok(models);
    }
}