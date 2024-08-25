#include <WiFi.h>
#include <WebServer.h>

const char* ssid = "IIT_Bhilai";
const char* password = "iitbhilai2023";

WebServer server(80); // Create a web server on port 80

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  server.on("/send", HTTP_POST, []() {
    String message = server.arg("plain");
    Serial.println("Message received: " + message);
    server.send(200, "text/plain", "Message received");
  });

  server.begin();
}

void loop() {
  server.handleClient();
}