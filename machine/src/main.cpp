/*
 * TVS2102 - Thread Verification System
 * 
 * Model Designation:
 * TVS  - Thread Verification System (product line)
 * 2    - Dual QR scanners (number of scanning units for thread verification)
 * 1    - Single output (number of outputs)
 * 02   - Version 02 (product version/revision)
 * 
 * ESP32 Firmware for Thread Verification using RFID Kanban and Dual QR Scanners
 * 
 * Features:
 * - MFRC522 RFID reader for Kanban cards
 * - Dual GM65 QR scanners for thread verification
 * - Proximity sensors for bobbin detection
 * - LED indicators (Ready/Alarm)
 * - Machine relay control
 * - Bypass mode support
 * 
 * Author: weerachai
 * Version: 1.0.0
 * License: MIT
 */

#include <Arduino.h>
#include <SPI.h>
#include <MFRC522.h>
#include <HardwareSerial.h>

// =============== PIN DEFINITIONS ===============
// MFRC522 RFID Reader (SPI)
#define RFID_SS_PIN     5
#define RFID_RST_PIN    22
#define RFID_SCK_PIN    18
#define RFID_MOSI_PIN   23
#define RFID_MISO_PIN   19

// GM65 QR Scanner 1 (Hardware Serial1 with custom pins)
#define QR1_RX_PIN      4
#define QR1_TX_PIN      2
// #define QR1_TRIG_PIN    12  // Not used - trigger via serial command

// GM65 QR Scanner 2 (Hardware Serial2 - U2_RXD/U2_TXD)
#define QR2_RX_PIN      16
#define QR2_TX_PIN      17
// #define QR2_TRIG_PIN    13  // Not used - trigger via serial command

// Proximity Sensors
#define BOBBIN1_PIN     32
#define BOBBIN2_PIN     33

// LED Indicators
#define LED_READY1_PIN  25
#define LED_READY2_PIN  26
#define LED_ALARM1_PIN  27
#define LED_ALARM2_PIN  14

// Machine Outputs
#define MACHINE_OUT1_PIN 21
// #define MACHINE_OUT2_PIN 15  // Reserved for V2 (connect through ULN2003A)

// =============== CONSTANTS ===============
#define BLOCK_THREAD1   4
#define BLOCK_THREAD2   5
#define QR_TIMEOUT      5000
#define BYPASS_KEYWORD  "bypass"

// Timing constants (milliseconds)
#define DEBOUNCE_DELAY        500
#define RESET_ALARM_DELAY     250
#define RFID_WAKEUP_DELAY     10
#define RFID_RESET_DELAY      50
#define QR_TRIGGER_DELAY      500
#define QR_READ_DELAY         50
#define QR_POLL_DELAY         10
#define SERIAL_STABILIZE_DELAY 100
#define LOOP_DELAY            100
#define BOBBIN_WAIT_TIMEOUT   30000

// Card presence detection constants
#define CARD_CHECK_INTERVAL      300  // Check every 300ms (~3 times/sec)
#define CARD_MISSING_THRESHOLD   1    // Confirm removal after 3 consecutive failures

// =============== GLOBAL OBJECTS ===============
MFRC522 rfid(RFID_SS_PIN, RFID_RST_PIN);
MFRC522::MIFARE_Key key;
HardwareSerial qrScanner1(1);  // Use UART1 with custom pins
HardwareSerial qrScanner2(2);  // Use UART2 (GPIO16/17)

// =============== STATE MACHINE ===============
enum SystemState {
    STATE_INIT,
    STATE_WAIT_KANBAN,
    STATE_READ_KANBAN,
    STATE_WAIT_BOBBINS,
    STATE_SCAN_QR1,
    STATE_SCAN_QR2,
    STATE_VERIFY,
    STATE_READY,
    STATE_ERROR,
    STATE_BYPASS
};

SystemState currentState = STATE_INIT;

