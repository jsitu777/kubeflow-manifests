import boto3
import datetime
import xml.etree.ElementTree as ET


xml_path = "../canary/integration_tests.xml"

def readXML_and_publish_metrics_to_cw():
    tree = ET.parse(xml_path)
    testsuite = tree.find('testsuite')
    failures = testsuite.attrib['failures']
    errors = testsuite.attrib['errors']
    tests = testsuite.attrib['tests']
    timestamp = testsuite.attrib['timestamp']

    success_rate = 1 - (int(failures)/int(tests))

    print (f"Failures: {failures}")
    print (f"Errors: {errors}")
    print (f"Total tests: {tests}")
    print (f"Success_rate: {success_rate}")

    #push to cloudwatch
    cw_client = boto3.client("cloudwatch")
    # Define the metric data
    metric_data = [
        {
            'MetricName': 'failures',
            'Timestamp': timestamp,
            'Value': int(failures),
            'Unit': 'Count'
        },
        {
            'MetricName': 'errors',
            'Timestamp': timestamp,
            'Value': int(errors),
            'Unit': 'Count'
        },
        {
            'MetricName': 'total_tests',
            'Timestamp': timestamp,
            'Value': int(tests),
            'Unit': 'Count'
        },
        {
            'MetricName': 'successes_rate',
            'Timestamp': timestamp,
            'Value': success_rate,
            'Unit': 'Percent'
        }
    ]

# Use the put_metric_data method to push the metric data to CloudWatch
    try:
        response = cw_client.put_metric_data(
            Namespace='Canary_Telemetry',
            MetricData=metric_data
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print("Successfully pushed data to CloudWatch")
            # return 200 status code if successful
            return 200
        else:
            # raise exception if the status code is not 200
            raise Exception("Unexpected response status code: {}".format(response['ResponseMetadata']['HTTPStatusCode']))
    except Exception as e:
        print("Error pushing data to CloudWatch: {}".format(e))
        # raise exception if there was an error pushing data to CloudWatch
        raise

    



    

def main(): 
    readXML_and_publish_metrics_to_cw()

if __name__ == "__main__":
    main()


