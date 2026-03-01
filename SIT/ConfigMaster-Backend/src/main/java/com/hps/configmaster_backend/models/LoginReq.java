package com.hps.configmaster_backend.models;


public class LoginReq {
    private String email;
    private String password;
    private String enve;

    public LoginReq() {
    }

    public LoginReq(String email, String password) {
        this.email = email;
        this.password = password;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

	public String getEnve() {
		return enve;
	}

	public void setEnve(String enve) {
		this.enve = enve;
	}
    
}
