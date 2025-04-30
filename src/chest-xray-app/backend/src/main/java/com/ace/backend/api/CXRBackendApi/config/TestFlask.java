package com.ace.backend.api.CXRBackendApi.config;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;

public class TestFlask {
    public static void main(String[] args) {
        String flaskUrl = "http://127.0.0.1:5001/predict"; // Change if needed

        try {
            System.out.println("🔍 Testing Flask connection at " + flaskUrl);

            URL url = new URL(flaskUrl);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setDoOutput(true);

            // Send an empty JSON body
            OutputStream os = conn.getOutputStream();
            os.write("{}".getBytes());
            os.flush();
            os.close();

            int responseCode = conn.getResponseCode();
            System.out.println("✅ Response Code: " + responseCode);

            if (responseCode == 200) {
                BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                String inputLine;
                StringBuilder response = new StringBuilder();
                while ((inputLine = in.readLine()) != null) {
                    response.append(inputLine);
                }
                in.close();

                System.out.println("✅ Flask Response: " + response.toString());
            } else {
                System.out.println("❌ Flask is not reachable. HTTP Code: " + responseCode);
            }

        } catch (Exception e) {
            System.err.println("❌ Java cannot reach Flask API.");
            e.printStackTrace();
        }
    }
}
