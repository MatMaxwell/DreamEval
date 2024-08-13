#include <Wire.h>
#include <LCD_I2C.h>
#include <DHT.h>

#define PHOTO_PIN A0   // Analog pin for Photosensor
#define SOUND_PIN A1   // Analog pin for Sound sensor
#define DHT_PIN 49    // Digital pin connected to DHT11 (Temperature and Humidity)
#define VCC_PIN 2      // Digital pin used to supply 5V (just in case)
#define MOTION_PIN 53  // Digital pin connected to Motion Sensor
#define TOGGLE_PIN 51  // Digital pin connected to button
#define DHTTYPE DHT22
#define VREF 3.0 

const int sampleWindow = 50; // Sample window for sound sensor
unsigned int sample;
int ldr = 0; // Photosensor variable
int motion; // Motion sensor variable
float db; // Decibel variable
bool toggle = false;
unsigned long elapsedTime = 0; // Elapsed time variable
unsigned long lastDebounceTime = 0; // Last time the toggle button was pressed
const unsigned long debounceDelay = 200; // Debounce delay in milliseconds

LCD_I2C lcd(0x3F, 20, 4); // I2C address of the LCD & Screen size
DHT dht(DHT_PIN, DHTTYPE);

void setup() {
    Serial.begin(9600);
    delay(500); // Delay for sensors to stabilize

    pinMode(VCC_PIN, OUTPUT);   // Set pin 2 to output mode and set it HIGH to provide 5V
    digitalWrite(VCC_PIN, HIGH);
    dht.begin();

    pinMode(PHOTO_PIN, INPUT);  // Input for Photosensor
    pinMode(SOUND_PIN, INPUT);  // Input for Sound
    pinMode(MOTION_PIN, INPUT); // Input for Motion
    pinMode(TOGGLE_PIN, INPUT); // Input for button

    lcd.begin();     // Initialize LCD
    lcd.backlight(); // Turn on LCD backlight

    // Print initial screen layout
    lcd.print("TM:");   // Initial message: Temperature
    lcd.setCursor(0, 1);     // Move cursor to the second line
    lcd.print("RH:");  // Initial message: Humidity
    lcd.setCursor(0, 2);     // Move cursor to the third line
    lcd.print("PR:");  // Initial message: Photo-resistance
    lcd.setCursor(0, 3);     // Move cursor to the fourth line
    lcd.print("VL:"); // Initial message: Volume
    lcd.setCursor(12, 0);    // Move cursor to (13,0)
    lcd.print("Motion:");    // Initial message: Motion
    lcd.setCursor(12, 2);    // Move cursor to (13,2)
    lcd.print("SD:OFF");     // Initial message: SD status
    lcd.setCursor(12, 3);    // Move cursor to (13,3)
    
    delay(1000); // Delay before starting
}

void loop() {
    readSensors();
    displayData();

    unsigned long currentMillis = millis();
    int buttonState = digitalRead(TOGGLE_PIN);

    // Button debounce logic
    if (buttonState == LOW && (currentMillis - lastDebounceTime) > debounceDelay) {
        toggle = !toggle; // Toggle the state
        lastDebounceTime = currentMillis; // Update the debounce time
        if (toggle) {
            elapsedTime = 0; // Reset elapsed time when toggled on
        }
    }

    // Update elapsed time and display
    if (toggle) {
        displayToggleStatus(elapsedTime);
        printData(elapsedTime);
        elapsedTime++; // Increment elapsed time every second
    } else {
        displayToggleStatus(0);
    }

    delay(1000); // 1 second delay
}

void readSensors() {
    ldr = analogRead(PHOTO_PIN); // Read photosensor
    motion = digitalRead(MOTION_PIN); // Read motion sensor
    
    int rawValue = analogRead(SOUND_PIN); // Read raw analog value
    float voltageValue = rawValue / 1024.0 * VREF; // Convert to voltage
    db = voltageValue * 48.00;  // Convert voltage to decibel value

}

void displayData() {
    float tempC = dht.readTemperature(); // Get temperature in Celsius
    float tempF = tempC * 1.8 + 32; // Convert to Fahrenheit

    // Display Temperature
    lcd.setCursor(3, 0); // Set cursor for temperature value
    lcd.print(tempF, 1); // Print temperature in Fahrenheit with 1 decimal place
    lcd.print(" F   "); // Pad with spaces to clear extra characters

    // Display Humidity
    lcd.setCursor(3, 1); // Set cursor for humidity value
    lcd.print(dht.readHumidity()); // Print humidity
    lcd.print(" %   "); // Pad with spaces

    // Display Photoresistor value
    lcd.setCursor(3, 2); // Set cursor for photosensor value
    lcd.print(ldr); // Print photoresistor value
    lcd.print(" Ohm"); // Pad with spaces

    // Display Decibel value
    lcd.setCursor(3, 3); // Set cursor for sound level value
    lcd.print(db); // Print decibels
    lcd.print(" dB  "); // Pad with spaces

    // Display Motion status
    lcd.setCursor(12, 1); // Set cursor for motion status
    lcd.print(motion ? "True " : "False"); // Print motion status
}

void displayToggleStatus(unsigned long elapsedTime) {
    lcd.setCursor(12, 2); // Set cursor for toggle status
    lcd.print(toggle ? "SD:ON " : "SD:OFF"); // Print toggle status

    lcd.setCursor(12, 3); // Set cursor for elapsed time
    lcd.print(elapsedTime); // Print elapsed time
    lcd.print("     "); // Clear previous digits by overwriting with spaces
    lcd.setCursor(19, 3); // Move cursor to the seconds position
}

void printData(unsigned long elapsedTime) {
    float tempC = dht.readTemperature(); // Get temperature in Celsius
    float tempF = tempC * 1.8 + 32; // Convert to Fahrenheit

    Serial.print("Time: ");
    Serial.print(elapsedTime); // Print elapsed time
    Serial.print(" s, ");

    Serial.print("Temp: ");
    Serial.print(tempF, 1); // Print temperature in Fahrenheit with 1 decimal place
    Serial.print(" F, ");

    Serial.print("Hum: ");
    Serial.print(dht.readHumidity()); // Print humidity
    Serial.print(" %, ");

    Serial.print("PR: ");
    Serial.print(ldr); // Print photoresistor value
    Serial.print(" Ohm, ");

    Serial.print("dB: ");
    Serial.print(db); // Print decibels
    Serial.print(" dB, ");

    Serial.print("Motion: ");
    Serial.println(motion ? "True" : "False"); // Print motion status
}