// =============== DATA STRUCTURES ===============
struct ThreadData {
    String thread1;
    String thread2;
    bool isBypass;
};

ThreadData kanbanData;
String qrCode1 = "";
String qrCode2 = "";
byte kanbanUID[10]; // Store Kanban card UID (max 10 bytes)
byte kanbanUIDSize = 0;
bool thread1Error = false; // Track Thread 1 mismatch
bool thread2Error = false; // Track Thread 2 mismatch
bool resetMonitoringArmed = false;
bool bobbinsLatched = false;
int cardMissingCount = 0; // Counter for card presence debouncing

// =============== FUNCTION PROTOTYPES ===============
void setupPins();
void setupRFID();
void setupQRScanners();
void updateLEDs(bool ready1, bool ready2, bool alarm1, bool alarm2);
void setMachineOutput(bool enable);
void triggerQRScanner(int scannerNum);
String readQRCode(HardwareSerial& scanner, int timeoutMs);
bool readKanbanCard(ThreadData& data);
bool isKanbanCardStillPresent();
bool detectBobbin(int bobbinPin);
bool verifyThreads();
void handleStateMachine();
void printState(SystemState state);
String byteArrayToString(byte* buffer, byte bufferSize);
void clearProcessData();
bool handleResetIfBobbinRemoved(const char* stateLabel);
const char* stateToString(SystemState state);
void testOutputs();

// =============== SETUP ===============
void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n\n========================================");
    Serial.println("  Thread Verification System");
    Serial.println("  ESP32 Machine Controller v1.0.0");
    Serial.println("========================================\n");
    
    setupPins();
    setupRFID();
    setupQRScanners();
    
    // Initialize default key (all 0xFF)
    for (byte i = 0; i < 6; i++) {
        key.keyByte[i] = 0xFF;
    }
    
    currentState = STATE_WAIT_KANBAN;
    Serial.println("System initialized. Waiting for Kanban card...\n");
}

// =============== MAIN LOOP ===============
void loop() {
    // Uncomment for circuit testing mode
    // testOutputs();
    
    // Normal operation
    handleStateMachine();
    delay(LOOP_DELAY);
}

// =============== TEST FUNCTIONS ===============
void testOutputs() {
    // Continuous blinking for circuit verification
    digitalWrite(LED_READY1_PIN, HIGH);
    digitalWrite(LED_READY2_PIN, HIGH);
    digitalWrite(LED_ALARM1_PIN, HIGH);
    digitalWrite(LED_ALARM2_PIN, HIGH);
    digitalWrite(MACHINE_OUT1_PIN, HIGH);
    delay(RESET_ALARM_DELAY);
    
    digitalWrite(LED_READY1_PIN, LOW);
    digitalWrite(LED_READY2_PIN, LOW);
    digitalWrite(LED_ALARM1_PIN, LOW);
    digitalWrite(LED_ALARM2_PIN, LOW);
    digitalWrite(MACHINE_OUT1_PIN, LOW);
    delay(RESET_ALARM_DELAY);
}

// =============== PIN SETUP ===============
void setupPins() {
    // QR Scanner triggers (Not used - trigger via serial command)
    // pinMode(QR1_TRIG_PIN, OUTPUT);
    // pinMode(QR2_TRIG_PIN, OUTPUT);
    // digitalWrite(QR1_TRIG_PIN, LOW);
    // digitalWrite(QR2_TRIG_PIN, LOW);
    
    // Proximity sensors
    pinMode(BOBBIN1_PIN, INPUT);
    pinMode(BOBBIN2_PIN, INPUT);
    
    // LED outputs
    pinMode(LED_READY1_PIN, OUTPUT);
    pinMode(LED_READY2_PIN, OUTPUT);
    pinMode(LED_ALARM1_PIN, OUTPUT);
    pinMode(LED_ALARM2_PIN, OUTPUT);
    
    // Machine outputs
    pinMode(MACHINE_OUT1_PIN, OUTPUT);
    // pinMode(MACHINE_OUT2_PIN, OUTPUT);  // Reserved for V2
    
    // Initialize all outputs to safe state
    updateLEDs(false, false, false, false);
    setMachineOutput(false);
    
    Serial.println("[SETUP] Pins configured");
}

