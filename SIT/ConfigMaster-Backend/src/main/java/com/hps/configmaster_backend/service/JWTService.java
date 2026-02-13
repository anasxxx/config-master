// Déclaration du package
package com.hps.configmaster_backend.service;

import java.util.Date;
import java.util.List;
import java.util.concurrent.TimeUnit;

import javax.crypto.SecretKey;

import org.springframework.security.core.AuthenticationException;


import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.models.*;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.JwtParser;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import jakarta.servlet.http.HttpServletRequest;


import java.util.List;
import jakarta.servlet.http.HttpServletRequest;
import io.jsonwebtoken.Claims;
import com.hps.configmaster_backend.models.User;

public interface JWTService {

    String createToken(User user);

    Claims resolveClaims(HttpServletRequest req);

    String resolveToken(HttpServletRequest request);

    boolean validateClaims(Claims claims);

    String getEmail(Claims claims);

    List<String> getRoles(Claims claims);
}

