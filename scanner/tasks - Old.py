# scanner/tasks.py

from .models import ScanResult
from reports.models import ComplianceReport 
from django.utils import timezone
import time
import random

from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@shared_task(bind=True)
def run_compliance_scan(self, scan_id):
    scan = ScanResult.objects.get(id=scan_id)
    scan.status = 'running'
    scan.scan_log += "\n[START] Compliance scan initiated..."
    scan.save(update_fields=['status', 'scan_log'])

    steps = [
        ("Initializing scanner", 1),
        ("Connecting to scanner", 2),
        ("Authenticating credentials", 3),
        ("Fetching domain info", 5),
        ("Crawling domain and sitemap", 15),
        ("Checking DNS records", 20),
        ("Analyzing cookies & consent banners", 25),
        ("Scanning privacy policy for GDPR/CCPA", 45),
        ("Testing TLS/SSL configuration", 65),
        ("Analyzing email security", 70),
        ("Checking data collection forms", 75),
        ("Evaluating third-party scripts", 85),
        ("Generating compliance report", 90),
        ("Generating risk report", 95),
        ("Finalizing results", 100),
                
    ]

    findings = []
    breach_alerts = []
    checklist = {}

    for i, (step, progress) in enumerate(steps):
        time.sleep(1.8)  # Simulate work

        # Simulate findings
        if random.random() > 0.7:
            findings.append(f"Non-compliant {step.lower()}")
        if random.random() > 0.9:
            breach_alerts.append(f"High-risk in {step}")

        scan.scan_log += f"\n[{progress}%] {step}"
        scan.progress = progress
        scan.save(update_fields=['scan_log', 'progress'])

    # Finalize
    scan.status = 'complete'
    scan.grade = random.choice(['A', 'B', 'C', 'D'])[0]
    scan.risk_score = round(random.uniform(5.0, 45.0), 1)
    scan.anomaly_score = round(random.uniform(0.0, 10.0), 1)

    scan.raw_data = {
        'findings': findings,
        'recommendations': [
            "Implement cookie consent banner",
            "Update privacy policy with CCPA clause",
            "Enable HSTS headers"
        ],
        'scanned_urls': 47,
        'issues_found': len(findings)
    }

    scan.breach_alerts = breach_alerts
    scan.checklist_status = {
        'gdpr': scan.grade in ['A', 'B'],
        'ccpa': scan.grade in ['A', 'B', 'C'],
        'https': True,
        'cookie_banner': len(findings) == 0
    }

    scan.scan_log += f"\n[COMPLETE] Grade: {scan.grade}, Risk: {scan.risk_score}"
    scan.save()
    
    
    
# scanner/tasks.py
@shared_task(bind=True)
def run_compliance_scan(self, scan_id):
    scan = ScanResult.objects.get(id=scan_id)
    scan.status = 'running'
    scan.progress = 0
    scan.scan_log = "Scan initiated..."
    scan.save(update_fields=['status', 'progress', 'scan_log'])
    

    # ... your steps ...
    scan.progress = progress
    scan.scan_log += f"\n[{progress}%] {step}"
    scan.save(update_fields=['progress', 'scan_log'])

    # Final
    scan.status = 'complete'
    scan.grade = 'A'
    scan.risk_score = 12.4
    scan.progress = 100
    scan.save()
    
    scan.recommendations = [
        {"title": "Implement Cookie Consent", "description": "Add GDPR-compliant banner", "priority": "high"},
        {"title": "Enable HSTS", "description": "Add Strict-Transport-Security header", "priority": "medium"}
    ]
    scan.save()
    
    
    # CREATE REPORT
    ComplianceReport.objects.get_or_create(
        scan=scan,
        defaults={'generated_at': timezone.now()}
    )
    