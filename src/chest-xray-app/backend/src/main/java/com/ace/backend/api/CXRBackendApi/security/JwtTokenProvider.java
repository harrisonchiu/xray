package com.ace.backend.api.CXRBackendApi.security;

import com.ace.backend.api.CXRBackendApi.exception.APIException;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.UnsupportedJwtException;
import io.jsonwebtoken.io.Decoder;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.security.Key;
import java.util.Date;

@Component
public class JwtTokenProvider {

    @Value("${app.jwt-secret}")
    private String jwtSecret;
    @Value(("${app-jwt-expiration-milliseconds}"))
    private Long jwtExpirationDate;

    // generate JWT token
    public String generateToken(Authentication authentication){
        String username = authentication.getName();
        Date currentDate = new Date();
        Date expireDate = new Date(currentDate.getTime() + jwtExpirationDate);

        String token = Jwts.builder()
                .setSubject(username)
                .setIssuedAt(new Date())
                .setExpiration(expireDate)
                .signWith(key())
                .compact();

        return token;
    }

    private Key key(){
        return Keys.hmacShaKeyFor(Decoders.BASE64.decode(jwtSecret));
    }

    // get username from JWT TOKEN
    public String getUsername(String token){
        return Jwts.parserBuilder()
                .setSigningKey((SecretKey) key())
                .build()
                .parseClaimsJws(token)
                .getBody()
                .getSubject();
    }

    // validate JWT token
    public boolean validateToken(String token){
        try {
            Jwts.parserBuilder()
                    .setSigningKey(key())
                    .build()
                    .parse(token);
            return true;
        } catch (MalformedJwtException malformedJwtException){
            throw new APIException("Invalid JWT token", HttpStatus.BAD_REQUEST);
        } catch (ExpiredJwtException exception){
            throw new APIException("Expired JWT token", HttpStatus.BAD_REQUEST);
        } catch (UnsupportedJwtException unsupportedJwtException){
            throw new APIException("Unsupported JWT token", HttpStatus.BAD_REQUEST);
        } catch (IllegalArgumentException illegalArgumentException){
            throw new APIException("JWT claims string is empty or null", HttpStatus.BAD_REQUEST);
        }
    }
}
