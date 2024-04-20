from os import getenv
from argparse import ArgumentParser
from requests import post


def upload_to_defectdojo(is_new_import: bool, token: str | None, url: str, product_name: str, engagement_name: str, filename: str):
    if token is None:
        print('Token is required')
        exit(-1)

    multipart_form_data = {
        'file': (filename, open(filename, 'rb')),
        'scan_type': (None, 'Semgrep JSON Report'),
        'product_name': (None, product_name),
        'engagement_name': (None, engagement_name),
    }

    endpoint = '/api/v2/import-scan/' if is_new_import else '/api/v2/reimport-scan/'
    r = post(
        url + endpoint,
        files=multipart_form_data,
        headers={
            'Authorization': 'Token ' + token,
        }
    )
    if r.status_code != 200:
        exit(f'Post failed: {r.text}')
    print(r.text)


if __name__ == "__main__":
    try:
        token = getenv("DEFECT_DOJO_API_TOKEN")
    except KeyError:
        print("Please set the environment variable DEFECT_DOJO_API_TOKEN")
        exit(1)

    parser = ArgumentParser('s2dd')
    parser.add_argument('--host', help='Defect Dojo URL', required=True, type=str, dest='host')
    parser.add_argument('--product', help='Product name', required=True, type=str, dest='product')
    parser.add_argument('--engagement', help='Engagement name',
                        required=True, type=str, dest='engagement')
    parser.add_argument('--report', help='Semgrep JSON report file', required=True, type=str, dest='report')

    args = parser.parse_args()
    url = args.url
    product_name = args.product
    engagement_name = args.engagement
    report = args.report

    upload_to_defectdojo(True, token, url, product_name, engagement_name, report)
