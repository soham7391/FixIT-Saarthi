from typing import Dict, List, Any
from app.schemas.diagnostic import SafetyLevel, FixStep


NETWORK_SYMPTOMS: Dict[str, Dict[str, Any]] = {
    "wifi_disabled_airplane": {
        "name": "Wi-Fi Disabled / Airplane Mode Enabled",
        "description": "Wi-Fi adapter is toggled off or Airplane mode is active",
        "type": "boolean"
    },
    "connected_no_internet": {
        "name": "Connected, No Internet Access",
        "description": "Device is connected to Wi-Fi/Ethernet but shows 'No Internet'",
        "type": "boolean"
    },
    "intermittent_disconnection": {
        "name": "Intermittent Connection Drops / Weak Signal",
        "description": "Network drops frequently or signal strength is low",
        "type": "boolean"
    },
    "dns_lookup_failure": {
        "name": "DNS Resolution Failure",
        "description": "Websites fail to load with DNS or server not found errors",
        "type": "boolean"
    },
    "vpn_proxy_enabled": {
        "name": "VPN or Proxy Active",
        "description": "VPN or proxy software is active and blocking or routing traffic",
        "type": "boolean"
    },
    "slow_network_speed": {
        "name": "Unusually Slow Connection Speed",
        "description": "High latency or extremely slow download/upload speeds",
        "type": "boolean"
    },
    "other_devices_working": {
        "name": "Other Devices Working on Same Network",
        "description": "Other phones/laptops connected to the same Wi-Fi have working internet",
        "type": "boolean"
    },
    "single_app_affected": {
        "name": "Single App or Browser Affected",
        "description": "Only one specific browser or app fails to connect while others work",
        "type": "boolean"
    }
}