// =============== RFID SETUP ===============
void setupRFID() {
    // Explicit SPI pins for ESP32
    SPI.begin(RFID_SCK_PIN, RFID_MISO_PIN, RFID_MOSI_PIN, RFID_SS_PIN);
    
    // Set SS and RST as outputs
    pinMode(RFID_SS_PIN, OUTPUT);
    pinMode(RFID_RST_PIN, OUTPUT);
    
    // Hardware reset
    digitalWrite(RFID_RST_PIN, LOW);
    delay(RFID_RESET_DELAY);
    digitalWrite(RFID_RST_PIN, HIGH);
    delay(RFID_RESET_DELAY);
    
    rfid.PCD_Init(RFID_SS_PIN, RFID_RST_PIN);
    delay(SERIAL_STABILIZE_DELAY);
    
    // Debug SPI communication
    // Verify RFID reader is connected
    byte version = rfid.PCD_ReadRegister(rfid.VersionReg);
    Serial.print("[SETUP] MFRC522 Register: 0x");
    Serial.println(version, HEX);
    
    if (version == 0x00 || version == 0xFF) {
        Serial.println("[WARNING] MFRC522 not detected! Check wiring.");
        // Continue anyway for testing without hardware
    } else {
        Serial.println("[SETUP] MFRC522 initialized successfully");
    }
}

// =============== QR SCANNER SETUP ===============
void setupQRScanners() {
    // Initialize QR Scanner 1 on Serial1 with custom pins
    qrScanner1.begin(9600, SERIAL_8N1, QR1_RX_PIN, QR1_TX_PIN);
    
    // Initialize QR Scanner 2 on Serial2 with hardware UART pins
    qrScanner2.begin(9600, SERIAL_8N1, QR2_RX_PIN, QR2_TX_PIN);
    
    delay(100); // Allow serial ports to stabilize    
    Serial.println("[SETUP] QR Scanners initialized");
}

// =============== LED CONTROL ===============
void updateLEDs(bool ready1, bool ready2, bool alarm1, bool alarm2) {
    digitalWrite(LED_READY1_PIN, ready1 ? HIGH : LOW);
    digitalWrite(LED_READY2_PIN, ready2 ? HIGH : LOW);
    digitalWrite(LED_ALARM1_PIN, alarm1 ? HIGH : LOW);
    digitalWrite(LED_ALARM2_PIN, alarm2 ? HIGH : LOW);
}

// =============== MACHINE OUTPUT CONTROL ===============
void setMachineOutput(bool enable) {
    static bool lastState = false;
    static bool initialized = false;
    
    // Only update and print if state changed
    if (!initialized || lastState != enable) {
        digitalWrite(MACHINE_OUT1_PIN, enable ? HIGH : LOW);
        // digitalWrite(MACHINE_OUT2_PIN, enable ? HIGH : LOW);  // Reserved for V2
        Serial.print("[OUTPUT] Machine: ");
        Serial.println(enable ? "ENABLED" : "DISABLED");
        lastState = enable;
        initialized = true;
    }
    // Future V2: Add Machine 2 control
}

// Clears runtime data so the workflow can restart from WAIT_KANBAN safely.
void clearProcessData() {
    kanbanData.thread1 = "";
    kanbanData.thread2 = "";
    kanbanData.isBypass = false;
    qrCode1 = "";
    qrCode2 = "";
    for (byte i = 0; i < sizeof(kanbanUID); i++) {
        kanbanUID[i] = 0x00;
    }
    kanbanUIDSize = 0;
    thread1Error = false;
    thread2Error = false;
    resetMonitoringArmed = false;
    bobbinsLatched = false;
    cardMissingCount = 0;
}

