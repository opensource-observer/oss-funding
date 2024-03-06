# OSS Funding [![License: Apache 2.0][license-badge]][license]

[license]: https://opensource.org/license/apache-2-0/
[license-badge]: https://img.shields.io/badge/License-Apache2.0-blue.svg

This repository contains a curated registry of grants and other funding to open source software (OSS) projects. Data is uploaded in CSV or JSON format and transformed to a common schema.

This directory is a public good, free to use and distribute. We hope it serves the needs of researchers, developers, foundations, and other users looking to better understand the OSS ecosystem!

## Schema

Here is the current schema for indexing funding data:

- `oso_slug`: The OSO project slug (if it exists).
- `project_name`: The name of the project (according to the funder's data).
- `project_id`: The unique identifier for the project (according to the funder's data).
- `project_url`: The URL of the project's grant application or profile.
- `project_address`: The address the project used to receive the grant.
- `funder_name`: The name of the funding source.
- `funder_round_name`: The name of the funding round or grants program.
- `funder_round_type`: The type of funding this round is (eg, retrospective, builder grant, etc).
- `funder_address`: The address of the funder.
- `funding_amount`: The amount of funding.
- `funding_currency`: The currency of the funding amount.
- `funding_network`: The network the funding was provided on (eg, Mainnet, Optimism, Arbitrum, fiat, etc).
- `funding_date`: The date of the funding event.

## How to contribute

Currently the main way to contribute is by submitting a pull request. You can add static data in CSV or JSON format to the `./uploads/` directory. You can also transform the data to meet our schema and add a CSV version to the `./clean/` directory. Submissions will be validated to ensure they conform to the schema and don't contain any funding events that are already in the registry. 

If you do something cool with the data (eg, a visualization or analysis), please share it with us!

Check out [our docs](https://docs.opensource.observer/) for more ways of contributing.
