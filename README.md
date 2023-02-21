![GitHub](https://img.shields.io/github/license/surquest/python-utils-config-formatter?style=flat-square)
![GitHub Workflow Status (with branch)](https://img.shields.io/github/actions/workflow/status/surquest/python-utils-config-formatter/test.yml?branch=main&style=flat-square)
![Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/surquest/6e25c317000917840152a5e702e71963/raw/python-utils-config-formatter.json&style=flat-square)
![PyPI - Downloads](https://img.shields.io/pypi/dm/surquest-utils-config-formatter?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/surquest-utils-config-formatter)


# Introduction

The Formatter helps you to follow the naming patterns of resources defined
for your Python application as well as for the IaC (Infrastructure as Code)
scripts in Terraform.

# Getting started

Following example illustrates how to use the Formatter can help you get names of resources defined with the help of the naming patterns.


```python
# Project configuration
config = {
    "env": "PROD",
    "project": {
        "code": "analytics-datamart",
        "slug": "adm",
        "solution": {
            "code": "exchange-rates",
            "slug": "fx"
        }
    }
}
# Project naming patterns
naming_patterns = {
    "storage": {
        "buckets": {
            "ingress": "${project.slug}--${project.solution.code}--ingress--${lower(env)}",
            "asset": "${project.slug}--${project.solution.code}--assets--${lower(env)}",
        }
    },
    "bigquery": {
        "datasets": {
            "raw": "${project.slug}_${replace(project.solution.code,'-','_')}_raw",
            "reporting": "${project.slug}_${replace(project.solution.code,'-','_')}_reporting",
        }
    }
}

from surquest.utils.config.formatter import Formatter
formatter = Formatter(
    config=config,
    naming_patterns=naming_patterns,
)

# Get the name of the bucket for the ingress data
formatter.get("storage.buckets.ingress") # adm--exchange-rates--ingress--prod
formatter.get("bigquery.datasets.raw") # adm_exchange_rates_raw
```

# Advanced usage

Let's assume we have all the configuration specified in 4 different JSON files
as follows:

* `config.cloud.google.env.PROD.json` - configuration for the production
  environment (GCP project details)
* `config.cloud.google.services.json` - specification of the GCP services used
  in the project (e.g. BigQuery, Cloud Storage, Cloud SQL, etc.) - independent
  on the environment
* `config.solution.json` - specification of the solution (e.g. name of the
  solution, name of the solution owner, etc.) - independent on the environment
* `config.tenants.json` - specification of the tenants (e.g. name of the tenant,
  country of the tenant, etc.) - independent on the environment

If you want to see more details about the configuration files, please check
the [config directory](https://github.com/surquest/python-utils-config-formatter/tree/main/config)

```python
from surquest.utils.config.formatter import Formatter

formatter = Formatter(
  config=Formatter.import_config(
    configs={
      "GCP": "path/to/config/config.cloud.google.env.PROD.json",
      "services": "path/to/config/config.cloud.google.services.json",
      "solution": "path/to/config/config.solution.json",
    }
  ),
  naming_patterns=Formatter.load_json(
    path="path/to/config/naming.patterns.json"
  )
)

formatter.get("storage.buckets.ingress") # adm--exchange-rates--ingress--prod
```


# Local development

You are more than welcome to contribute to this project. To make your start easier we have prepared a docker image with all the necessary tools to run it as interpreter for Pycharm or to run tests.

## Build docker image

```
docker build `
--tag python/utils/config/formatter     `
--file package.base.dockerfile `
--target test .
```

## Run tests

```
docker run --rm -it `
-v "${pwd}:/opt/project" `
-w "/opt/project/test" `
python/utils/config/formatter pytest
```