NETWORK_CAUSES: List[Dict[str, Any]] = [
    {
        "cause_id": "cause_wifi_disabled",
        "cause_name": "Wi-Fi Adapter Disabled or Airplane Mode Active",
        "description": "The wireless network card is toggled off or system Airplane mode is blocking radio signals.",
        "symptom_weights": {
            "wifi_disabled_airplane": 0.70,
            "connected_no_internet": 0.15,
            "other_devices_working": 0.15
        },
        "min_threshold": 0.35,
        "explanation": "Wi-Fi radio or Airplane mode toggle is disabling wireless connectivity.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Verify Wi-Fi Toggle and Disable Airplane Mode",
                instruction="Click the Action Center in the bottom-right taskbar (or press Win + A). Ensure 'Airplane Mode' is OFF and 'Wi-Fi' is ON.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Is Wi-Fi toggled ON and showing available wireless networks?"
            ),
            FixStep(
                step_number=2,
                title="Enable Wi-Fi Network Adapter in Control Panel",
                instruction="Press Win + R, type 'ncpa.cpl', right-click 'Wi-Fi' adapter -> select 'Enable'.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Did the Wi-Fi adapter change state from Disabled to Enabled?"
            )
        ]
    },
    {
        "cause_id": "cause_connected_no_internet",
        "cause_name": "IP Address / Router Gateway Handshake Issue",
        "description": "Device is connected to the local wireless network but failed to receive a valid IP or Default Gateway from the router.",
        "symptom_weights": {
            "connected_no_internet": 0.55,
            "other_devices_working": 0.25,
            "slow_network_speed": 0.20
        },
        "min_threshold": 0.35,
        "explanation": "The local network adapter has a local connection but is not receiving internet traffic from the router gateway.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Forget and Reconnect to Wi-Fi Network",
                instruction="Open Settings -> Network & internet -> Wi-Fi -> Manage known networks. Click 'Forget' on your network, then click your Wi-Fi name and reconnect with password.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Does internet access resume after reconnecting to Wi-Fi?"
            ),
            FixStep(
                step_number=2,
                title="Release and Renew IP Address",
                instruction="Open Command Prompt as Administrator. Type 'ipconfig /release' and press Enter, then type 'ipconfig /renew' and press Enter.",
                safety_level=SafetyLevel.CAUTION,
                warning_note="This will temporarily drop your network connection for a few seconds while requesting a new IP.",
                verification_question="Did ipconfig /renew report a valid IPv4 address and restore connectivity?"
            )
        ]
    },
    {
        "cause_id": "cause_dns_resolution_issue",
        "cause_name": "DNS Resolution Failure / Stale DNS Cache",
        "description": "Domain Name System (DNS) server settings or local DNS resolver cache failed to translate web addresses into IP addresses.",
        "symptom_weights": {
            "dns_lookup_failure": 0.60,
            "connected_no_internet": 0.25,
            "other_devices_working": 0.15
        },
        "min_threshold": 0.35,
        "explanation": "Web address resolution failed due to stale local DNS cache or unreachable ISP DNS servers.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Flush Local DNS Resolver Cache",
                instruction="Open Command Prompt as Administrator. Type 'ipconfig /flushdns' and press Enter.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Did the Command Prompt report 'Successfully flushed the DNS Resolver Cache'?"
            ),
            FixStep(
                step_number=2,
                title="Configure Reliable Public DNS (Cloudflare / Google DNS)",
                instruction="Press Win + R, type 'ncpa.cpl', right-click active network adapter -> Properties -> double-click 'Internet Protocol Version 4 (TCP/IPv4)'. Select 'Use the following DNS server addresses': Primary: 1.1.1.1, Secondary: 8.8.8.8.",
                safety_level=SafetyLevel.CAUTION,
                warning_note="Custom DNS changes apply to all outgoing domain name requests on this adapter.",
                verification_question="Are websites opening normally after changing DNS servers?"
            )
        ]
    },
    {
        "cause_id": "cause_intermittent_wifi_signal",
        "cause_name": "Weak Wireless Signal or Channel Interference",
        "description": "Physical distance, wall obstructions, or 2.4GHz channel congestion cause packet loss and drops.",
        "symptom_weights": {
            "intermittent_disconnection": 0.55,
            "slow_network_speed": 0.30,
            "other_devices_working": 0.15
        },
        "min_threshold": 0.30,
        "explanation": "Weak Wi-Fi signal strength or frequency channel interference is causing periodic connection drops.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Move Closer to Wi-Fi Router or Connect 5GHz Band",
                instruction="Move computer closer to the wireless router. If available, switch from 2.4GHz to the 5GHz Wi-Fi network band for higher stability.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Does Wi-Fi connection remain stable when closer to the router?"
            ),
            FixStep(
                step_number=2,
                title="Restart Wireless Router (Power Cycle)",
                instruction="Unplug router power cable, wait 30 seconds, and plug back in. Allow 2 minutes for router to initialize.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Did restarting the router stabilize your wireless connection?"
            )
        ]
    },
    {
        "cause_id": "cause_vpn_proxy_interference",
        "cause_name": "Active VPN or Proxy Configuration Blocking Traffic",
        "description": "A Virtual Private Network (VPN) tunnel or proxy server setting is dropping packets or misrouting traffic.",
        "symptom_weights": {
            "vpn_proxy_enabled": 0.60,
            "dns_lookup_failure": 0.20,
            "connected_no_internet": 0.20
        },
        "min_threshold": 0.35,
        "explanation": "Active VPN software or manual proxy settings are intercepting and blocking network traffic.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Disconnect Active VPN Client",
                instruction="Open your VPN application (NordVPN, ExpressVPN, Cisco AnyConnect, etc.) and click 'Disconnect'.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Does internet access resume after disconnecting the VPN?"
            ),
            FixStep(
                step_number=2,
                title="Disable Windows Proxy Settings",
                instruction="Open Settings -> Network & internet -> Proxy. Ensure 'Use a proxy server' is toggled OFF.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Is the Windows proxy setting set to Disabled?"
            )
        ]
    },
    {
        "cause_id": "cause_single_app_firewall",
        "cause_name": "Application-Specific Connection / Firewall Block",
        "description": "Windows Defender Firewall or browser settings are blocking internet access for a specific program.",
        "symptom_weights": {
            "single_app_affected": 0.65,
            "other_devices_working": 0.20,
            "slow_network_speed": 0.15
        },
        "min_threshold": 0.35,
        "explanation": "Internet connection is working system-wide, but a firewall rule or browser extension is blocking one application.",
        "fix_steps": [
            FixStep(
                step_number=1,
                title="Allow Application Through Windows Defender Firewall",
                instruction="Open Control Panel -> Windows Defender Firewall -> 'Allow an app or feature through Windows Defender Firewall'. Ensure your application has 'Private' and 'Public' checkboxes checked.",
                safety_level=SafetyLevel.CAUTION,
                warning_note="Only allow trusted applications through Windows Defender Firewall.",
                verification_question="Does the application connect after enabling firewall access?"
            ),
            FixStep(
                step_number=2,
                title="Test Application in Browser Incognito / Clean Profile",
                instruction="Open browser in Incognito/Private Mode (Ctrl + Shift + N) to test if extensions/cookies are blocking connections.",
                safety_level=SafetyLevel.SAFE,
                verification_question="Does the website load in Incognito mode?"
            )
        ]
    }
]