// =============== KANBAN CARD PRESENCE CHECK ===============
bool isKanbanCardStillPresent() {
    byte bufferATQA[2];
    byte bufferSize = sizeof(bufferATQA);
    
    // Send Wake-up (WUPA) command to check if card responds
    // This is gentler than PCD_Init() and doesn't reset SPI bus
    MFRC522::StatusCode status = rfid.PICC_WakeupA(bufferATQA, &bufferSize);
    
    // Clear state for next check cycle
    rfid.PICC_HaltA();
    
    return (status == MFRC522::STATUS_OK);
}

// Handles global reset when bobbins are removed mid-process.
bool handleResetIfBobbinRemoved(const char* stateLabel) {
    if (!resetMonitoringArmed) {
        return false;
    }

    bool bobbin1Present = detectBobbin(BOBBIN1_PIN);
    bool bobbin2Present = detectBobbin(BOBBIN2_PIN);

    if (bobbin1Present && bobbin2Present && !bobbinsLatched) {
        bobbinsLatched = true;
    }

    if (!bobbinsLatched || (bobbin1Present && bobbin2Present)) {
        return false;
    }

    Serial.print("[RESET] Bobbin removed during ");
    Serial.print(stateLabel);
    Serial.println(" state. Restarting system...");

    updateLEDs(false, false, true, true);
    setMachineOutput(false);
    delay(RESET_ALARM_DELAY);
    clearProcessData();
    currentState = STATE_WAIT_KANBAN;
    return true;
}

// =============== QR SCANNER TRIGGER ===============
void triggerQRScanner(int scannerNum) {
    // GM65 Serial command trigger: 7E 00 08 01 00 02 01 AB CD
    byte triggerCmd[] = {0x7E, 0x00, 0x08, 0x01, 0x00, 0x02, 0x01, 0xAB, 0xCD};
    
    HardwareSerial& scanner = (scannerNum == 1) ? qrScanner1 : qrScanner2;
    
    // Clear buffer before trigger
    while (scanner.available()) scanner.read();
    
    // Send serial trigger command
    scanner.write(triggerCmd, sizeof(triggerCmd));
    
    Serial.print("[QR] Triggered scanner ");
    Serial.print(scannerNum);
    Serial.println(" (Serial command)");
}

// =============== READ QR CODE ===============
String readQRCode(HardwareSerial& scanner, int timeoutMs) {
    String qrData = "";
    unsigned long startTime = millis();
    bool headerSkipped = false;
    int headerBytes = 0;
    
    // Wait for data with timeout
    // GM65 response format: [02][00][00][01][00][LEN_HIGH][LEN_LOW] + QR_DATA + [0D]
    // Skip first 7 bytes (header + length bytes)
    while (millis() - startTime < timeoutMs) {
        while (scanner.available()) {
            byte b = scanner.read();
            
            // Skip header bytes (first 7 bytes)
            if (!headerSkipped) {
                headerBytes++;
                if (headerBytes >= 7) {
                    headerSkipped = true;
                }
                continue;
            }
            
            // End of data (CR or LF)
            if (b == 0x0D || b == 0x0A) {
                if (qrData.length() > 0) {
                    break;
                }
                continue;
            }
            
            // Printable ASCII only
            if (b >= 32 && b <= 126) {
                qrData += (char)b;
            }
        }
        
        // Exit if we got data and saw end marker
        if (qrData.length() > 0 && headerSkipped) {
            // Check if no more data coming
            delay(QR_READ_DELAY);
            if (!scanner.available()) break;
        }
        delay(QR_POLL_DELAY);
    }
    
    qrData.trim();
    return qrData;
}

