from typing import Dict, List, Any
from app.schemas.diagnostic import SafetyLevel, FixStep


BOOT_SYMPTOMS: Dict[str, Dict[str, Any]] = {
    "slow_boot_time": {
        "name": "Slow Boot Time",
        "description": "System takes a long time (minutes) to boot to desktop",
        "type": "boolean"
    },
    "stuck_on_logo": {
        "name": "Stuck on Boot Logo",
        "description": "Stuck on manufacturer or Windows logo or spinning dots screen",
        "type": "boolean"
    },
    "boot_error_screen": {
        "name": "Boot Error Screen / BSOD",
        "description": "Windows shows error screen (BSOD / Boot BCD error / Startup Repair)",
        "type": "boolean"
    },
    "reboot_loop": {
        "name": "Repeated Reboot Loop",
        "description": "Computer repeatedly restarts before reaching desktop",
        "type": "boolean"
    },
    "slow_desktop_usable": {
        "name": "Slow Desktop Response After Login",
        "description": "Desktop loads but icons and apps take long before system becomes responsive",
        "type": "boolean"
    },
    "recent_windows_update": {
        "name": "Recent Windows Update / Driver Change",
        "description": "Issue started right after a recent Windows update or driver install",
        "type": "boolean"
    },
    "external_drives_connected": {
        "name": "External USB Drives Connected",
        "description": "External hard drives, flash drives, or memory cards connected during startup",
        "type": "boolean"
    },
    "disk_space_low": {
        "name": "Low System Disk Space",
        "description": "System C: drive has very low free storage space",
        "type": "boolean"
    },
    "disk_clicking_noise": {
        "name": "Clicking / Grinding Drive Noise",
        "description": "Storage drive making unusual clicking, grinding, or slow read/write sounds",
        "type": "boolean"
    }
}


