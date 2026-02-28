# HabCal - Habitability Calculator

**Hardware specifications and sensor systems for monitoring dwelling habitability**

---

## Overview

The **Habitability Calculator (HabCal)** is a sensor-based monitoring system that tracks environmental conditions within SOV-HAB dwellings and other sovereign living spaces. It continuously measures critical habitability parameters and provides real-time feedback on whether living conditions meet minimum livable thresholds.

HabCal integrates with the GhostStack civic OS to provide data-driven insights for community health monitoring, environmental optimization, and long-term sustainability tracking.

---

## Purpose

**Core Function:** Monitor and validate that dwelling conditions remain within habitability thresholds defined by:
- Community health standards
- Regulatory minimum requirements (where applicable)
- Occupant-defined comfort ranges
- Long-term sustainability metrics

**Key Applications:**
- SOV-HAB environmental monitoring
- Early warning for system failures (HVAC, water, insulation)
- Data collection for regenerative living optimization
- Proof-of-habitability for regulatory compliance
- Research data for autonomous dwelling design iteration

---

## Monitored Parameters

### Essential Habitability Metrics

| Parameter | Range (Threshold) | Sensor Type | Update Frequency |
|-----------|------------------|-------------|------------------|
| **Temperature** | 15-25°C (habitable) | Digital thermistor | 1 min |
| **Humidity** | 30-60% RH | Capacitive humidity sensor | 1 min |
| **CO₂ Concentration** | <1000 ppm (safe) | NDIR CO₂ sensor | 5 min |
| **Particulate Matter** | <25 µg/m³ PM2.5 | Laser particle counter | 5 min |
| **Light Level** | >200 lux (daytime) | Photodiode/LDR | 10 min |
| **Sound Level** | <55 dBA (quiet) | MEMS microphone | Continuous |
| **VOC Concentration** | <500 ppb | Metal oxide gas sensor | 10 min |

### Optional Extended Metrics

| Parameter | Purpose | Sensor Type |
|-----------|---------|-------------|
| **Barometric Pressure** | Weather prediction, altitude calibration | BMP/BME sensor |
| **Water Quality** | Potability monitoring (separate module) | TDS, pH, turbidity sensors |
| **Power Availability** | Battery state of charge | Voltage/current monitor |
| **Water Availability** | Tank level monitoring | Ultrasonic level sensor |

---

## System Architecture

### Hardware Components

**1. Sensor Module**
- Integrated PCB with all environmental sensors
- Low-power microcontroller (ESP32 or RP2040)
- LoRa radio for mesh network communication
- Optional WiFi for local data access
- USB-C power input (5V) or battery operation

**2. Data Logger**
- SD card storage for offline operation
- RTC (Real-Time Clock) for accurate timestamping
- Data retention: 6+ months at 1-minute intervals
- CSV export format for analysis

**3. Display Interface**
- e-Paper or OLED display showing current conditions
- LED indicator array (green/yellow/red for each parameter)
- Optional web interface for detailed historical data
- Audible alarm for critical threshold violations

**4. Enclosure**
- Wall-mounted or freestanding design
- 3D-printable housing (STL files provided)
- Ventilated sensor exposure chamber
- Mounting options for standard stud spacing

---

## Specifications

### Sensor Module PCB

| Specification | Value |
|--------------|-------|
| Dimensions | 100 × 60 × 25 mm (enclosure) |
| Power Input | 5V USB-C or 3.7V LiPo battery |
| Power Consumption | <500 mW (active), <50 mW (sleep) |
| Operating Temp Range | -10°C to +50°C |
| Communication | LoRa (868/915 MHz), WiFi (optional) |
| Data Storage | MicroSD (up to 32 GB) |
| Calibration Interval | 12 months (CO₂, VOC sensors) |

### Sensor Accuracy (Typical)

