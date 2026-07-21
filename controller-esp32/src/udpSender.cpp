#include "udpSender.h"

#include <WiFi.h>
#include <WiFiUdp.h>



// WiFi credentials broadcast by the tank Uno R4.
const char* WIFI_SSID = "Tank_AP";
const char* WIFI_PASS = "12345678";

#define UDP_PORT 4210
#define COORDINATE_PRINT_INTERVAL_MS 1000
#define WIFI_CONNECTION_ATTEMPT_TIMEOUT_MS 10000
#define UDP_SOCKET_RECOVERY_INTERVAL_MS 1000
#define UDP_SEND_FAILURE_LIMIT 3
#define UDP_TX_FAULT_BACKOFF_MS 100

static WiFiUDP udp;

static IPAddress tankIP(192, 168, 4, 1);
static unsigned long lastCoordinatePrintTime = 0;
static unsigned long lastWifiConnectionStartTime = 0;
static unsigned long lastSocketRecoveryAttemptTime = 0;
static bool wifiWasConnected = false;
static bool udpReady = false;
static bool suppressCommandAfterConnection = false;
static uint8_t consecutiveUdpSendFailures = 0;
static unsigned long lastUdpSendFailureTime = 0;
static bool udpFaultReported = false;

static bool isEmptyIp(IPAddress ip) {
    // Check if an IP is 0.0.0.0, i.e. invalid.
    return ip[0] == 0 && ip[1] == 0 && ip[2] == 0 && ip[3] == 0;
}

static void resetUdpSendFailures() {
    consecutiveUdpSendFailures = 0;
    udpFaultReported = false;
}

// Comparison using unsigned subtraction remains correct even when millis() wraps.
static bool udpTxBackoffActive(unsigned long now) {
    return consecutiveUdpSendFailures >= UDP_SEND_FAILURE_LIMIT &&
           now - lastUdpSendFailureTime < UDP_TX_FAULT_BACKOFF_MS;
}

static const char* wifiStatusName(wl_status_t status) {
    switch (status) {
        case WL_IDLE_STATUS:
            return "IDLE";
            case WL_NO_SSID_AVAIL:
                return "SSID_NOT_FOUND";
            case WL_SCAN_COMPLETED:
                return "SCAN_COMPLETED";
            case WL_CONNECTED:
                return "CONNECTED";
            case WL_CONNECT_FAILED:
                return "CONNECT_FAILED";
            case WL_CONNECTION_LOST:
                return "CONNECTION_LOST";
            case WL_DISCONNECTED:
                return "DISCONNECTED";
        default:
            return "UNKNOWN_STATUS";
    }
}

static void startWifiConnectionAttempt(unsigned long now, bool resetConnection) {
    lastWifiConnectionStartTime = now;

    if (resetConnection) {
        WiFi.disconnect(false, false);
    }

    WiFi.begin(WIFI_SSID, WIFI_PASS);
}

// ENOMEM from endPacket() indicates sendto() cannot queue the datagram in the
// WiFi/lwIP stack. Closing and reopening the socket here would require a new
// allocation of the UDP buffer (1460 bytes), worsening this condition.
static void registerUdpSendFailure() {
    if (consecutiveUdpSendFailures < UDP_SEND_FAILURE_LIMIT) {
        consecutiveUdpSendFailures++;
    }

    lastUdpSendFailureTime = millis();

    if (consecutiveUdpSendFailures == UDP_SEND_FAILURE_LIMIT && !udpFaultReported) {
        udpFaultReported = true;
        Serial.println("UDP TX temporarily saturated: scheduled recovery pause");
    }
}

