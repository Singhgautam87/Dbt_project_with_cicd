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
    
    # Create soda scan results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS soda_scan_results (
            id SERIAL PRIMARY KEY,
            scan_id VARCHAR(255),
            table_name VARCHAR(255),
            check_name VARCHAR(255),
            check_status VARCHAR(50),
            check_value VARCHAR(500),
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
    print("Validation tables created successfully")

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
    """Save Soda scan results to database"""
    cursor = conn.cursor()
    
    # Run soda scan and capture results
    try:
        result = subprocess.run([
            'soda', 'scan', '-d', 'postgres', '-c', 'configuration.yml', 
            'checks/checks.yml', '--output', 'json'
        ], cwd='/home/ubuntu/dbt_project_2/soda_project', 
           capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            # Parse JSON output
            output_lines = result.stdout.strip().split('\n')
            for line in output_lines:
                if line.startswith('{'):
                    try:
                        scan_data = json.loads(line)
                        
                        # Extract scan results
                        for check in scan_data.get('checks', []):
                            cursor.execute("""
                                INSERT INTO soda_scan_results 
                                (scan_id, table_name, check_name, check_status, check_value)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (
                                scan_data.get('scan_id', 'unknown'),
                                check.get('table', 'unknown'),
                                check.get('name', 'unknown'),
                                check.get('outcome', 'unknown'),
                                str(check.get('value', ''))
                            ))
                        
                        conn.commit()
                        print(f"Saved Soda scan results")
                        break
                    except json.JSONDecodeError:
                        continue
        
    except Exception as e:
        print(f"Error running soda scan: {e}")

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
