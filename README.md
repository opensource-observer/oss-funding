# OSS Funding [![License: Apache 2.0][license-badge]][license]

[license]: https://opensource.org/license/apache-2-0/
[license-badge]: https://img.shields.io/badge/License-Apache2.0-blue.svg

This repository contains a curated registry of grants and other funding to open source software (OSS) projects. Data is uploaded in CSV format and transformed to a common schema.

This directory is a public good, free to use and distribute. We hope it serves the needs of researchers, developers, foundations, and other users looking to better understand the OSS ecosystem!

For adding projects (and project naming conventions), please refer to our companion repo: https://github.com/opensource-observer/oss-directory

## Latest Funding Data

The latest funding data can be found at:
- CSV: [`./data/funding_data.csv`](./data/funding_data.csv)
- JSON: [`./data/funding_data.json`](./data/funding_data.json)
- Google Sheets: [here](https://docs.google.com/spreadsheets/d/1gYwfeZUSEEiUbf2c_A0SWTG7aiy52uWiVFazNVLDaiA/edit?usp=sharing)

## Schema

Here is the current schema for indexing funding data:

- `to_project_name`: The name of the project as specified in OSS Directory. See [here](https://github.com/opensource-observer/oss-directory) for more info. Leave blank if the project is not yet in OSS Directory.
- `amount`: The amount of funding in USD equivalent at the time of the funding event.
- `funding_date`: The approximate date when the project received funding. Date format is `YYYY-MM-DD` (ie, '2024-01-17').
- `from_funder_name`: The name of the funder as specified in the funder's YAML file. See more details below.
- `grant_pool_name`: The name of the funding round or grants program.
- `metadata`: Optional metadata from the grants program in JSON format.

## Funder Profiles

Funders in oss-funding are registered as YAML files. Each funder should have its own directory in `./data/funders/` and a YAML file with the same `name`. 

For example, a funder profile for a `funderxyz` would have a YAML file at `./data/funders/funderxyz/funderxyz.yaml` and might contain the following:

```
version: 1
name: funderxyz
type: Foundation
display_name: Funder XYZ
grant_pools:
  - name: grants-round-1
  - name: grants-round-2
```  

The funder profile should also contain a directory of CSV data at `./data/funders/funderxyz/uploads/`, ideally one for each grant pool it has run. These CSV should conform to the schema described above.

## DAOIP-5

Funding data is intended to conform to the DAOIP-5 metadata standard developed by The Metagovernance Project. For more information on DAOIP-5, see [here](https://github.com/metagov/daostar). We have included a conversion utility in [`./daoip-5`](./daoip-5).

## How to Contribute

Currently the main way to contribute is by submitting a pull request. You can add static data in CSV format to the `./uploads/` directory for a given funder. You can also create new funder profiles by following the steps above.

Submissions will be validated to ensure they conform to the schema and don't contain any funding events that are already in the  registry. To test whether your submission is valid, you may run the processing script from your CLI in the root directory:

```
python src/main.py
```

If you do something cool with the data (eg, a visualization or analysis), please share it with us!

Check out [our docs](https://docs.opensource.observer/) for more ways of contributing.
