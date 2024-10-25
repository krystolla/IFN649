#include <Wire.h>
#include <MAX30105.h>  // Correct SparkFun library for MAX3010x sensors
#include "heartRate.h"  // Library for heart rate calculations

MAX30105 particleSensor;  // Create an instance of the sensor

// Variables for heart rate calculations
uint32_t irValue;
int beatsPerMinute;
double beatAvg = 0;
long lastBeat = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);  // Give time for the Serial to initialize

  // Initialize the sensor
  if (!particleSensor.begin(Wire)) {
    Serial.println("MAX30102 was not found. Please check wiring/power.");
    while (1);  // Stop execution if sensor is not found
  }

  Serial.println("Place your index finger on the sensor with steady pressure.");

  // Setup sensor with default settings
  particleSensor.setup();  // Use default settings (includes sample rate and pulse width)
  particleSensor.setPulseAmplitudeRed(0x0A);  // Turn Red LED to low
  particleSensor.setPulseAmplitudeGreen(0);   // Turn off Green LED
}

void loop() {
  // Read the IR value (Infrared light)
  irValue = particleSensor.getIR();

  // If a heartbeat is detected
  if (checkForBeat(irValue)) {
    // Calculate time since last beat
    long delta = millis() - lastBeat;
    lastBeat = millis();

    // Calculate beats per minute (BPM)
    beatsPerMinute = 60 / (delta / 1000.0);

    // Filter out unrealistic values
    if (beatsPerMinute > 20 && beatsPerMinute < 255) {
      beatAvg = (beatAvg * 0.95) + (beatsPerMinute * 0.05);  // Running average of BPM
    }


  }

  // Print heart rate to the Serial Monitor, Print IR values for reference
  Serial.print("BPM=");
  Serial.println(beatAvg);
  Serial.print("IR=");
  Serial.println(irValue);

  delay(100);  // Wait 100 ms before the next reading
}
