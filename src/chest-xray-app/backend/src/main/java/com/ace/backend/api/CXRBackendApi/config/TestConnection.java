package com.ace.backend.api.CXRBackendApi.config;

import java.io.IOException;
import java.net.Socket;

public class TestConnection {
    public static void main(String[] args) {
        String host = "localhost";
        int port = 5001;

        try (Socket socket = new Socket(host, port)) {
            System.out.println("✅ Java successfully connected to Flask at " + host + ":" + port);
        } catch (IOException e) {
            System.out.println("❌ Java cannot connect to Flask: " + e.getMessage());
        }
    }
}