// =============== READ KANBAN CARD ===============
bool readKanbanCard(ThreadData& data) {
    // Reset data
    data.thread1 = "";
    data.thread2 = "";
    data.isBypass = false;
    
    // Try to read card serial (card already detected in WAIT_KANBAN state)
    if (!rfid.PICC_ReadCardSerial()) {
        // If failed, try detecting again
        if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
            Serial.println("[DEBUG] Cannot read card serial");
            return false;
        }
    }   
    
    // Read Thread 1 from Block 4
    byte buffer1[18];
    byte size1 = sizeof(buffer1);
    MFRC522::StatusCode status;
    
    // Authenticate Block 4
    status = rfid.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, BLOCK_THREAD1, &key, &(rfid.uid));
    if (status != MFRC522::STATUS_OK) {
        Serial.print("[RFID] Authentication failed for Block 4: ");
        Serial.println(rfid.GetStatusCodeName(status));
        rfid.PCD_StopCrypto1();
        rfid.PICC_HaltA();
        return false;
    }
    
    // Read Block 4
    status = rfid.MIFARE_Read(BLOCK_THREAD1, buffer1, &size1);
    if (status != MFRC522::STATUS_OK) {
        Serial.print("[RFID] Read failed for Block 4: ");
        Serial.println(rfid.GetStatusCodeName(status));
        rfid.PCD_StopCrypto1();
        rfid.PICC_HaltA();
        return false;
    }
    
    data.thread1 = byteArrayToString(buffer1, 16);
    Serial.print("[RFID] Thread 1: ");
    Serial.println(data.thread1);
    
    // Check for bypass mode
    if (data.thread1.equalsIgnoreCase(BYPASS_KEYWORD)) {
        data.isBypass = true;
        Serial.println("[RFID] BYPASS MODE DETECTED");
        rfid.PCD_StopCrypto1();
        rfid.PICC_HaltA();
        return true;
    }
    
    // Read Thread 2 from Block 5
    byte buffer2[18];
    byte size2 = sizeof(buffer2);
    
    // Authenticate Block 5
    status = rfid.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, BLOCK_THREAD2, &key, &(rfid.uid));
    if (status != MFRC522::STATUS_OK) {
        Serial.print("[RFID] Authentication failed for Block 5: ");
        Serial.println(rfid.GetStatusCodeName(status));
        rfid.PCD_StopCrypto1();
        rfid.PICC_HaltA();
        return false;
    }
    
    // Read Block 5
    status = rfid.MIFARE_Read(BLOCK_THREAD2, buffer2, &size2);
    if (status != MFRC522::STATUS_OK) {
        Serial.print("[RFID] Read failed for Block 5: ");
        Serial.println(rfid.GetStatusCodeName(status));
        rfid.PCD_StopCrypto1();
        rfid.PICC_HaltA();
        return false;
    }
    
    data.thread2 = byteArrayToString(buffer2, 16);
    Serial.print("[RFID] Thread 2: ");
    Serial.println(data.thread2);
    
    rfid.PCD_StopCrypto1();
    rfid.PICC_HaltA();
    return true;
}

// =============== BOBBIN DETECTION ===============
bool detectBobbin(int bobbinPin) {
    // PNP sensor or active HIGH logic
    return digitalRead(bobbinPin) == HIGH;
}

// =============== THREAD VERIFICATION ===============
bool verifyThreads() {
    bool match1 = (qrCode1 == kanbanData.thread1);
    bool match2 = (qrCode2 == kanbanData.thread2);
    
    // Store individual thread error status
    thread1Error = !match1;
    thread2Error = !match2;
    
    Serial.println("\n[VERIFY] Thread Verification:");
    Serial.print("  Thread 1: ");
    Serial.print(match1 ? "✓ MATCH" : "✗ MISMATCH");
    Serial.print(" (Kanban: ");
    Serial.print(kanbanData.thread1);
    Serial.print(", QR: ");
    Serial.print(qrCode1);
    Serial.println(")");
    
    Serial.print("  Thread 2: ");
    Serial.print(match2 ? "✓ MATCH" : "✗ MISMATCH");
    Serial.print(" (Kanban: ");
    Serial.print(kanbanData.thread2);
    Serial.print(", QR: ");
    Serial.print(qrCode2);
    Serial.println(")");
    
    return match1 && match2;
}

