#include <WiFi.h>
#include <WebServer.h>

// Motor control pins
#define IN1 25   // Motor A direction control
#define IN2 26   // Motor A direction control
#define IN3 27   // Motor B direction control
#define IN4 14   // Motor B direction control

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

  // Set all motor control pins as outputs
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Define server routes
  server.on("/send", HTTP_POST, handleMotorControl);

  server.begin();
}

void loop() {
  server.handleClient();
}

void handleMotorControl() {
  String message = server.arg("plain");
  Serial.println("Message received: " + message);

  if (message == "F") {
    moveForward();
    server.send(200, "text/plain", "Moving Forward");
  } else if (message == "B") {
    moveBackward();
    server.send(200, "text/plain", "Moving Backward");
  } else if (message == "L") {
    turnLeft();
    server.send(200, "text/plain", "Turning Left");
  } else if (message == "R") {
    turnRight();
    server.send(200, "text/plain", "Turning Right");
  } else if (message == "S") {
    stopMotors();
    server.send(200, "text/plain", "Stopping Motors");
  } else {
    server.send(400, "text/plain", "Invalid Command");
  }
}

void moveForward() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void moveBackward() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void turnLeft() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void turnRight() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}
