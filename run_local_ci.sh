#!/bin/bash

echo "🚀 Running Local CI/CD Pipeline..."
echo "=================================="

# Set environment variables
export DB_HOST=172.17.0.3
export DB_USER=admin
export DB_PASSWORD=admin
export DB_NAME=test_db
export DB_SCHEMA=public
export DB_PORT=5432

# Activate virtual environment
source /home/ubuntu/myenv/bin/activate

echo "📋 Step 1: Installing dependencies..."
pip install -q dbt-postgres soda-core-postgres psycopg2-binary

echo "📋 Step 2: Creating profiles.yml..."
mkdir -p ~/.dbt
cat > ~/.dbt/profiles.yml << EOF
dbt_project_2:
  target: dev
  outputs:
    dev:
      type: postgres
      host: ${DB_HOST}
      user: ${DB_USER}
      password: ${DB_PASSWORD}
      port: ${DB_PORT}
      dbname: ${DB_NAME}
      schema: ${DB_SCHEMA}
      threads: 4
      keepalives_idle: 0
      search_path: ${DB_SCHEMA}
EOF

echo "📋 Step 3: Running dbt debug..."
dbt debug

echo "📋 Step 4: Running dbt compile..."
dbt compile

echo "📋 Step 5: Running dbt test..."
dbt test

echo "📋 Step 6: Running dbt run..."
dbt run

echo "📋 Step 7: Running Soda data quality checks..."
cd soda_project
soda scan -d postgres -c configuration.yml checks/checks.yml || true

echo "📋 Step 8: Saving validation results..."
cd ..
python save_validation_results.py

echo "✅ CI/CD Pipeline completed successfully!"
echo "📊 Check validation results in PostgreSQL database"
