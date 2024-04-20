from argparse import ArgumentParser
from json import load, dump
from os import listdir


def merge_sarif_files(input_files_dir, output_file):
    merged_results = []

    input_files = listdir(input_files_dir)

    for file_path in input_files:
        complete_file_path = f'{input_files_dir}/{file_path}'
        with open(complete_file_path, 'r') as f:
            data = load(f)
            if 'runs' in data and isinstance(data['runs'], list):
                merged_results.extend(data['runs'])

    merged_sarif = {
        '$schema': 'https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/schemas/sarif-schema-2.1.0.json',
        'version': '2.1.0',
        'runs': merged_results
    }

    with open(output_file, 'w', encoding='utf-8') as out_f:
        dump(merged_sarif, out_f)

    print(f'[*] Merged Sarif file: {output_file}')


if __name__ == '__main__':
    parser = ArgumentParser(prog='sarif-merger', description='tool to merge sarif files')

    parser.add_argument('-i', '--input-dir', type=str, dest='input_dir',
                        help='path of directory containing sarif files to be merged', required=True)
    parser.add_argument('-o', '--output', type=str, dest='output_file',
                        help='output sarif file path', required=True)

    args = parser.parse_args()

    # merge sarif files
    merge_sarif_files(
        input_files_dir=args.input_dir,
        output_file=args.output_file,
    )
