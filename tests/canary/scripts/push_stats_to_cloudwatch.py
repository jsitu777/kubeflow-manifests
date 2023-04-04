import boto3
from datetime import datetime
import xml.etree.ElementTree as ET
import os
import subprocess

xml_path = "../canary/integration_tests.xml"
test_file_name = "../e2e/tests/test_sanity_portforward.py"

def readXML_and_publish_metrics_to_cw():
    tests = get_num_collected_tests(test_file_name)
    print(f"number of test cases run: {tests}")
    if os.path.isfile(xml_path):
        tree = ET.parse(xml_path)
        testsuite = tree.find("testsuite")
        failures = testsuite.attrib["failures"]
        successes = int(tests) - int(failures)
    else:
        failures = 0
        successes = 0
        

    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    print(f"Failures: {failures}")
    print(f"Total tests: {tests}")
    print(f"Success: {successes}")

    # push to cloudwatch
    cw_client = boto3.client("cloudwatch")
    project_name = "CodeBuild-Run-All-Tests"

    # Define the metric data
    metric_data = [
        {
            "MetricName": "failures",
            "Timestamp": timestamp,
            "Dimensions": [
                {"Name": "CodeBuild Project Name", "Value": project_name},
            ],
            "Value": int(failures),
            "Unit": "Count",
        },
        {
            "MetricName": "total_tests",
            "Timestamp": timestamp,
            "Dimensions": [
                {"Name": "CodeBuild Project Name", "Value": project_name},
            ],
            "Value": int(tests),
            "Unit": "Count",
        },
        {
            "MetricName": "successes",
            "Timestamp": timestamp,
            "Dimensions": [
                {"Name": "CodeBuild Project Name", "Value": project_name},
            ],
            "Value": int(successes),
            "Unit": "Count",
        },
    ]

    # Use the put_metric_data method to push the metric data to CloudWatch
    try:
        response = cw_client.put_metric_data(
            Namespace="Canary_Metrics", MetricData=metric_data
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            print("Successfully pushed data to CloudWatch")
            # return 200 status code if successful
            return 200
        else:
            # raise exception if the status code is not 200
            raise Exception(
                "Unexpected response status code: {}".format(
                    response["ResponseMetadata"]["HTTPStatusCode"]
                )
            )
    except Exception as e:
        print("Error pushing data to CloudWatch: {}".format(e))
        # raise exception if there was an error pushing data to CloudWatch
        raise


def get_num_collected_tests(test_file_name):
    # Run the pytest command and capture its output
    result = subprocess.run(["pytest", "-q", "--collect-only", test_file_name], capture_output=True, text=True)

    # Extract the number of collected tests from the output
    num_tests = int(result.stdout.splitlines()[-1].split()[0])

    # Return the number of collected tests as an integer
    return num_tests


def main():
    readXML_and_publish_metrics_to_cw()


if __name__ == "__main__":
    main()