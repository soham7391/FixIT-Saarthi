from typing import Dict, List, Any
from app.schemas.diagnostic import SafetyLevel, FixStep


DRIVER_SYMPTOMS: Dict[str, Dict[str, Any]] = {
    "printer_not_detected": {
        "name": "Printer Not Detected or Not Printing",
        "description": "Printer is offline, unresponsive, or fails to print documents",
        "type": "boolean"
    },
    "keyboard_mouse_unresponsive": {
        "name": "Keyboard or Mouse Unresponsive",
        "description": "Keyboard keys or mouse cursor do not react to input",
        "type": "boolean"
    },
    "audio_device_issue": {
        "name": "Audio Device Issue (Sound/Mic)",
        "description": "Speakers produce no sound or microphone captures no input",
        "type": "boolean"
    },
    "webcam_unavailable": {
        "name": "Webcam / Camera Unavailable",
        "description": "Webcam is not detected or shows a black/error screen in apps",
        "type": "boolean"
    },
    "bluetooth_connection_failed": {
        "name": "Bluetooth Peripheral Connection Failure",
        "description": "Bluetooth device fails to pair, connect, or maintain connection",
        "type": "boolean"
    },
    "device_failed_after_update": {
        "name": "Device Failed After Driver/Windows Update",
        "description": "Peripheral stopped functioning immediately following a system update",
        "type": "boolean"
    },
    "usb_physical_disconnection": {
        "name": "USB Cable or Port Disconnected",
        "description": "USB device is loose, unplugged, or connected to an unpowered port",
        "type": "boolean"
    },
    "app_permissions_blocked": {
        "name": "Privacy Settings Blocking Device",
        "description": "Windows privacy settings blocking camera or microphone access",
        "type": "boolean"
    }
}