| Sensor | Accuracy |
|--------|----------|
| Temperature | ±0.5°C |
| Humidity | ±3% RH |
| CO₂ | ±50 ppm + 3% of reading |
| PM2.5 | ±10 µg/m³ or ±10% |
| Light | ±15% |
| Sound | ±2 dBA |
| VOC | ±15% |

---

## Installation

### Mounting Location

**Optimal Placement:**
- Wall-mounted at breathing height (~1.5m above floor)
- Central location within dwelling (avoid corners, direct sunlight, HVAC vents)
- Minimum 0.5m clearance from windows, doors, heat sources
- Away from cooking area (prevents false high readings)

**Multi-Room Installations:**
- One sensor per occupied room (bedroom, living area)
- Additional sensor near air intake/circulation system
- Outdoor reference sensor (optional) for comparison

### Wiring and Power

**Power Options:**
1. **USB-C Mains Power** (recommended for continuous operation)
2. **Battery Operation** (3.7V LiPo, ~1 week autonomy with hourly logging)
3. **Solar Panel** (5V, 500mA for off-grid installations)

**Data Connectivity:**
- LoRa mesh (primary): No wiring required, auto-joins network
- WiFi (optional): Connect to local network for web dashboard access
- Wired Ethernet (future): For high-reliability fixed installations

---

## Calibration Procedures

### Initial Calibration (Factory)

All sensors are factory-calibrated prior to shipment. Calibration certificates included with each unit.

### Field Calibration (Annual Recommended)

**CO₂ Sensor (NDIR):**
1. Place sensor in fresh outdoor air (≈400 ppm reference)
2. Allow 10-minute stabilization period
3. Trigger calibration routine via button/web interface
4. Record calibration timestamp

**VOC Sensor (Metal Oxide):**
1. Place sensor in clean, ventilated environment
2. Allow 24-hour burn-in period
3. Baseline auto-calibrates during first week of operation
4. Manual recalibration if relocated to different environment

**Particulate Sensor:**
1. Gently clean optical chamber with compressed air
2. Verify zero reading in HEPA-filtered environment
3. No electronic calibration required (optical measurement)

**Temperature/Humidity:**
- Factory-calibrated; no field adjustment required
- Verify against certified reference thermometer annually
- Replace sensor if drift exceeds ±1°C or ±5% RH

---

## Data Logging and Export

### Local Storage

- **Format:** CSV (comma-separated values)
- **Filename Convention:** `habcal_YYYYMMDD.csv`
- **Columns:** Timestamp, Temp, Humidity, CO2, PM25, Light, Sound, VOC, Status
- **Storage Capacity:** 32 GB SD card = ~10 years of 1-minute data

### Mesh Network Integration

- Real-time data streamed to GhostStack via LoRa mesh
- Automated alerts when thresholds exceeded
- Community-wide environmental trend analysis
- Privacy-preserving aggregation (individual dwellings anonymized)

### Web Dashboard (Optional)

