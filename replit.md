# OSS Funding - Open Source Grant Registry

## Overview

This repository maintains a curated registry of grants and funding data for open source software projects. It serves as a comprehensive database that tracks funding flows across the OSS ecosystem, providing researchers, developers, foundations, and other stakeholders with structured access to funding information. The system implements the DAOIP-5 metadata standard for grants management and provides data in multiple formats (CSV, JSON, and through Google Sheets integration).

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Data Storage and Schema
The repository uses a file-based data storage approach with standardized CSV inputs that are transformed into JSON outputs. The core schema includes fields for project identification, funding amounts, dates, funder information, grant pool names, and extensible metadata. All funding data conforms to the DAOIP-5 standard developed by DAOstar/Metagov, ensuring interoperability across different grants management systems.

### Data Processing Pipeline
The system employs Python-based data processing scripts that handle CSV ingestion, data validation, and format conversion. Key processing includes data cleaning, schema standardization, and multi-format output generation. The pipeline supports both individual funder data processing and bulk operations across all grant systems.

### DAOIP-5 Implementation
The architecture implements a comprehensive DAOIP-5 grants management system with four main components: grant systems (top-level organizations), grant pools (funding rounds), projects (recipients), and applications (individual funding requests). Each component supports an extensions field for implementation-specific metadata while maintaining core schema compliance.

### Funder Management System
Funders are organized in a hierarchical directory structure where each funder has its own directory containing YAML configuration files and CSV upload folders. This design enables distributed data management while maintaining centralized schema consistency. Each funder profile includes metadata about the organization and references to their grant pools.

### Data Quality and Validation
The system includes comprehensive data quality validation scripts that check schema compliance, date format consistency, URL validation, and data completeness. Quality scoring mechanisms help identify and prioritize data issues across different grant systems. Critical issue fixes handle common data problems like date format standardization and schema field mapping.

### Output Format Support
The architecture supports multiple output formats including structured JSON files conforming to DAOIP-5, CSV exports for analysis tools, and integration with Google Sheets for collaborative access. The JSON outputs are organized by grant system with separate files for grant pools and applications to optimize for different access patterns.

## External Dependencies

- **Python Libraries**: pandas for data manipulation, PyYAML for configuration parsing, requests for API validation
- **DAOIP-5 Standard**: Implements DAOstar metadata standard for grants management interoperability
- **Google Sheets API**: Integration for collaborative data access and sharing
- **OSS Directory**: References the companion oss-directory repository for project naming conventions and standardization
- **GitHub Pages/Raw Content**: Hosts JSON files via GitHub's raw content delivery for API access
- **External Validation APIs**: Uses Open Source Observer API for project validation and verification