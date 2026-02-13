package com.hps.configmaster_backend.models;

import java.util.Objects;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public class MigResourcesModule {

    @NotNull(message = "Bank code cannot be null")
    @Size(max = 20, message = "Bank code cannot exceed 20 characters")
    private String bankCode;

    @NotNull(message = "Resource wording cannot be null")
    @Size(max = 20, message = "Resource wording cannot exceed 20 characters")
    private String resourceWording;

    // Getters and Setters
    public String getBankCode() {
        return bankCode;
    }

    public void setBankCode(String bankCode) {
        this.bankCode = bankCode;
    }

    public String getResourceWording() {
        return resourceWording;
    }

    public void setResourceWording(String resourceWording) {
        this.resourceWording = resourceWording;
    }





    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof MigResourcesModule)) return false;
        MigResourcesModule that = (MigResourcesModule) o;
        return Objects.equals(bankCode, that.bankCode) &&
               Objects.equals(resourceWording, that.resourceWording);
    }

    @Override
    public int hashCode() {
        return Objects.hash(bankCode, resourceWording);
    }


}

