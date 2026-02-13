package com.hps.configmaster_backend.config;


import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import  com.hps.configmaster_backend.filter.*;
@Configuration
public class SpringSecurityConfig {
	
	@Bean
	public SecurityFilterChain filterChain(HttpSecurity http, JwtAuthorizationFilter jwtAuthenticationFilter) throws Exception {
	    return http
	            .cors(Customizer.withDefaults())
	            .csrf(csrf -> csrf.disable())
	            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
	            .authorizeHttpRequests(auth -> auth
	                    .requestMatchers("/v1/api/login","/v2/api-docs/**",
	                            "/v3/api-docs/**",
	                            "/swagger-resources/**",
	                            "/swagger-ui/**",
	                            "/swagger-ui.html",
	                            "/h2-console"

	                            ).permitAll()  // Permet l'accès sans authentification
	                    .anyRequest().authenticated())          // Toutes les autres requêtes doivent être authentifiées
	            .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class)
	            .build();
	}

    
    @Bean
    public UserDetailsService users() {
        UserDetails full = User.builder().username("full@gmail.com").password(passwordEncoder().encode("full")).roles("full")
                .build();
        
        UserDetails demo = User.builder().username("demo@gmail.com").password(passwordEncoder().encode("demo")).roles("demo")
                .build();
        
        return new InMemoryUserDetailsManager(demo,full);
    }
    
    @Bean
    public AuthenticationManager authenticationManager(HttpSecurity http, BCryptPasswordEncoder passwordEncoder) throws Exception {
        UserDetailsService userDetailsService = users();  // Crée un service utilisateur en mémoire
        DaoAuthenticationProvider authProvider = new DaoAuthenticationProvider();
        authProvider.setUserDetailsService(userDetailsService);
        authProvider.setPasswordEncoder(passwordEncoder);

        return http.getSharedObject(AuthenticationManagerBuilder.class)
                   .authenticationProvider(authProvider)
                   .build();
    }

    
   
    
    @Bean
    public BCryptPasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    
    
    

}