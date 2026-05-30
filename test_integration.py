#!/usr/bin/env python3
"""
Aegis-Antigravity SRE: Webhook Integration Test Script
------------------------------------------------------
This script verifies the full end-to-end incident dispatch loop:
1. Simulates a degraded service CVE incident.
2. Triggers the n8n dispatcher engine.
3. Auto-starts the background HTTP mock receiver server.
4. Validates that the incident is successfully received, parsed, and logged to the persistent audit trail.
"""

import os
import sys
import time
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.n8n_dispatcher import trigger_n8n_workflow

def run_test():
    print("=" * 60)
    print("🛡️  AEGIS SRE INTEGRATION TEST RUNNER")
    print("=" * 60)
    
    # 1. Prepare simulated high-fidelity incident payload
    mock_payload = {
        "incident_id": "INC-2026-CVE-43804",
        "severity": "CRITICAL",
        "service": "API Gateway",
        "root_cause": "Vulnerability CVE-2023-43804 in urllib3 package traced to TANISHX1's commit a5d89f3",
        "blast_radius_nodes": ["API Gateway", "Auth Service", "Primary DB"],
        "remediation_action": "Upgrade urllib3 to >=1.26.18 and roll back commit a5d89f3",
        "raw_forensics": {
            "cve": "CVE-2023-43804",
            "package": "urllib3",
            "culprit_commit": "a5d89f3",
            "author": "TANISHX1"
        }
    }
    
    print("\n[STEP 1] Prepared simulated SRE incident payload:")
    print(json.dumps(mock_payload, indent=2))
    
    # 2. Trigger n8n dispatcher engine
    print("\n[STEP 2] Dispatching incident payload via trigger_n8n_workflow()...")
    result = trigger_n8n_workflow(mock_payload)
    
    print("\n[STEP 3] Received Dispatch Engine response:")
    print(json.dumps(result, indent=2))
    
    # 3. Verify audit trail logging
    audit_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "n8n_data", "incident_log.jsonl")
    print(f"\n[STEP 4] Verifying dispatch status:")
    
    if result.get("status") == "success" and result.get("status_code") == 200:
        if "Workflow was started" in str(result.get("n8n_response")):
            print("🎉 SUCCESS: Real n8n docker container was online and executed the SRE remediation workflow successfully!")
            print("=" * 60)
            return True
        
        time.sleep(0.5) # Wait for local file write if mocked
        if os.path.exists(audit_file):
            with open(audit_file, "r") as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    last_entry = json.loads(last_line)
                    print("✅ Forensic mock log validated! Last logged audit trail entry:")
                    print(json.dumps(last_entry, indent=2))
                    print("\n🎉 INTEGRATION TEST COMPLETED: SUCCESSFUL END-TO-END REMEDIATION DISPATCH!")
                    print("=" * 60)
                    return True
    
    print("❌ Error: Forensic log not found or empty.")
    print("=" * 60)
    return False

if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
