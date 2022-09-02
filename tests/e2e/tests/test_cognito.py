import requests
import pytest
import time

from e2e.utils.config import metadata, configure_env_file
from e2e.conftest import region

from e2e.fixtures.cluster import cluster
from e2e.fixtures.installation import installation, clone_upstream
from e2e.fixtures.clients import account_id

from e2e.fixtures.cognito_dependencies import (
    cognito_bootstrap,
    post_deployment_dns_update,
)

INSTALLATION_PATH_FILE = "./resources/kubeflow_installation_paths.yaml"

@pytest.fixture(scope="class")
def installation_path(installation_option,aws_telemetry_option,deployment_option):
    print(f"Installation Option: {installation_option}")
    print(f"Deployment Option: {deployment_option}")
    print(f"AWS-telemetry Option: {aws_telemetry_option}")
    return INSTALLATION_PATH_FILE


@pytest.fixture(scope="class")
def configure_manifests(region, cluster, cognito_bootstrap):
    print(
        "fixture to introduce dependency to setup cognito related resources before applying manifests"
    )


class TestCognito:
    @pytest.fixture(scope="class")
    def setup(self, metadata, post_deployment_dns_update):
        metadata_file = metadata.to_file()
        metadata.log()
        print("Created metadata file for TestSanity", metadata_file)

    def test_url_is_up(self, setup, cognito_bootstrap):
        subdomain_name = cognito_bootstrap["route53"]["subDomain"]["name"]
        kubeflow_endpoint = "https://kubeflow." + subdomain_name
        print("kubeflow_endpoint:")
        print(kubeflow_endpoint)
        #wait a bit till website is accessible
        print("Wait for 60s for website to be available...")
        time.sleep(60)
        response = requests.get(kubeflow_endpoint)
        assert response.status_code == 200
        # request was redirected
        assert len(response.history) > 0
        # redirection was to cognito domain
        assert "auth." + subdomain_name in response.url

    # Kubeflow sdk client need cookies provided by ALB. Currently it is not possible to programmatically fetch these cookies using tokens provided by cognito
    # See - https://stackoverflow.com/questions/62572327/how-to-pass-cookies-when-calling-authentication-enabled-aws-application-loadbala
    # The other way to test multiuser kfp is by using selenium and creating a session using a real browser. There are drivers which can be used via Selenium webdriver to programmatically control a browser
    # e.g. https://chromedriver.chromium.org/getting-started
    # This is a hack and has been implemented in this PR - https://github.com/kubeflow/pipelines/pull/4182
    # TODO: explore if this will work in codebuild since there is an option to run headless i.e. without GUI