// =============== STATE MACHINE ===============
void handleStateMachine() {
    static unsigned long stateEntryTime = 0;
    static SystemState previousState = STATE_INIT;
    
    // Detect state change
    if (currentState != previousState) {
        stateEntryTime = millis();
        printState(currentState);
        previousState = currentState;
    }

    if (handleResetIfBobbinRemoved(stateToString(currentState))) {
        return;
    }
    
    switch (currentState) {
        // ===== WAIT FOR KANBAN =====
        case STATE_WAIT_KANBAN: {
            static bool readerReset = false;
            
            // Reset RFID reader once when entering this state to clear HALT status
            if (!readerReset) {
                rfid.PCD_Init();
                delay(RFID_RESET_DELAY);
                readerReset = true;
            }
            
            // Blink READY LEDs every 1 second when waiting (no bobbin state)
            bool blinkState = (millis() / 1000) % 2 == 0;
            updateLEDs(blinkState, blinkState, false, false);
            setMachineOutput(false);
            
            if (rfid.PICC_IsNewCardPresent()) {
                readerReset = false; // Reset flag for next time
                currentState = STATE_READ_KANBAN;
            }
            break;
        }
        
        // ===== READ KANBAN CARD =====
        case STATE_READ_KANBAN:
            if (readKanbanCard(kanbanData)) {
                // Store Kanban card UID for later comparison
                kanbanUIDSize = rfid.uid.size;
                for (byte i = 0; i < kanbanUIDSize; i++) {
                    kanbanUID[i] = rfid.uid.uidByte[i];
                }
                
                Serial.println("\n========== KANBAN DATA ==========");
                Serial.print("[RFID] Card detected!\n[RFID] UID: ");
                for (byte i = 0; i < rfid.uid.size; i++) {
                    Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
                    Serial.print(rfid.uid.uidByte[i], HEX);
                }
                Serial.println();
                Serial.print("Thread 1: \"");
                Serial.print(kanbanData.thread1);
                Serial.println("\"");
                Serial.print("Thread 2: \"");
                Serial.print(kanbanData.thread2);
                Serial.println("\"");
                Serial.print("Bypass: ");
                Serial.println(kanbanData.isBypass ? "YES" : "NO");
                
                if (kanbanData.isBypass) {
                    resetMonitoringArmed = true;
                    bobbinsLatched = false;
                    currentState = STATE_BYPASS;
                } else if (kanbanData.thread1.length() > 0 && kanbanData.thread2.length() > 0) {
                    resetMonitoringArmed = true;
                    bobbinsLatched = false;
                    currentState = STATE_WAIT_BOBBINS;
                } else {
                    Serial.println("[ERROR] Invalid Kanban data");
                    currentState = STATE_ERROR;
                }
            } else {
                // Failed to read, try again
                delay(DEBOUNCE_DELAY);
                currentState = STATE_WAIT_KANBAN;
            }
            break;
        
        // ===== WAIT FOR BOBBINS =====
        case STATE_WAIT_BOBBINS: {
            bool bobbin1Present = detectBobbin(BOBBIN1_PIN);
            bool bobbin2Present = detectBobbin(BOBBIN2_PIN);
            
            // Blink READY LEDs every 1 second when waiting for bobbins
            bool blinkState = (millis() / 1000) % 2 == 0;
            updateLEDs(blinkState, blinkState, false, false);
            
            if (bobbin1Present && bobbin2Present) {
                Serial.println("[INFO] Both bobbins detected");
                delay(DEBOUNCE_DELAY);
                currentState = STATE_SCAN_QR1;
            }
            
            // Timeout after 30 seconds
            if (millis() - stateEntryTime > BOBBIN_WAIT_TIMEOUT) {
                Serial.println("[TIMEOUT] Waiting for bobbins");
                currentState = STATE_ERROR;
            }
            break;
        }
        
        // ===== SCAN QR CODE 1 =====
        case STATE_SCAN_QR1:
            Serial.println("[INFO] Scanning QR Code 1...");
            triggerQRScanner(1);
            delay(QR_TRIGGER_DELAY);
            
            qrCode1 = readQRCode(qrScanner1, QR_TIMEOUT);
            
            if (qrCode1.length() > 0) {
                Serial.print("[SUCCESS] QR Code 1: ");
                Serial.println(qrCode1);
                updateLEDs(true, false, false, false);
                currentState = STATE_SCAN_QR2;
            } else {
                Serial.println("[ERROR] Failed to read QR Code 1");
                thread1Error = true;
                thread2Error = false;
                updateLEDs(false, false, true, false);
                currentState = STATE_ERROR;
            }
            break;
        
        // ===== SCAN QR CODE 2 =====
        case STATE_SCAN_QR2:
            Serial.println("[INFO] Scanning QR Code 2...");
            triggerQRScanner(2);
            delay(QR_TRIGGER_DELAY);
            
            qrCode2 = readQRCode(qrScanner2, QR_TIMEOUT);
            
            if (qrCode2.length() > 0) {
                Serial.print("[SUCCESS] QR Code 2: ");
                Serial.println(qrCode2);
                updateLEDs(true, true, false, false);
                currentState = STATE_VERIFY;
            } else {
                Serial.println("[ERROR] Failed to read QR Code 2");
                thread1Error = false;
                thread2Error = true;
                updateLEDs(true, false, false, true);
                currentState = STATE_ERROR;
            }
            break;
        
        // ===== VERIFY THREADS =====
        case STATE_VERIFY:
            if (verifyThreads()) {
                Serial.println("[SUCCESS] Thread verification passed!");
                Serial.println("==================================");
                currentState = STATE_READY;
            } else {
                Serial.println("[ERROR] Thread verification failed!");
                Serial.println("==================================");
                currentState = STATE_ERROR;
            }
            break;
        
        // ===== READY (MACHINE ENABLED) =====
        case STATE_READY: {
            static unsigned long lastCardCheck = 0;
            bool bobbin1Present = detectBobbin(BOBBIN1_PIN);
            bool bobbin2Present = detectBobbin(BOBBIN2_PIN);
            
            // Check Kanban card presence using PICC_WakeupA (non-intrusive method)
            if (millis() - lastCardCheck > CARD_CHECK_INTERVAL) {
                lastCardCheck = millis();
                
                if (!isKanbanCardStillPresent()) {
                    cardMissingCount++;
                    if (cardMissingCount >= CARD_MISSING_THRESHOLD) {
                        Serial.println("[WARNING] Kanban card removed! Restarting system...");
                        setMachineOutput(false);
                        updateLEDs(false, false, true, true);
                        delay(RESET_ALARM_DELAY);
                        clearProcessData();
                        rfid.PCD_Init();  // Reset RFID reader for next card detection
                        delay(RFID_RESET_DELAY);
                        currentState = STATE_WAIT_KANBAN;
                        break;
                    }
                } else {
                    cardMissingCount = 0;  // Reset counter if card detected
                }
            }
            
            // Check if any bobbin is removed → restart entire system
            if (!bobbin1Present || !bobbin2Present) {
                Serial.println("[WARNING] Bobbin removed! Restarting system...");
                setMachineOutput(false);
                updateLEDs(false, false, true, true);
                delay(RESET_ALARM_DELAY);
                clearProcessData();
                currentState = STATE_WAIT_KANBAN;
                break;
            }
            
            updateLEDs(true, true, false, false);
            setMachineOutput(true);
            break;
        }
        
        // ===== BYPASS MODE =====
        case STATE_BYPASS: {
            static unsigned long lastCardCheck = 0;
            
            // Check Kanban card presence using PICC_WakeupA (non-intrusive method)
            if (millis() - lastCardCheck > CARD_CHECK_INTERVAL) {
                lastCardCheck = millis();
                
                if (!isKanbanCardStillPresent()) {
                    cardMissingCount++;
                    if (cardMissingCount >= CARD_MISSING_THRESHOLD) {
                        Serial.println("[WARNING] Kanban card removed! Restarting system...");
                        setMachineOutput(false);
                        updateLEDs(false, false, true, true);
                        delay(RESET_ALARM_DELAY);
                        clearProcessData();
                        rfid.PCD_Init();  // Reset RFID reader for next card detection
                        delay(RFID_RESET_DELAY);
                        currentState = STATE_WAIT_KANBAN;
                        break;
                    }
                } else {
                    cardMissingCount = 0;  // Reset counter if card detected
                }
            }

            updateLEDs(true, true, false, false);
            setMachineOutput(true);
            break;
        }
        
        // ===== ERROR STATE =====
        case STATE_ERROR: {
            static unsigned long lastCardCheck = 0;
            
            // READY LEDs for matched threads, ALARM LEDs for mismatched threads
            updateLEDs(!thread1Error, !thread2Error, thread1Error, thread2Error);
            setMachineOutput(false);
            
            bool bobbin1Present = detectBobbin(BOBBIN1_PIN);
            bool bobbin2Present = detectBobbin(BOBBIN2_PIN);
            
            // Check Kanban card presence using PICC_WakeupA (non-intrusive method)
            if (millis() - lastCardCheck > CARD_CHECK_INTERVAL) {
                lastCardCheck = millis();
                
                if (!isKanbanCardStillPresent()) {
                    cardMissingCount++;
                    if (cardMissingCount >= CARD_MISSING_THRESHOLD) {
                        Serial.println("[WARNING] Kanban card removed! Restarting system...");
                        setMachineOutput(false);
                        updateLEDs(false, false, true, true);
                        delay(RESET_ALARM_DELAY);
                        clearProcessData();
                        rfid.PCD_Init();  // Reset RFID reader for next card detection
                        delay(RFID_RESET_DELAY);
                        currentState = STATE_WAIT_KANBAN;
                        break;
                    }
                } else {
                    cardMissingCount = 0;  // Reset counter if card detected
                }
            }
            
            // Reset when any bobbin removed (changing thread)
            if (!bobbin1Present || !bobbin2Present) {
                Serial.println("[INFO] Bobbin removed! Resetting system...");
                delay(RESET_ALARM_DELAY);
                clearProcessData();
                currentState = STATE_WAIT_KANBAN;
            }
            break;
        }
        
        default:
            currentState = STATE_WAIT_KANBAN;
            break;
    }
}

// =============== UTILITY FUNCTIONS ===============
const char* stateToString(SystemState state) {
    switch (state) {
        case STATE_INIT:         return "INIT";
        case STATE_WAIT_KANBAN:  return "WAIT_KANBAN";
        case STATE_READ_KANBAN:  return "READ_KANBAN";
        case STATE_WAIT_BOBBINS: return "WAIT_BOBBINS";
        case STATE_SCAN_QR1:     return "SCAN_QR1";
        case STATE_SCAN_QR2:     return "SCAN_QR2";
        case STATE_VERIFY:       return "VERIFY";
        case STATE_READY:        return "READY";
        case STATE_ERROR:        return "ERROR";
        case STATE_BYPASS:       return "BYPASS";
        default:                 return "UNKNOWN";
    }
}

void printState(SystemState state) {
    Serial.print("\n[STATE] ");
    Serial.println(stateToString(state));
}

String byteArrayToString(byte* buffer, byte bufferSize) {
    String result = "";
    for (byte i = 0; i < bufferSize; i++) {
        if (buffer[i] == 0) break; // Stop at null terminator
        if (buffer[i] >= 32 && buffer[i] <= 126) { // Printable ASCII
            result += (char)buffer[i];
        }
    }
    result.trim();
    return result;
}