DRIVER_CAUSES: List[Dict[str, Any]] = [
    {
        "cause_id": "cause_device_disconnected_power",
        "cause_name": "Physical Cable Disconnection, Power Off, or Low Battery",
        "description": "The peripheral device is physically unplugged, toggled off, or running on depleted battery power.",
        "symptom_weights": {
            "usb_physical_disconnection": 0.50,
            "keyboard_mouse_unresponsive": 0.30,
            "printer_not_detected": 0.20
        },
        "min_threshold": 0.35,
        "explanation": "The physical connection, power toggle, or wireless battery level is preventing device communication.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Inspect Cable Connections and Power Switch",
                instruction="Ensure the USB cable or wireless dongle is firmly seated. Verify device power switch is ON and battery is charged.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Does the device power indicator light up when plugged in?"
            ),
            FixStep(
                step_number=2,
                title="Test on an Alternate USB Port",
                instruction="Disconnect the peripheral and plug it into a direct rear motherboard USB port (avoid unpowered USB hubs).",
                safety_level=SafetyLevel.SAFE,
                verification_question="Does Windows play a connection chime or recognize the device in a different port?"
            )
        ]
    },
    {
        "cause_id": "cause_audio_output_input_misconfiguration",
        "cause_name": "Incorrect Audio Playback or Recording Device Selection",
        "description": "Windows sound output or microphone input is routed to an inactive audio device or muted.",
        "symptom_weights": {
            "audio_device_issue": 0.70,
            "device_failed_after_update": 0.30
        },
        "min_threshold": 0.35,
        "explanation": "Windows audio endpoint router has selected the wrong default speaker or microphone.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Verify Windows Default Sound Output and Input Device",
                instruction="Click the Speaker icon in bottom-right taskbar -> Sound Output icon (or press Win + Ctrl + V). Ensure the correct headphones/speakers and microphone are selected.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Does test sound play when selecting the correct playback device?"
            ),
            FixStep(
                step_number=2,
                title="Check Volume Levels and Mute Toggles",
                instruction="Open Settings -> System -> Sound. Ensure volume is above 0% and physical inline mute switches on headsets are disabled.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Are audio meter bars moving when playing audio or speaking?"
            )
        ]
    },
    {
        "cause_id": "cause_privacy_permissions_blocked",
        "cause_name": "Windows Privacy Settings Blocking App Access",
        "description": "Windows Camera or Microphone privacy toggles are turned off, preventing applications from accessing the device.",
        "symptom_weights": {
            "app_permissions_blocked": 0.60,
            "webcam_unavailable": 0.25,
            "audio_device_issue": 0.15
        },
        "min_threshold": 0.35,
        "explanation": "Windows security policy is blocking browser or desktop applications from opening camera/microphone hardware.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Enable Camera & Microphone Access in Windows Settings",
                instruction="Open Settings -> Privacy & security -> Camera (and Microphone). Toggle 'Camera access' to ON and ensure 'Let apps access your camera' is ON.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Can video/audio applications now access the webcam and microphone?"
            ),
            FixStep(
                step_number=2,
                title="Verify Browser/App Specific Device Permissions",
                instruction="In your web browser or app settings (e.g. Zoom/Teams), check site settings to ensure camera and microphone permission is 'Allow'.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Does the camera feed preview work in app settings?"
            )
        ]
    },
    {
        "cause_id": "cause_bluetooth_pairing_connection",
        "cause_name": "Bluetooth Adapter Disabled or Corrupt Device Pairing",
        "description": "Bluetooth service is turned off or existing device pairing cache is stale.",
        "symptom_weights": {
            "bluetooth_connection_failed": 0.65,
            "keyboard_mouse_unresponsive": 0.20,
            "audio_device_issue": 0.15
        },
        "min_threshold": 0.35,
        "explanation": "Bluetooth radio adapter is disabled or stale pairing cache prevents re-establishing a secure link.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Toggle Bluetooth Radio and Re-pair Device",
                instruction="Open Settings -> Bluetooth & devices. Toggle Bluetooth OFF for 5 seconds, then back ON. Click 'Remove device' on your peripheral, put it in pairing mode, and click 'Add device'.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Does the Bluetooth device successfully complete re-pairing and show 'Connected'?"
            ),
            FixStep(
                step_number=2,
                title="Restart Bluetooth Support Service",
                instruction="Press Win + R, type 'services.msc'. Right-click 'Bluetooth Support Service' -> select 'Restart'. Set Startup type to Automatic.",
                safety_level=SafetyLevel.CAUTION,
                warning_note="Restarting services temporarily drops all active Bluetooth connections.",
                verification_question="Did restarting the Bluetooth service restore connection capability?"
            )
        ]
    },
    {
        "cause_id": "cause_driver_update_rollback",
        "cause_name": "Corrupt or Incompatible Device Driver After Update",
        "description": "A recent Windows or driver update installed an incompatible software driver for your hardware device.",
        "symptom_weights": {
            "device_failed_after_update": 0.55,
            "printer_not_detected": 0.25,
            "webcam_unavailable": 0.20
        },
        "min_threshold": 0.35,
        "explanation": "Device driver binaries in Windows system store were corrupted or replaced with incompatible drivers during an update.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Roll Back Device Driver in Device Manager",
                instruction="Press Win + X -> Device Manager. Expand target device category, right-click your device -> Properties -> Driver tab -> click 'Roll Back Driver'.",
                safety_level=SafetyLevel.CAUTION,
                warning_note="Rolling back driver restores the previous functional driver version.",
                verification_question="Did rolling back the driver restore device functionality?"
            ),
            FixStep(
                step_number=2,
                title="Uninstall Device and Scan for Hardware Changes",
                instruction="In Device Manager, right-click the failing device -> 'Uninstall device'. Do NOT check 'Delete driver software'. Then click Action -> 'Scan for hardware changes'.",
                safety_level=SafetyLevel.ADVANCED,
                warning_note="Windows will re-detect the hardware and reinstall default clean drivers upon scan.",
                verification_question="Does Device Manager reinstall the device clean without warning icons?"
            )
        ]
    },
    {
        "cause_id": "cause_hardware_peripheral_fault",
        "cause_name": "Peripheral Hardware Malfunction or Defective Port",
        "description": "Physical hardware fault in the peripheral device controller, cable wiring, or motherboards USB controller.",
        "symptom_weights": {
            "keyboard_mouse_unresponsive": 0.40,
            "printer_not_detected": 0.30,
            "usb_physical_disconnection": 0.30
        },
        "min_threshold": 0.35,
        "explanation": "Internal electronic circuit failure or damaged USB connector pins prevent hardware detection across all computers.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Cross-Test Peripheral on Another Computer",
                instruction="Plug the peripheral into a second computer or laptop to isolate whether the fault is in the device or your PC.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Does the device fail to work on a second computer as well?"
            ),
            FixStep(
                step_number=2,
                title="Replace Cable / Contact Hardware Repair or Manufacturer",
                instruction="If available, replace detachable USB power/data cable. If failure persists across computers, contact manufacturer for warranty or replacement.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Does replacing the cable or testing a replacement device resolve the issue?"
            )
        ]
    }
]