- Local web server (IP: http://habcal.local)
- Live readings with historical graphs (24h, 7d, 30d views)
- Threshold configuration interface
- Export CSV for external analysis (R, Python, Excel)

---

## Alarm and Notification System

### Alert Levels

| Level | Condition | Indication | Action |
|-------|-----------|------------|--------|
| **Green** | All parameters within range | Green LED | None |
| **Yellow** | Parameter approaching threshold | Yellow LED | Log warning |
| **Red** | Critical threshold exceeded | Red LED + buzzer | Immediate notification |
| **Critical** | Multiple parameters failed | Flashing red + alarm | Emergency protocol |

### Notification Channels

1. **Local Visual/Audio:** LED array + buzzer on device
2. **Mesh Alert:** Broadcast to GhostStack governance system
3. **Mobile App:** Push notification (if WiFi connected)
4. **Email/SMS:** Via external gateway (optional, requires internet)

---

## Bill of Materials (BOM)

### Core Sensors

| Component | Specification | Supplier | Approx. Cost (USD) |
|-----------|--------------|----------|-------------------|
| Temperature/Humidity | SHT31, SHT40 | Adafruit, Mouser | $5-8 |
| CO₂ Sensor | SCD30, SCD40 (NDIR) | Sensirion | $40-60 |
| Particulate Sensor | PMS5003, SPS30 | Plantower, Sensirion | $15-40 |
| VOC Sensor | SGP30, BME680 | Sensirion, Bosch | $8-15 |
| Light Sensor | BH1750, TSL2561 | Mouser, Adafruit | $3-5 |
| Sound Sensor | MEMS mic + SPL calc | InvenSense, TDK | $2-5 |

### Electronics

| Component | Specification | Approx. Cost (USD) |
|-----------|--------------|-------------------|
| Microcontroller | ESP32-C3, RP2040 | $3-8 |
| LoRa Radio | RFM95W (868/915 MHz) | $8-12 |
| RTC | DS3231 (I²C) | $3-5 |
| MicroSD Slot | Card holder + level shifter | $2-3 |
| Power Management | LDO regulator, USB-C PD | $3-5 |
| PCB (Custom) | 2-layer, 100×60 mm | $10-20 (batch) |

### Enclosure and Mounting

| Component | Specification | Approx. Cost (USD) |
|-----------|--------------|-------------------|
| Enclosure | 3D-printed ABS/PETG | $5-10 (material) |
| Display (Optional) | 2.9" e-Paper or 0.96" OLED | $10-25 |
| LEDs | 5mm RGB or discrete R/Y/G | $0.50 |
| Buzzer | Piezo 3-5V | $1 |
| Mounting Hardware | Screws, anchors, backplate | $2-5 |

**Total Estimated Cost (DIY Assembly):** $120-180 USD
**Total Estimated Cost (Pre-Assembled):** $200-250 USD

---

## Firmware and Software

### Microcontroller Firmware

**Language:** C/C++ (Arduino/ESP-IDF framework)
**Source:** `/src/habcal/firmware/`
**License:** AGPL-3.0

**Key Features:**
- Sensor polling and data aggregation
- Threshold monitoring and alert triggering
- LoRa mesh protocol integration
- Web server for local dashboard (optional)
- SD card logging with rotation
- OTA (Over-The-Air) firmware updates

### Data Analysis Tools

**Language:** Python
**Source:** `/src/habcal/analysis/`

**Scripts Include:**
- CSV import and cleaning
- Habitability score calculation
- Anomaly detection (sensor drift, failures)
- Long-term trend visualization
- Comparative analysis (multiple dwellings)

### Web Dashboard

**Framework:** React (static build) or simple HTML/CSS/JS
**Source:** `/src/habcal/dashboard/`

**Features:**
- Real-time gauges for all parameters
- Historical charts (Chart.js or D3.js)
- Threshold configuration UI
- CSV export button
- Mobile-responsive design

---

## Regulatory and Compliance

### Safety Standards

**Electrical Safety:**
- Low-voltage operation (<50V DC)
- USB-C PD compliant power supply
- No exposed high-voltage components

**Sensor Certifications:**
- CO₂ sensors: NDIR technology (no chemical consumables)
- VOC sensors: RoHS compliant
- All sensors meet EU/UK safety standards

### Data Privacy

**Local-First Design:**
- All data stored locally on SD card (no cloud dependency)
- Mesh transmission encrypted (end-to-end)
- Web dashboard accessible only on local network (no internet exposure by default)
- Opt-in data sharing for community aggregation

**GDPR Compliance:**
- No personal data collected (environmental readings only)
- User retains full control over data export/deletion
- Anonymized aggregation for community statistics

---

## Maintenance and Lifespan

### Routine Maintenance

| Task | Frequency | Procedure |
|------|-----------|-----------|
| **Sensor Cleaning** | 6 months | Gently clean particulate sensor intake with compressed air |
| **Calibration Check** | 12 months | Verify CO₂ and VOC calibration per procedures above |
| **SD Card Check** | 12 months | Verify data integrity, replace if errors detected |
| **Firmware Update** | As released | OTA update via web interface or USB |
| **Battery Replacement** | 2-3 years | Replace LiPo battery if capacity degrades (battery-powered units) |

### Expected Lifespan

| Component | Expected Lifespan | Failure Mode |
|-----------|------------------|--------------|
| **Temperature/Humidity** | 10+ years | Drift (recalibration extends life) |
| **CO₂ Sensor (NDIR)** | 10-15 years | Optical degradation |
| **Particulate Sensor** | 5-10 years | Fan/laser failure |
| **VOC Sensor** | 5-10 years | Baseline drift |
| **Microcontroller/Electronics** | 15+ years | Component failure (capacitors) |
| **Enclosure** | 20+ years | UV degradation (if outdoors) |

**Design Philosophy:** All sensors are modular and user-replaceable. No proprietary components.

---

## Future Development

### Planned Enhancements

- **Water Quality Module:** Integrated TDS, pH, turbidity sensors for potability monitoring
- **Energy Monitor Integration:** Direct read from SOV-HAB battery/solar systems
- **Predictive Maintenance:** Machine learning for early failure detection
- **Multi-Dwelling Comparison:** Automated benchmarking against community averages
- **External Sensors:** Soil moisture, outdoor weather station integration

### Research Opportunities

- **Habitability Scoring Algorithm:** Develop weighted composite score from all parameters
- **Long-Term Health Correlation:** Link environmental data to occupant health outcomes
- **Energy-Environment Optimization:** Identify HVAC efficiency improvements from sensor data
- **Climate Adaptation:** Track seasonal patterns and dwelling performance over years

---

## Troubleshooting

### Common Issues

| Symptom | Probable Cause | Solution |
|---------|---------------|----------|
| **High CO₂ readings** | Insufficient ventilation | Open windows, check HVAC intake |
| **High humidity** | Poor insulation, water leak | Inspect for moisture sources, improve ventilation |
| **Erratic readings** | Sensor contamination | Clean sensor chamber, recalibrate |
| **No data logging** | SD card failure | Replace SD card, verify formatting (FAT32) |
| **Mesh connection lost** | LoRa radio failure or obstruction | Check antenna connection, verify mesh node proximity |
| **Battery drains quickly** | High polling frequency or radio transmit power | Reduce update frequency, lower LoRa TX power |

---

## Contributing

### Hardware Improvements

- Submit PCB design improvements via pull request
- Share alternative sensor selections (cost/performance trade-offs)
- Contribute enclosure designs for different mounting scenarios

### Firmware Development

- Add support for new sensors
- Improve power efficiency
- Enhance mesh protocol reliability

### Data Analysis

- Develop better habitability scoring algorithms
- Create visualization templates
- Build predictive models for system optimization

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution workflow.

---

## Licensing

**Hardware Designs:** AGPL-3.0 (Small Operators: full commercial rights; Large Entities: internal non-commercial use only)
**Firmware/Software:** AGPL-3.0
**Documentation:** CC BY-SA 4.0

Large Entities seeking commercial manufacturing or services require a paid license. Contact sovereign@ghoststack.dev.

See [LICENSE.md](../../LICENSE.md) for complete terms.

---

## Status

**Current Phase:** Specification and Design
**Prototype Status:** Not yet built
**Target Completion:** Q2 2026

---

## References

- **Sensor Datasheets:** `/hardware/habcal/datasheets/`
- **PCB Schematics:** `/hardware/habcal/schematics/` (KiCAD format)
- **Firmware Source:** `/src/habcal/firmware/`
- **3D Models:** `/hardware/habcal/enclosures/` (STL, OpenSCAD)

---

## Contact

**Technical Questions:** https://github.com/vanj900
**Build Support:** https://github.com/vanj900
**Bug Reports:** Open an issue with `[HabCal]` tag

---

*"Habitability is not a luxury. It is a measurable, achievable threshold—and every human deserves to live above it."*
