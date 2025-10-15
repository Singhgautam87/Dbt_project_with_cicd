#!/usr/bin/env python3
"""
Script to save dbt and Soda validation results to PostgreSQL
"""
import psycopg2
import json
import subprocess
import sys
from datetime import datetime
import os

def connect_to_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host="172.17.0.3",
            database="test_db",
            user="admin",
            password="admin",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def create_validation_tables(conn):
    """Create tables to store validation results"""
    cursor = conn.cursor()
    
    # Create dbt run results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dbt_run_results (
            id SERIAL PRIMARY KEY,
            run_id VARCHAR(255),
            model_name VARCHAR(255),
            status VARCHAR(50),
            execution_time FLOAT,
            rows_affected INTEGER,
            run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create soda scan results table (enhanced structure)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS soda_scan_results (
            id SERIAL PRIMARY KEY,
            scan_id VARCHAR(255),
            scan_start_timestamp TIMESTAMP,
            scan_end_timestamp TIMESTAMP,
            table_name VARCHAR(255),
            check_name VARCHAR(255),
            check_type VARCHAR(100),
            check_status VARCHAR(50),
            check_value TEXT,
            check_diagnostics JSONB,
            check_location_file VARCHAR(500),
            check_location_line INTEGER,
            check_location_col INTEGER,
            scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create soda metrics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS soda_metrics (
            id SERIAL PRIMARY KEY,
            scan_id VARCHAR(255),
            metric_name VARCHAR(100),
            metric_value TEXT,
            table_name VARCHAR(255),
            column_name VARCHAR(255),
            scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create validation summary table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS validation_summary (
            id SERIAL PRIMARY KEY,
            validation_type VARCHAR(50),
            total_checks INTEGER,
            passed_checks INTEGER,
            failed_checks INTEGER,
            error_checks INTEGER,
            validation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    print("Enhanced validation tables created successfully")

def save_dbt_results(conn):
    """Save dbt run results to database"""
    cursor = conn.cursor()
    
    # Get dbt run results from target/run_results.json
    try:
        with open('/home/ubuntu/dbt_project_2/target/run_results.json', 'r') as f:
            results = json.load(f)
        
        run_id = results.get('metadata', {}).get('dbt_version', 'unknown')
        
        for result in results.get('results', []):
            cursor.execute("""
                INSERT INTO dbt_run_results 
                (run_id, model_name, status, execution_time, rows_affected)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                run_id,
                result.get('unique_id', 'unknown'),
                result.get('status', 'unknown'),
                result.get('execution_time', 0),
                result.get('adapter_response', {}).get('rows_affected', 0)
            ))
        
        conn.commit()
        print(f"Saved {len(results.get('results', []))} dbt run results")
        
    except FileNotFoundError:
        print("dbt run results file not found")
    except Exception as e:
        print(f"Error saving dbt results: {e}")

def save_soda_results(conn):
    """Save Soda scan results to database using structured JSON parsing"""
    cursor = conn.cursor()
    
    # Run soda scan with JSON output
    try:
        # Create temporary JSON file for scan results
        json_file = '/tmp/soda_scan_results.json'
        
        result = subprocess.run([
            'soda', 'scan', '-d', 'postgres', '-c', 'configuration.yml', 
            'checks/checks.yml', '-srf', json_file
        ], cwd='/home/ubuntu/dbt_project_2/soda_project', 
           capture_output=True, text=True, check=False)
        
        scan_id = f"soda_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Parse JSON output from file
        try:
            # Read JSON from file
            with open(json_file, 'r') as f:
                json_data = json.load(f)
                
                print(f"Parsing structured JSON output from Soda scan...")
                
                # Extract scan metadata
                scan_start_timestamp = json_data.get('scanStartTimestamp')
                scan_end_timestamp = json_data.get('scanEndTimestamp')
                
                # Save metrics
                metrics_saved = 0
                metrics = json_data.get('metrics', [])
                for metric in metrics:
                    metric_name = metric.get('metricName', '')
                    metric_value = str(metric.get('value', ''))
                    
                    # Extract table and column from identity
                    identity = metric.get('identity', '')
                    parts = identity.split('-')
                    table_name = parts[2] if len(parts) > 2 else 'unknown'
                    column_name = parts[3] if len(parts) > 3 else None
                    
                    cursor.execute("""
                        INSERT INTO soda_metrics 
                        (scan_id, metric_name, metric_value, table_name, column_name)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        scan_id,
                        metric_name,
                        metric_value,
                        table_name,
                        column_name
                    ))
                    metrics_saved += 1
                
                # Save checks with full details
                checks_saved = 0
                checks = json_data.get('checks', [])
                
                for check in checks:
                    table_name = check.get('table', 'unknown')
                    check_name = check.get('name', 'unknown')
                    check_type = check.get('type', 'generic')
                    check_status = check.get('outcome', 'unknown')
                    check_value = str(check.get('diagnostics', {}).get('value', ''))
                    
                    # Extract location information
                    location = check.get('location', {})
                    location_file = location.get('filePath', '')
                    location_line = location.get('line', 0)
                    location_col = location.get('col', 0)
                    
                    # Store diagnostics as JSONB
                    diagnostics = json.dumps(check.get('diagnostics', {}))
                    
                    # Map Soda outcomes to our status
                    status_mapping = {
                        'pass': 'PASSED',
                        'fail': 'FAILED',
                        'error': 'ERROR',
                        'warning': 'WARNING'
                    }
                    
                    mapped_status = status_mapping.get(check_status.lower(), check_status.upper())
                    
                    cursor.execute("""
                        INSERT INTO soda_scan_results 
                        (scan_id, scan_start_timestamp, scan_end_timestamp, table_name, 
                         check_name, check_type, check_status, check_value, check_diagnostics,
                         check_location_file, check_location_line, check_location_col)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        scan_id,
                        scan_start_timestamp,
                        scan_end_timestamp,
                        table_name,
                        check_name,
                        check_type,
                        mapped_status,
                        check_value,
                        diagnostics,
                        location_file,
                        location_line,
                        location_col
                    ))
                    checks_saved += 1
                    print(f"Saved check: {table_name}.{check_name} = {mapped_status}")
                
                conn.commit()
                print(f"Saved {checks_saved} checks and {metrics_saved} metrics with scan_id: {scan_id}")
                
                # Clean up JSON file
                import os
                if os.path.exists(json_file):
                    os.remove(json_file)
                return
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"JSON parsing failed: {e}")
            print("Falling back to text parsing...")
        
        # Fallback to text parsing if JSON fails
        print("Using fallback text parsing method...")
        output_lines = result.stdout.strip().split('\n')
        
        # Look for check results in the output
        current_table = None
        checks_saved = 0
        
        for line in output_lines:
            # Remove timestamp prefix like "[01:11:46] " from the beginning
            if line.startswith('[') and ']' in line:
                # Find the closing bracket
                end_bracket = line.find(']')
                if end_bracket != -1:
                    line = line[end_bracket + 1:].strip()
            
            # Skip empty lines and summary lines
            if not line or 'Scan summary:' in line or 'checks PASSED:' in line or 'checks FAILED:' in line or 'Oops!' in line:
                continue
                
            # Look for table names - pattern: "dim_customers in postgres"
            if ' in postgres' in line:
                # Extract table name before " in postgres"
                table_part = line.split(' in postgres')[0].strip()
                # Remove any leading spaces or dashes
                table_part = table_part.lstrip('- ').strip()
                if table_part:
                    current_table = table_part
                    print(f"Found table: {current_table}")
                    continue
            
            # Look for check results - pattern: "row_count > 0 [PASSED]"
            if '[PASSED]' in line or '[FAILED]' in line or '[ERROR]' in line:
                if current_table and '[' in line and ']' in line:
                    check_part = line.split('[')[0].strip()
                    status_part = line.split('[')[1].split(']')[0].strip()
                    
                    # Clean up check name - remove leading spaces/dashes
                    check_name = check_part.lstrip('- ').strip()
                    
                    if check_name and status_part in ['PASSED', 'FAILED', 'ERROR']:
                        cursor.execute("""
                            INSERT INTO soda_scan_results 
                            (scan_id, table_name, check_name, check_status, check_value)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            scan_id,
                            current_table,
                            check_name,
                            status_part,
                            ''
                        ))
                        checks_saved += 1
                        print(f"Saved check: {current_table}.{check_name} = {status_part}")
        
        conn.commit()
        print(f"Saved {checks_saved} Soda scan results with scan_id: {scan_id}")
        
    except Exception as e:
        print(f"Error running soda scan: {e}")
        import traceback
        traceback.print_exc()

def save_validation_summary(conn):
    """Save validation summary to database"""
    cursor = conn.cursor()
    
    # Get dbt summary
    cursor.execute("""
        SELECT COUNT(*) as total, 
               SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as passed,
               SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as failed,
               SUM(CASE WHEN status NOT IN ('success', 'error') THEN 1 ELSE 0 END) as other
        FROM dbt_run_results 
        WHERE run_timestamp >= CURRENT_DATE
    """)
    dbt_summary = cursor.fetchone()
    
    if dbt_summary:
        cursor.execute("""
            INSERT INTO validation_summary 
            (validation_type, total_checks, passed_checks, failed_checks, error_checks)
            VALUES (%s, %s, %s, %s, %s)
        """, ('dbt', dbt_summary[0], dbt_summary[1], dbt_summary[2], dbt_summary[3]))
    
    # Get Soda summary
    cursor.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN check_status = 'pass' THEN 1 ELSE 0 END) as passed,
               SUM(CASE WHEN check_status = 'fail' THEN 1 ELSE 0 END) as failed,
               SUM(CASE WHEN check_status = 'error' THEN 1 ELSE 0 END) as error
        FROM soda_scan_results 
        WHERE scan_timestamp >= CURRENT_DATE
    """)
    soda_summary = cursor.fetchone()
    
    if soda_summary:
        cursor.execute("""
            INSERT INTO validation_summary 
            (validation_type, total_checks, passed_checks, failed_checks, error_checks)
            VALUES (%s, %s, %s, %s, %s)
        """, ('soda', soda_summary[0], soda_summary[1], soda_summary[2], soda_summary[3]))
    
    conn.commit()
    print("Validation summary saved successfully")

def main():
    """Main function to orchestrate validation result saving"""
    print("Starting validation result saving process...")
    
    # Connect to database
    conn = connect_to_db()
    if not conn:
        print("Failed to connect to database")
        sys.exit(1)
    
    try:
        # Create tables
        create_validation_tables(conn)
        
        # Save results
        save_dbt_results(conn)
        save_soda_results(conn)
        save_validation_summary(conn)
        
        print("Validation results saved successfully!")
        
    except Exception as e:
        print(f"Error in main process: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
