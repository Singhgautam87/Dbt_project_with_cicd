<<<<<<< HEAD
# Dbt_project_with_cicd
=======
# dbt Project 2 - Data Pipeline with Soda Data Quality

This project implements a complete data pipeline using dbt (data build tool) with Soda data quality validation, PostgreSQL storage, and CI/CD automation.

## Project Structure

```
dbt_project_2/
├── models/
│   ├── steging/           # Staging models
│   │   ├── stg_customers.sql
│   │   └── stg_transactions.sql
│   ├── marts/             # Mart models
│   │   ├── dim_customers.sql
│   │   ├── fact_transactions.sql
│   │   └── schema.yml
│   └── sources.yml        # Source definitions
├── soda_project/          # Data quality checks
│   ├── configuration.yml  # Database connection
│   └── checks/
│       └── checks.yml     # Quality checks
├── macros/                # Custom macros
├── snapshots/             # Data snapshots
├── tests/                 # Custom tests
├── .github/workflows/     # CI/CD pipeline
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Multi-service setup
├── requirements.txt      # Python dependencies
├── init.sql             # Database initialization
└── save_validation_results.py # Results storage script
```

## Features

### Data Pipeline
- **Staging Layer**: Raw data cleaning and standardization
- **Mart Layer**: Business-ready dimensional models
- **Incremental Processing**: Efficient data loading for transactions
- **Data Quality**: Comprehensive validation with Soda

### Data Quality Checks
- Row count validation
- Missing value detection
- Duplicate identification
- Data freshness monitoring
- Invalid value detection

### CI/CD Pipeline
- Automated testing on pull requests
- Production deployment on main branch
- Docker containerization
- Validation result storage

## Setup Instructions

### Prerequisites
- Python 3.12+
- PostgreSQL 15+
- Docker (optional)
- Git

### Local Development

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd dbt_project_2
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure database connection**:
   ```bash
   mkdir -p ~/.dbt
   cp profiles.yml.template ~/.dbt/profiles.yml
   # Edit profiles.yml with your database credentials
   ```

3. **Initialize database**:
   ```sql
   -- Run init.sql in your PostgreSQL database
   ```

4. **Run the pipeline**:
   ```bash
   # Test connection
   dbt debug
   
   # Compile models
   dbt compile
   
   # Run data quality tests
   dbt test
   
   # Execute models
   dbt run
   
   # Run Soda data quality checks
   cd soda_project
   soda scan -d postgres -c configuration.yml checks/checks.yml
   
   # Save validation results
   cd ..
   python save_validation_results.py
   ```

### Docker Deployment

1. **Using Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Manual Docker build**:
   ```bash
   docker build -t dbt-pipeline .
   docker run -e DB_HOST=localhost -e DB_USER=admin -e DB_PASSWORD=admin dbt-pipeline
   ```

### CI/CD Pipeline

The GitHub Actions workflow automatically:
- Runs on every push and pull request
- Executes dbt tests and compilation
- Performs data quality validation
- Deploys to production on main branch
- Saves validation results to database

## Data Models

### Staging Models
- `stg_customers`: Cleaned customer data with standardized fields
- `stg_transactions`: Processed transaction data with validation

### Mart Models
- `dim_customers`: Customer dimension table with deduplication
- `fact_transactions`: Transaction fact table with incremental loading

## Data Quality Validation

### Soda Checks
- **Row Count**: Ensures tables have data
- **Missing Values**: Validates required fields are populated
- **Duplicates**: Checks for duplicate keys
- **Data Freshness**: Monitors data recency
- **Invalid Values**: Validates against expected value sets

### Validation Storage
Results are automatically saved to PostgreSQL tables:
- `dbt_run_results`: dbt execution results
- `soda_scan_results`: Data quality check results
- `validation_summary`: Aggregated validation metrics

## Monitoring

### Database Tables
Monitor validation results:
```sql
-- View latest validation summary
SELECT * FROM validation_summary 
ORDER BY validation_timestamp DESC;

-- Check data quality results
SELECT * FROM soda_scan_results 
WHERE scan_timestamp >= CURRENT_DATE
ORDER BY scan_timestamp DESC;
```

### Logs
- dbt logs: `logs/`
- Soda logs: Console output
- Docker logs: `docker-compose logs`

## Troubleshooting

### Common Issues

1. **Database Connection**:
   - Verify PostgreSQL is running
   - Check connection parameters in profiles.yml
   - Ensure database and schema exist

2. **dbt Errors**:
   - Run `dbt debug` to check configuration
   - Check model syntax with `dbt compile`
   - Review logs in `logs/` directory

3. **Soda Issues**:
   - Verify configuration.yml database settings
   - Check check syntax in checks.yml
   - Review Soda documentation for metric support

4. **Docker Issues**:
   - Ensure Docker and Docker Compose are installed
   - Check port conflicts (5432 for PostgreSQL)
   - Review container logs

## Contributing

1. Create feature branch from `develop`
2. Make changes and test locally
3. Create pull request to `main`
4. CI/CD pipeline will validate changes
5. Merge after approval and successful tests

## License

This project is licensed under the MIT License.
>>>>>>> 5952d8e (Initial commit: Complete dbt project with CI/CD setup)