BOOT_CAUSES: List[Dict[str, Any]] = [
    {
        "cause_id": "cause_startup_app_overload",
        "cause_name": "Startup Application & Background Service Overload",
        "description": "Too many autostart applications and services launch during boot, delaying desktop usability.",
        "symptom_weights": {
            "slow_desktop_usable": 0.50,
            "slow_boot_time": 0.30,
            "recent_windows_update": 0.20
        },
        "min_threshold": 0.30,
        "explanation": "Multiple autostart applications delay desktop responsiveness after login.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Disable Non-Essential Startup Programs",
                instruction="Open Task Manager (Ctrl + Shift + Esc) -> Startup apps tab. Right-click non-essential programs (browsers, launchers) and select 'Disable'.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Did disabling startup programs decrease startup loading time?"
            ),
            FixStep(
                step_number=2,
                title="Perform Clean Boot Service Isolation",
                instruction="Press Win + R, type 'msconfig' -> Services tab -> Check 'Hide all Microsoft services' -> Click 'Disable all'. Reboot computer.",
                safety_level=SafetyLevel.CAUTION,
                warning_note="Ensure 'Hide all Microsoft services' is checked to avoid disabling core Windows OS services.",
                verification_question="Does Windows boot faster after performing a clean boot?"
            )
        ]
    },
    {
        "cause_id": "cause_disk_space_pressure",
        "cause_name": "Low Storage Space on System Drive (C:)",
        "description": "Primary system drive C: has critically low free storage, bottlenecking virtual memory and boot caches.",
        "symptom_weights": {
            "disk_space_low": 0.60,
            "slow_boot_time": 0.25,
            "slow_desktop_usable": 0.15
        },
        "min_threshold": 0.35,
        "explanation": "Low disk space on the primary system drive (C:) prevents Windows from allocating virtual memory and boot caches efficiently.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Clear Temporary Files and Storage Sense",
                instruction="Open Settings -> System -> Storage -> Temporary files. Select 'Remove files' to free up disk space on C:.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Did temporary file cleanup free up at least 5-10 GB on C: drive?"
            ),
            FixStep(
                step_number=2,
                title="Uninstall Unused Large Applications",
                instruction="Open Settings -> Apps -> Installed apps. Sort by size and uninstall non-essential large games or software.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Is system disk C: now showing free space highlighted in blue?"
            )
        ]
    },
    {
        "cause_id": "cause_recent_update_issue",
        "cause_name": "Pending or Interrupted Windows Update",
        "description": "A recent Windows update or driver change left startup system files in an incomplete or rolling back state.",
        "symptom_weights": {
            "recent_windows_update": 0.50,
            "boot_error_screen": 0.25,
            "stuck_on_logo": 0.25
        },
        "min_threshold": 0.35,
        "explanation": "A recent Windows update or driver installation interrupted startup configuration or triggered an update rollback loop.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Boot into Safe Mode & Uninstall Recent Updates",
                instruction="Hold Shift while clicking Restart -> Troubleshoot -> Advanced options -> Startup Settings -> Restart. Select 4 (Safe Mode). Go to Settings -> Windows Update -> Update history -> Uninstall updates.",
                safety_level=SafetyLevel.CAUTION,
                warning_note="Safe Mode disables third-party drivers. Only uninstall recent updates if startup problems started immediately after updating.",
                verification_question="Did Windows boot successfully into Safe Mode?"
            ),
            FixStep(
                step_number=2,
                title="Run Windows Startup Repair",
                instruction="Force shutdown 2-3 times during boot to enter Windows Recovery -> Troubleshoot -> Advanced options -> Startup Repair.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Did Startup Repair finish and allow normal Windows boot?"
            )
        ]
    },
    {
        "cause_id": "cause_peripheral_boot_conflict",
        "cause_name": "Connected External Peripheral Conflict",
        "description": "External USB hard drive, flash drive, or card reader interfering with BIOS/UEFI boot order sequence.",
        "symptom_weights": {
            "external_drives_connected": 0.60,
            "stuck_on_logo": 0.40
        },
        "min_threshold": 0.35,
        "explanation": "External USB devices connected at startup confuse BIOS boot order or delay hardware device detection.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Disconnect All External USB Peripherals",
                instruction="Unplug external hard drives, USB flash drives, memory cards, and USB hubs. Restart the computer.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Does the computer boot normally without external USB drives attached?"
            ),
            FixStep(
                step_number=2,
                title="Check BIOS/UEFI Boot Device Priority",
                instruction="Restart and press F2/Del to enter BIOS. Ensure your primary internal SSD/HDD is set as 'Boot Option #1'.",
                safety_level=SafetyLevel.CAUTION,
                warning_note="Do not change other hardware settings in BIOS/UEFI.",
                verification_question="Is the internal system drive set as the first boot option?"
            )
        ]
    },
    {
        "cause_id": "cause_boot_file_corruption",
        "cause_name": "System File or Boot Configuration (BCD) Error",
        "description": "Windows boot system files or BCD entries are corrupted, causing startup error screens or reboot loops.",
        "symptom_weights": {
            "boot_error_screen": 0.45,
            "reboot_loop": 0.35,
            "stuck_on_logo": 0.20
        },
        "min_threshold": 0.35,
        "explanation": "Essential boot configuration files (BCD) or Windows kernel system files contain integrity errors.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Run Automated Windows Startup Repair",
                instruction="Boot into Windows Recovery -> Troubleshoot -> Advanced options -> Startup Repair.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Did Startup Repair complete successfully?"
            ),
            FixStep(
                step_number=2,
                title="Run System File Checker (SFC) in Command Prompt",
                instruction="In Advanced options -> Command Prompt, type 'sfc /scannow /offbootdir=C:\\ /offwindir=C:\\Windows' and press Enter.",
                safety_level=SafetyLevel.ADVANCED,
                warning_note="Advanced command line tool. Verify correct drive letters before executing.",
                verification_question="Did SFC complete and report corrupted system files repaired?"
            ),
            FixStep(
                step_number=3,
                title="Rebuild Boot Configuration Data (BCD)",
                instruction="In Recovery Command Prompt, run 'bootrec /fixmbr', then 'bootrec /fixboot', and 'bootrec /rebuildbcd'.",
                safety_level=SafetyLevel.ADVANCED,
                warning_note="BCD rebuild is an advanced repair. Backup data if drive symptoms persist.",
                verification_question="Did BCD rebuild command execute with success?"
            )
        ]
    },
    {
        "cause_id": "cause_hardware_disk_fault",
        "cause_name": "Storage Drive Hardware Fault / Physical Degradation",
        "description": "Physical disk sectors or storage drive controller hardware are experiencing read errors.",
        "symptom_weights": {
            "disk_clicking_noise": 0.60,
            "stuck_on_logo": 0.20,
            "slow_boot_time": 0.20
        },
        "min_threshold": 0.35,
        "explanation": "Unusual drive noises or read sector delays indicate physical storage drive degradation.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Immediate File Backup to External / Cloud Storage",
                instruction="If Windows boots into Safe Mode or desktop, immediately copy important personal files to external storage.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Have critical files been safely backed up?"
            ),
            FixStep(
                step_number=2,
                title="Seek Professional Hardware Diagnostics",
                instruction="If clicking noises continue or drive fails diagnostic scans, contact a qualified computer hardware repair technician.",
                safety_level=SafetyLevel.CAUTION,
                warning_note="Continued operation of a physically degraded drive may cause irreversible data loss.",
                verification_question="Have you scheduled hardware diagnostic inspection?"
            )
        ]
    }
]