// Update the tank address and reopen UDP after each new connection.
// An unopened socket is not treated as an operational control channel.
static bool configureUdpConnection() {
    IPAddress gateway = WiFi.gatewayIP();
    if (!isEmptyIp(gateway)) {
        tankIP = gateway;
    }

    udp.stop();
    udpReady = udp.begin(UDP_PORT) == 1;
    lastSocketRecoveryAttemptTime = millis();
    lastCoordinatePrintTime = millis();
    JoystickReader_requireNeutralBeforeCommands();
    suppressCommandAfterConnection = true;

    if (!udpReady) {
        Serial.println("ERROR: controller UDP socket not available");
        return false;
    }

    resetUdpSendFailures();
    Serial.println("WiFi connected to tank");
    Serial.print("Controller IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("Tank IP: ");
    Serial.println(tankIP);
    return true;
}

static bool ensureWifiConnected() {
    unsigned long now = millis();

    if (WiFi.status() == WL_CONNECTED) {
        if (!wifiWasConnected) {
            wifiWasConnected = true;
            return configureUdpConnection();
        }

        // Even with WiFi associated, the initial socket open can fail.
        // ENOMEM send errors are handled without recreating the socket.
        if (!udpReady && now - lastSocketRecoveryAttemptTime >= UDP_SOCKET_RECOVERY_INTERVAL_MS) {
            lastSocketRecoveryAttemptTime = now;
            return configureUdpConnection();
        }

        return udpReady;
    }

    if (wifiWasConnected) {
        wifiWasConnected = false;
        udpReady = false;
        resetUdpSendFailures();
        udp.stop();
        Serial.println("WiFi lost: the tank will enter the safety timeout");

        startWifiConnectionAttempt(now, true);
        return false;
    }

    if (now - lastWifiConnectionStartTime >= WIFI_CONNECTION_ATTEMPT_TIMEOUT_MS) {
        Serial.print("New controlled WiFi attempt to Tank_AP (status: ");
        Serial.print(wifiStatusName(WiFi.status()));
        Serial.println(")...");

        startWifiConnectionAttempt(now, true);
    }

    return false;
}

void UdpSender_begin() {
    Serial.print("Connecting to ");
    Serial.println(WIFI_SSID);

    WiFi.mode(WIFI_STA);
    WiFi.persistent(false);
    WiFi.setAutoReconnect(false);
    WiFi.setSleep(false);
    startWifiConnectionAttempt(millis(), false);
    udpReady = false;
    resetUdpSendFailures();
    lastSocketRecoveryAttemptTime = millis();
}

/*
 * UDP SENDING METHOD
 *
 * The tank creates the WiFi network. The ESP32 connects as a client and sends
 * UDP packets to the tank's IP address. The message is a compact string:
 *
 * V1;driveX;driveY;turretX;elevationY;zero;fire
 */
void UdpSender_send(const ControllerData& data) {
    if (!ensureWifiConnected()) {
        return;
    }

    // Discard the sample read before the WiFi state change. From the next
    // cycle JoystickReader_read() returns only the safe command until
    // joysticks and buttons are neutral and released.
    if (suppressCommandAfterConnection) {
        suppressCommandAfterConnection = false;
        return;
    }

    // After three consecutive ENOMEMs, give the WiFi queue time to drain.
    // If the radio does not recover, the tank's independent timeout will stop the vehicle.
    if (udpTxBackoffActive(millis())) {
        return;
    }

    char message[64];

    int messageLength =
        snprintf(message, sizeof(message), "V1;%d;%d;%d;%d;%d;%d", data.driveX, data.driveY,
                 data.turretX, data.elevationY, data.zeroPressed ? 1 : 0, data.firePressed ? 1 : 0);

    if (messageLength <= 0 || messageLength >= static_cast<int>(sizeof(message))) {
        Serial.println("ERROR: invalid controller UDP packet");
        return;
    }

    if (udp.beginPacket(tankIP, UDP_PORT) == 0) {
        registerUdpSendFailure();
        return;
    }

    size_t writtenBytes = udp.print(message);
    int packetSent = udp.endPacket();
    if (writtenBytes != static_cast<size_t>(messageLength) || packetSent != 1) {
        registerUdpSendFailure();
        return;
    }

    resetUdpSendFailures();
    if (millis() - lastCoordinatePrintTime > COORDINATE_PRINT_INTERVAL_MS) {
        lastCoordinatePrintTime = millis();

        Serial.println();
        Serial.println("=== ESP32 TX UDP ===");
        Serial.print("Joy1 drive     X=");
        Serial.print(data.driveX);
        Serial.print(" Y=");
        Serial.println(data.driveY);
        Serial.print("Joy2 turret    X=");
        Serial.print(data.turretX);
        Serial.print(" elevation Y=");
        Serial.println(data.elevationY);
        Serial.print("Buttons        zero=");
        Serial.print(data.zeroPressed ? "PRESSED" : "off");
        Serial.print(" fire=");
        Serial.println(data.firePressed ? "PRESSED" : "off");
        Serial.println("===================");
    }
}
