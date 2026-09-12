MITRE_STAGES = ["Reconnaissance", "Initial Access", "Lateral Movement", "Command & Control", "Exfiltration"]
MITRE_TECHNIQUES = {
    "Reconnaissance": "T1595 Active Scanning", "Initial Access": "T1190 Exploit Public-Facing Application",
    "Lateral Movement": "T1021 Remote Services", "Command & Control": "T1071 Application Layer Protocol",
    "Exfiltration": "T1041 Exfiltration Over C2 Channel",
}
def technique_for(stage): return MITRE_TECHNIQUES.get(stage, "T0000 Unknown")
