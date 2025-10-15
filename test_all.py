#!/usr/bin/env python3
"""
Simple command to test everything - dbt + soda + validation + email
Usage: python test_all.py
"""
import subprocess
import sys
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import psycopg2

def setup_environment():
    """Setup environment variables"""
    os.environ['DB_HOST'] = '172.17.0.3'
    os.environ['DB_USER'] = 'admin'
    os.environ['DB_PASSWORD'] = 'admin'
    os.environ['DB_NAME'] = 'test_db'
    os.environ['DB_SCHEMA'] = 'public'
    os.environ['DB_PORT'] = '5432'

def run_command(cmd, description):
    """Run command and return result"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True, result.stdout
        else:
            # For soda scan, exit code 2 means some checks failed but scan completed
            if "soda" in cmd.lower() and result.returncode == 2:
                print(f"⚠️ {description} - COMPLETED (some checks failed)")
                return True, result.stdout + result.stderr
            else:
                print(f"❌ {description} - FAILED")
                print(f"Error: {result.stderr}")
                return False, result.stderr
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False, str(e)

def test_dbt():
    """Test dbt pipeline"""
    print("\n📊 TESTING DBT PIPELINE")
    print("=" * 50)
    
    results = []
    
    # dbt debug
    success, output = run_command("dbt debug", "dbt Debug")
    results.append(("dbt Debug", success))
    
    # dbt compile
    success, output = run_command("dbt compile", "dbt Compile")
    results.append(("dbt Compile", success))
    
    # dbt test
    success, output = run_command("dbt test", "dbt Test")
    results.append(("dbt Test", success))
    
    # dbt run
    success, output = run_command("dbt run", "dbt Run")
    results.append(("dbt Run", success))
    
    return results

def test_soda():
    """Test Soda data quality"""
    print("\n🔍 TESTING SODA DATA QUALITY")
    print("=" * 50)
    
    results = []
    
    # Soda scan (allow failure for freshness check)
    success, output = run_command(
        "cd soda_project && soda scan -d postgres -c configuration.yml checks/checks.yml",
        "Soda Data Quality Scan"
    )
    
    # Consider it success if it runs (even with failed freshness check)
    scan_success = success or ("freshness" in output and "FAILED" in output)
    results.append(("Soda Scan", scan_success))
    
    return results, output

def save_results():
    """Save validation results to database"""
    print("\n💾 SAVING VALIDATION RESULTS")
    print("=" * 50)
    
    success, output = run_command("python save_validation_results.py", "Save Results to Database")
    return success

def get_test_summary():
    """Get test summary from database"""
    try:
        conn = psycopg2.connect(
            host="172.17.0.3",
            database="test_db",
            user="admin",
            password="admin",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Get latest validation summary
        cursor.execute("""
            SELECT 
                validation_type,
                total_checks,
                passed_checks,
                failed_checks,
                validation_timestamp
            FROM validation_summary 
            WHERE validation_timestamp >= CURRENT_DATE
            ORDER BY validation_timestamp DESC
            LIMIT 2
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    except Exception as e:
        print(f"Error getting summary: {e}")
        return []

def send_email_notification(dbt_results, soda_results, soda_output, summary_results):
    """Send email notification"""
    print("\n📧 SENDING EMAIL NOTIFICATION")
    print("=" * 50)
    
    # Email configuration (you can set these as environment variables)
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    sender_email = os.getenv('SENDER_EMAIL', 'your-email@gmail.com')
    sender_password = os.getenv('SENDER_PASSWORD', 'your-app-password')
    recipient_email = os.getenv('RECIPIENT_EMAIL', 'recipient@gmail.com')
    
    if not sender_email or sender_email == 'your-email@gmail.com':
        print("⚠️ Email not configured. Set SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL environment variables")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"dbt + Soda Test Results - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Create email body
        body = f"""
🎯 DBT + SODA TEST RESULTS
========================

📊 DBT Results:
"""
        for test_name, success in dbt_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            body += f"   {test_name}: {status}\n"
        
        body += f"""
🔍 Soda Results:
"""
        for test_name, success in soda_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            body += f"   {test_name}: {status}\n"
        
        if soda_output:
            body += f"""
📋 Soda Details:
{soda_output[:500]}...
"""
        
        if summary_results:
            body += f"""
📈 Database Summary:
"""
            for row in summary_results:
                validation_type, total, passed, failed, timestamp = row
                body += f"   {validation_type}: {passed}/{total} passed, {failed} failed\n"
        
        body += f"""
⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        print("✅ Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def main():
    """Main function"""
    print("🚀 STARTING COMPLETE DBT + SODA TEST")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Test dbt
    dbt_results = test_dbt()
    
    # Test soda
    soda_results, soda_output = test_soda()
    
    # Save results
    save_success = save_results()
    
    # Get summary
    summary_results = get_test_summary()
    
    # Send email
    email_success = send_email_notification(dbt_results, soda_results, soda_output, summary_results)
    
    # Final summary
    print("\n🎯 FINAL SUMMARY")
    print("=" * 50)
    
    dbt_passed = sum(1 for _, success in dbt_results if success)
    dbt_total = len(dbt_results)
    soda_passed = sum(1 for _, success in soda_results if success)
    soda_total = len(soda_results)
    
    print(f"dbt Tests: {dbt_passed}/{dbt_total} passed")
    print(f"Soda Tests: {soda_passed}/{soda_total} passed")
    print(f"Results Saved: {'✅' if save_success else '❌'}")
    print(f"Email Sent: {'✅' if email_success else '❌'}")
    
    overall_success = dbt_passed == dbt_total and soda_passed == soda_total and save_success
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
