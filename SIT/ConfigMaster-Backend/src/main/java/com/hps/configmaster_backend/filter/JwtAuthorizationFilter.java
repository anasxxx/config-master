package com.hps.configmaster_backend.filter;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.hps.configmaster_backend.service.Imp.JWTService;

import io.jsonwebtoken.Claims;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

@Component
public class JwtAuthorizationFilter extends OncePerRequestFilter {

    private final JWTService jwtUtil;
    private final ObjectMapper mapper;

    public JwtAuthorizationFilter(JWTService jwtUtil, ObjectMapper mapper) {
        this.jwtUtil = jwtUtil;
        this.mapper = mapper;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        
        System.out.println("🔹 [JwtAuthorizationFilter] Filtre JWT activé pour la requête : " + request.getRequestURI());

        try {
            // Récupérer le token
            String accessToken = jwtUtil.resolveToken(request);
            if (accessToken == null) {
                System.out.println("🔹 Aucun token trouvé, passage au filtre suivant.");
                filterChain.doFilter(request, response);
                return;
            }

            System.out.println("🔹 Token reçu : " + accessToken);

            // Décoder le token
            Claims claims = jwtUtil.resolveClaims(request);

            if (claims != null && jwtUtil.validateClaims(claims)) {
                String email = claims.getSubject();
                System.out.println("✅ Utilisateur authentifié : " + email);

                Authentication authentication =
                        new UsernamePasswordAuthenticationToken(email, "", new ArrayList<>());

                SecurityContextHolder.getContext().setAuthentication(authentication);
            } else {
                System.out.println("❌ Token invalide !");
            }

        } catch (Exception e) {
            System.out.println("❌ Erreur d'authentification : " + e.getMessage());

            Map<String, Object> errorDetails = new HashMap<>();
            errorDetails.put("message", "Authentication Error");
            errorDetails.put("details", e.getMessage());

            response.setStatus(HttpStatus.FORBIDDEN.value());
            response.setContentType(MediaType.APPLICATION_JSON_VALUE);
            mapper.writeValue(response.getWriter(), errorDetails);
            
            return; // Empêche la requête de continuer après une erreur
        }

        filterChain.doFilter(request, response);
    }
}
