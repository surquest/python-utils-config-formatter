import pytest
from surquest.utils.config.formatter import Formatter


class TestFormatter:

    def test__basic__success(self):
        """Method tests the basic functionality of the Formatter class"""

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

        formatter = Formatter(
            config=config,
            naming_patterns=naming_patterns,
        )

        assert "adm--exchange-rates--ingress--prod" == formatter.get(
            pattern="storage.buckets.ingress"
        )
        assert "adm_exchange_rates_raw" == formatter.get(
            pattern="bigquery.datasets.raw"
        )

    def test__get_resource__success(self):
        """Test formatting from config and naming patterns sourced from files"""

        formatter = Formatter(
            config=Formatter.import_config(
                configs={
                    "GCP": "../config/config.cloud.google.env.PROD.json",
                    "services": "../config/config.cloud.google.services.json",
                    "solution": "../config/config.solution.json",
                }
            ),
            naming_patterns=Formatter.load_json(
                path="../config/naming.patterns.json"
            )
        )

        assert "ADM_FX_API_KEY_PROD" == formatter.get(
            pattern="security.secrets.apiKey",
        )

        assert "adm--exchange-rates--ingress--prod" == formatter.get(
            pattern="storage.buckets.ingress",
        )

        assert "adm_exchange_rates_raw" == formatter.get(
            pattern="bigquery.datasets.raw",
        )

    def test__get_resource__error(self):
        """Test exception: KeyError"""

        formatter = Formatter(
            config={},
            naming_patterns={},
        )

        try:
            formatter.get(
                pattern="non.exiting.patters",
            )

        except KeyError as e:

            assert True is isinstance(e, KeyError)
