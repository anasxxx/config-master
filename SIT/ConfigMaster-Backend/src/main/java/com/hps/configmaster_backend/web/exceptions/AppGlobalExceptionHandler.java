package com.hps.configmaster_backend.web.exceptions;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.context.request.WebRequest;
import jakarta.persistence.EntityNotFoundException;


@ControllerAdvice
public class AppGlobalExceptionHandler {
    private final Logger LOGGER = LoggerFactory.getLogger(getClass());
    
    private String appMode="PROD";
    
    public static class ErrorResponse {
        private LocalDateTime timestamp;
        private int status;
        private String error;
        private String message;
        private String path;
        private Map<String, Object> details;
        
        public ErrorResponse(HttpStatus status, String message, String path) {
            this.timestamp = LocalDateTime.now();
            this.status = status.value();
            this.error = status.getReasonPhrase();
            this.message = message;
            this.path = path;
            this.details = new HashMap<>();
        }
        
        public LocalDateTime getTimestamp() { return timestamp; }
        public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
        
        public int getStatus() { return status; }
        public void setStatus(int status) { this.status = status; }
        
        public String getError() { return error; }
        public void setError(String error) { this.error = error; }
        
        public String getMessage() { return message; }
        public void setMessage(String message) { this.message = message; }
        
        public String getPath() { return path; }
        public void setPath(String path) { this.path = path; }
        
        public Map<String, Object> getDetails() { return details; }
        public void setDetails(Map<String, Object> details) { this.details = details; }
    }
    
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    @ResponseBody
    public ErrorResponse handleValidationExceptions(MethodArgumentNotValidException ex, WebRequest request) {
        Map<String, String> errors = ex.getBindingResult()
                .getAllErrors()
                .stream()
                .collect(Collectors.toMap(
                        error -> ((FieldError) error).getField(),
                        error -> error.getDefaultMessage(),
                        (existing, replacement) -> existing + "; " + replacement
                ));
        
        LOGGER.error("Validation error: {}", errors);
        
        ErrorResponse response = new ErrorResponse(
                HttpStatus.BAD_REQUEST,
                "Validation failed",
                request.getDescription(false).replace("uri=", "")
        );
        response.getDetails().put("validationErrors", errors);
        
        return response;
    }
    
    @ExceptionHandler(AccessDeniedException.class)
    @ResponseStatus(HttpStatus.FORBIDDEN)
    @ResponseBody
    public ErrorResponse handleAccessDeniedException(AccessDeniedException ex, WebRequest request) {
        LOGGER.error("Access denied: {}", ex.getMessage());
        
        return new ErrorResponse(
                HttpStatus.FORBIDDEN,
                "Access denied: You don't have permission to access this resource",
                request.getDescription(false).replace("uri=", "")
        );
    }
    
    @ExceptionHandler(EntityNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    @ResponseBody
    public ErrorResponse handleEntityNotFoundException(EntityNotFoundException ex, WebRequest request) {
        LOGGER.error("Entity not found: {}", ex.getMessage());
        
        return new ErrorResponse(
                HttpStatus.NOT_FOUND,
                ex.getMessage(),
                request.getDescription(false).replace("uri=", "")
        );
    }
    
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> handleAllExceptions(Exception ex, WebRequest request) {
        LOGGER.error("Unhandled exception: ", ex);
        
        HttpStatus status = HttpStatus.INTERNAL_SERVER_ERROR;
        String message;
        
        if ("PROD".equals(appMode)) {
            message = "The application cannot execute the action because it has encountered an error, " +
                      "please contact the administrator of the application for more details";
        } else {
            LOGGER.warn("Dev mode is active");
            message = "The application is configured to work in DEV mode. " +
                      "An error has occurred: " + ex.getMessage();
        }
        
        ErrorResponse errorResponse = new ErrorResponse(
                status,
                message,
                request.getDescription(false).replace("uri=", "")
        );
        
        if (!"PROD".equals(appMode)) {
            errorResponse.getDetails().put("exception", ex.getClass().getName());
            errorResponse.getDetails().put("stackTrace", getStackTraceAsString(ex));
        }
        
        return new ResponseEntity<>(errorResponse, status);
    }
    
    private String getStackTraceAsString(Exception ex) {
        return java.util.Arrays.stream(ex.getStackTrace())
                .limit(10)
                .map(StackTraceElement::toString)
                .collect(Collectors.joining("\n"));
    }
}
