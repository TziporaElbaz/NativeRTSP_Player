import subprocess
import json
from datetime import datetime

def run_trivy_scan():
    print("🔍 Running Trivy security scan...")
    
    result = subprocess.run(
        ["trivy", "fs", ".", "--format", "json", "--severity", "HIGH,CRITICAL"],
        capture_output=True,
        text=True
    )
    
    return json.loads(result.stdout)

def parse_results(scan_data):
    vulnerabilities = []
    
    for result in scan_data.get("Results", []):
        for vuln in result.get("Vulnerabilities", []):
            vulnerabilities.append({
                "package": vuln.get("PkgName"),
                "severity": vuln.get("Severity"),
                "cve": vuln.get("VulnerabilityID"),
                "description": vuln.get("Title", "No description"),
                "fix": vuln.get("FixedVersion", "No fix available")
            })
    
    return vulnerabilities

def print_report(vulnerabilities):
    print("\n" + "="*50)
    print(f"🛡️  SECURITY REPORT — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*50)
    
    if not vulnerabilities:
        print("✅ No HIGH or CRITICAL vulnerabilities found!")
        return
    
    critical = [v for v in vulnerabilities if v["severity"] == "CRITICAL"]
    high = [v for v in vulnerabilities if v["severity"] == "HIGH"]
    
    print(f"\n🔴 CRITICAL: {len(critical)}")
    print(f"🟠 HIGH: {len(high)}")
    print("\nDetails:")
    
    for v in vulnerabilities:
        print(f"\n  [{v['severity']}] {v['package']}")
        print(f"  CVE: {v['cve']}")
        print(f"  Issue: {v['description']}")
        print(f"  Fix: {v['fix']}")

if __name__ == "__main__":
    data = run_trivy_scan()
    vulns = parse_results(data)
    print_report(vulns)