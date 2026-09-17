from typing import Dict, List, Any
from app.schemas.diagnostic import SafetyLevel, FixStep


PERFORMANCE_SYMPTOMS: Dict[str, Dict[str, Any]] = {
    "high_cpu_usage": {
        "name": "High CPU Usage",
        "description": "Processor utilization exceeds 80%",
        "type": "boolean"
    },
    "high_ram_usage": {
        "name": "High RAM Usage",
        "description": "Memory usage exceeds 80%",
        "type": "boolean"
    },
    "high_disk_usage": {
        "name": "High Disk Usage",
        "description": "Disk active time is stuck at 90-100%",
        "type": "boolean"
    },
    "general_slowdown": {
        "name": "General System Slowdown",
        "description": "Overall OS responsiveness is sluggish",
        "type": "boolean"
    },
    "app_freezing": {
        "name": "Application Freezing",
        "description": "Applications freeze or show 'Not Responding'",
        "type": "boolean"
    },
    "top_process_name": {
        "name": "Top Process Name",
        "description": "Name of the process consuming highest resources",
        "type": "string"
    }
}


PERFORMANCE_CAUSES: List[Dict[str, Any]] = [
    {
        "cause_id": "cause_ram_exhaustion",
        "cause_name": "RAM Exhaustion / Memory Leak",
        "description": "Available RAM is depleted, forcing Windows to use virtual memory paging, causing system freezes.",
        "symptom_weights": {
            "high_ram_usage": 0.50,
            "app_freezing": 0.25,
            "general_slowdown": 0.25
        },
        "min_threshold": 0.35,
        "explanation": "High RAM usage ({ram_pct}) was detected. When physical memory fills up, memory swapping causes freeze spikes.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Close High-Memory Applications",
                instruction="Open Task Manager (Ctrl + Shift + Esc), sort by Memory column, and close memory-heavy non-essential applications.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Did closing heavy applications lower memory usage and stop freezing?"
            ),
            FixStep(
                step_number=2,
                title="Terminate Rogue Memory Leak Process",
                instruction="In Task Manager, locate any single process consuming excessive RAM (e.g. {top_process}). Right-click and select 'End Task'.",
                safety_level=SafetyLevel.CAUTION,
                warning_note="Ending unknown background tasks may cause unsaved application data to be lost.",
                verification_question="Has memory usage dropped to normal levels?"
            ),
            FixStep(
                step_number=3,
                title="Configure Virtual Memory Paging",
                instruction="Open System Properties -> Performance Settings -> Advanced tab -> Virtual Memory. Ensure 'Automatically manage paging file size for all drives' is enabled.",
                safety_level=SafetyLevel.ADVANCED,
                warning_note="Modifying virtual memory incorrectly may affect system stability.",
                verification_question="Is Virtual Memory set to automatically managed?"
            )
        ]
    },
    {
        "cause_id": "cause_cpu_bottleneck",
        "cause_name": "High CPU Bottleneck / Rogue Process",
        "description": "Processor capacity is maxed out by an intensive application, background task, or runaway process.",
        "symptom_weights": {
            "high_cpu_usage": 0.55,
            "general_slowdown": 0.25,
            "app_freezing": 0.20
        },
        "min_threshold": 0.35,
        "explanation": "CPU utilization is maxed out ({cpu_pct}). A specific process ({top_process}) is saturating processor cores.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Identify and End High CPU Process",
                instruction="Open Task Manager (Ctrl + Shift + Esc), click CPU column header. Select the process consuming high CPU ({top_process}) and click 'End Task'.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Did CPU usage drop below 30% after ending the process?"
            ),
            FixStep(
                step_number=2,
                title="Inspect Background Scans & Updates",
                instruction="Check if Windows Update or antivirus background scanning is active. Allow the scan/update to finish or schedule it during idle hours.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Is an antivirus scan or system update currently active?"
            )
        ]
    },
    {
        "cause_id": "cause_disk_saturation",
        "cause_name": "Disk I/O Saturation / HDD Bottleneck",
        "description": "Hard drive active time is pinned at 100%, bottlenecking read/write operations.",
        "symptom_weights": {
            "high_disk_usage": 0.60,
            "general_slowdown": 0.25,
            "app_freezing": 0.15
        },
        "min_threshold": 0.35,
        "explanation": "Disk active time is stuck at 100%. Storage read/write queues are bottlenecking overall system responsiveness.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Disable SysMain Service",
                instruction="Press Win + R, type 'services.msc', locate 'SysMain', right-click -> Properties, set Startup type to 'Disabled' and click 'Stop'.",
                safety_level=SafetyLevel.CAUTION,
                warning_note="Disabling SysMain may slightly increase initial application launch times on mechanical HDDs.",
                verification_question="Did Disk usage drop from 100% in Task Manager?"
            ),
            FixStep(
                step_number=2,
                title="Clear Temporary Files",
                instruction="Open Settings -> System -> Storage -> Storage Sense. Run temporary file cleanup.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Did temporary file cleanup complete successfully?"
            ),
            FixStep(
                step_number=3,
                title="Run Disk Check Scan",
                instruction="Open Command Prompt as Administrator, type 'chkdsk C: /f /r' and press Enter to schedule a disk repair scan on reboot.",
                safety_level=SafetyLevel.ADVANCED,
                warning_note="Disk check will run on next system reboot and can take 30-60 minutes.",
                verification_question="Have you scheduled the disk check scan?"
            )
        ]
    },
    {
        "cause_id": "cause_thermal_power",
        "cause_name": "Thermal Throttling / Power Plan Constraint",
        "description": "CPU frequency is throttled due to high operating temperature or power saving plan limits.",
        "symptom_weights": {
            "high_cpu_usage": 0.35,
            "general_slowdown": 0.45,
            "app_freezing": 0.20
        },
        "min_threshold": 0.30,
        "explanation": "Processor clock speed is throttled, leading to system-wide lag despite moderate task loads.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Switch Power Plan to Balanced/Performance",
                instruction="Open Control Panel -> Power Options. Select 'Balanced' or 'High Performance' power plan.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Is the power plan set to Balanced or High Performance?"
            ),
            FixStep(
                step_number=2,
                title="Clean Air Vents & Ensure Ventilation",
                instruction="Ensure laptop or PC cooling vents are unobstructed. Clear dust from fans using compressed air.",
                safety_level=SafetyLevel.CAUTION,
                warning_note="Turn off power before using compressed air near cooling fans.",
                verification_question="Are cooling fans operating clearly without high thermal throttling?"
            )
        ]
    },
    {
        "cause_id": "cause_startup_overload",
        "cause_name": "Background Service / Startup Overload",
        "description": "Too many autostart utilities and background services competing for system startup headroom.",
        "symptom_weights": {
            "general_slowdown": 0.50,
            "high_ram_usage": 0.25,
            "high_cpu_usage": 0.25
        },
        "min_threshold": 0.30,
        "explanation": "Multiple background programs launching at startup consume CPU and memory headroom concurrently.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Disable Unnecessary Startup Programs",
                instruction="Open Task Manager (Ctrl + Shift + Esc) -> Startup apps tab. Right-click non-essential programs and select 'Disable'.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Have non-essential startup apps been disabled?"
            ),
            FixStep(
                step_number=2,
                title="Perform Clean Boot Isolation",
                instruction="Press Win + R, type 'msconfig' -> Services tab -> Check 'Hide all Microsoft services' -> click 'Disable all'. Click Apply and reboot.",
                safety_level=SafetyLevel.CAUTION,
                warning_note="Ensure 'Hide all Microsoft services' is checked to prevent disabling core OS services.",
                verification_question="Is system performance improved after clean boot?"
            )
        ]
    }
]
