# DAOIP-5 Scripts Documentation

This directory contains scripts for data validation, quality assurance, and critical issue fixes for the DAOIP-5 grant funding dataset.

## Scripts Overview

### 1. Data Quality Validation

#### `validate_data_quality.py`
Validates individual grant systems against DAOIP-5 schema standards.

**Usage:**
```bash
cd daoip-5/scripts
python validate_data_quality.py ../json/arbitrumfoundation
```

**Features:**
- Schema consistency validation
- Date format checking (ISO8601 compliance)
- URL validation
- Placeholder value detection
- Data type validation
- Quality scoring (0-100)

#### `validate_all_systems.py`
Comprehensive validation of all grant systems with aggregated reporting.

**Usage:**
```bash
cd daoip-5/scripts
python validate_all_systems.py
```

**Features:**
- Validates all grant systems automatically
- Generates comprehensive quality report
- Aggregates statistics across all systems
- Categorizes systems by quality score
- Identifies global patterns and issues

### 2. Critical Issue Fixes

#### `fix_critical_issues.py`
Implements Phase 1 critical fixes as identified in the field mapping analysis.

**Usage:**
```bash
# Fix single grant system
python fix_critical_issues.py ../json/arbitrumfoundation

# Fix all grant systems
python fix_critical_issues.py ../json all
```

**Fixes Applied:**
1. **Schema Standardization:** `grant_pools` → `grantPools`
2. **Date Format Fixes:** Convert all dates to ISO8601 format
3. **Unknown Value Fixes:** Convert "Unknown" strings to `null`

**Safety Features:**
- Creates `.backup` files before making changes
- Only modifies files that need fixes
- Detailed reporting of changes made

### 3. Data Conversion

#### `CSV-to-JSON.py`
Converts CSV grant data to DAOIP-5 compliant JSON format.

**Usage:**
```bash
python CSV-to-JSON.py --path /path/to/grant/system/folder
```

## Field Mapping Configuration

Each grant system includes a `field_mapping.yaml` file that documents:

- **Schema fixes needed:** Field naming inconsistencies
- **Data quality standards:** Expected formats and types
- **Known issues:** Critical and data quality problems
- **Validation rules:** Field-specific validation requirements

### Example Field Mapping Structure:
```yaml
system_name: "Grant System Name"
system_type: "Foundation|Entity"

schema_fixes:
  root_level:
    - from: "grant_pools"
      to: "grantPools"
      status: "needs_fix"

data_quality:
  date_format: "ISO8601"
  required_fields: ["projectName", "projectId", "grantPoolId"]

validation:
  date_fields: ["createdAt", "closeDate"]
  url_fields: ["projectsURI", "contentURI"]
  no_placeholder_values: ["Unknown", "not available"]
```

## API Documentation

The DAOIP-5 API provides access to validated grant data:

### Key Endpoints:
- `GET /` - List all grant systems
- `GET /<grant_system>` - List grant pools in system
- `GET /<grant_system>/<filename>.json` - Get specific grant data
- `GET /search/<project_name>` - Search across all systems
- `GET /help` - API documentation

### Running the API:
```bash
cd daoip-5/scripts/API
python run.py
```

## Data Quality Reports

### Individual System Reports
Generated in each grant system folder as `data_quality_report.json`:

```json
{
  "system_name": "arbitrumfoundation",
  "quality_score": 95,
  "statistics": {
    "total_applications": 50,
    "valid_applications": 48,
    "files_processed": 2
  },
  "issues": {
    "critical": [],
    "schema": ["Uses 'grant_pools' instead of 'grantPools'"],
    "data_quality": ["Some projectId values are 'unknown-project'"]
  }
}
```

### Comprehensive Report
Generated at `daoip-5/json/comprehensive_data_quality_report.json`:

- Aggregated statistics across all systems
- Quality categorization (excellent/good/fair/poor)
- Global issue patterns
- System-by-system validation results

## Workflow Recommendations

### 1. Initial Setup
```bash
# Navigate to scripts directory
cd daoip-5/scripts

# Install requirements
pip install -r requirements.txt
```

### 2. Data Quality Assessment
```bash
# Run comprehensive validation
python validate_all_systems.py

# Review comprehensive report
cat ../json/comprehensive_data_quality_report.json
```

### 3. Apply Critical Fixes
```bash
# Fix all systems
python fix_critical_issues.py ../json all

# Re-validate after fixes
python validate_all_systems.py
```

### 4. Individual System Work
```bash
# Validate specific system
python validate_data_quality.py ../json/optimism

# Review field mapping
cat ../json/optimism/field_mapping.yaml

# Review quality report
cat ../json/optimism/data_quality_report.json
```

## Quality Standards

### Excellent (90-100 points)
- All schema standards met
- No critical issues
- Minimal placeholder values
- Consistent data types

### Good (70-89 points)
- Minor schema inconsistencies
- Few data quality issues
- Mostly complete data

### Fair (50-69 points)
- Some schema problems
- Moderate data quality issues
- Some missing information

### Poor (<50 points)
- Major schema inconsistencies
- Significant data quality problems
- Extensive use of placeholder values

## Contributing

When adding new grant systems:

1. Create field mapping YAML file
2. Run validation scripts
3. Apply critical fixes if needed
4. Ensure quality score >70
5. Update API documentation if needed

## Support

For issues or questions:
- Check individual system quality reports
- Review field mapping configurations
- Run validation scripts for detailed diagnostics
- Consult the comprehensive quality report for global patterns

This analysis reveals that while the overall structure is consistent, there are significant data quality and naming consistency issues that should be addressed to improve API reliability and client integration.

## GitHub Actions Integration

The repository includes automated workflows for processing new funders:

### Automatic Processing
- **Trigger**: Any push/PR that modifies files in `data/funders/`
- **Actions**:
  1. Detects changed funder directories
  2. Validates directory structure (YAML + uploads/CSV files)
  3. Converts CSV to DAOIP-5 JSON format
  4. Runs data quality validation
  5. Applies critical fixes automatically
  6. Creates PR with generated files and reports

### Manual Workflow Dispatch
You can also trigger the workflow manually from the GitHub Actions tab.

### Workflow Files
- `.github/workflows/daoip5-update.yaml` - Main automation workflow

The workflow ensures all new funders are properly validated and converted to the DAOIP-5 standard before integration.