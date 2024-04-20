from pathlib import Path
from argparse import ArgumentParser
import collections
import json
import os

## SARIF DATA
SARIF_SCHEMA = 'https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/schemas/sarif-schema-2.1.0.json'
SARIF_VERSION = '2.1.0'

# https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html#_Toc34317648
# SonarQube severity can be one of BLOCKER, CRITICAL, MAJOR, MINOR, INFO
LEVEL_TO_SERVERITY = {
    'warning': 'MAJOR',
    'error': 'CRITICAL',
    'note': 'MINOR',
    'none': 'INFO'
}

# https://docs.sonarsource.com/sonarqube/latest/analyzing-source-code/importing-external-issues/generic-issue-import-format/
DEFAULT_REPORT_TYPE = 'VULNERABILITY'
REPORT_TYPE_BY_ENGINE = {
    'robocop': 'CODE_SMELL',
    'tfline': 'CODE_SMELL'
}

Position = collections.namedtuple('Position', ['line', 'column'])


def main(source, target):
    source = Path(source).resolve()
    target = Path(target).resolve()

    if target.exists():
        raise IOError(f'Target file "{target}" already exist.')

    content = source.read_text(encoding='utf-8')
    sarif_data = json.loads(content)
    if not sarif_data['$schema'].startswith(SARIF_SCHEMA):
        raise ValueError('Source is not a valid sarif file.')

    issues = []
    for run_index, run_data in enumerate(sarif_data['runs'], 1):

        engine_id = run_data['tool']['driver']['name']
        engine_key = engine_id.lower()
        report_type = REPORT_TYPE_BY_ENGINE.get(engine_key, DEFAULT_REPORT_TYPE)

        for result_index, result_data in enumerate(run_data['results'], 1):

            # Code is not programmed to handle multiple locations, because ... Its a WIP
            if (num_locations := len(result_data['locations'])) != 1:
                raise NotImplementedError(
                    f'File {source} : run[{run_index}].results[{result_index}].locations[] '
                    f'size expected 1, actual {num_locations}')

            location_data = result_data['locations'][0]['physicalLocation']
            file_path = location_data['artifactLocation']['uri']
            issue = {
                'engineId': engine_id,
                'primaryLocation': {
                    'filePath': file_path,
                    'message': result_data['message']['text']
                },
                'ruleId': result_data['ruleId'],
                'severity': LEVEL_TO_SERVERITY['warning'], # Semgrep doesn't support severity yet: https://github.com/returntocorp/semgrep/pull/6388
                'type': report_type
            }

            # Converting location data
            start = Position(
                location_data['region']['startLine'] - 1,
                location_data['region']['startColumn'] - 1)
            end = Position(
                location_data['region']['endLine'] - 1,
                location_data['region']['endColumn'] - 1)

            if engine_key == 'robocop':
                # Ensure the end position makes sense or fix it
                lines = Path(file_path).read_text(encoding='utf-8').split(os.linesep)
                if start == end or (end.column and end.column > len(lines[end.line])):
                    prev_start, prev_end = start, end
                    if end.line + 1 < len(lines):
                        # Move end position to next line at column 0
                        end = Position(end.line + 1, 0)
                    else:
                        # Move start to previous line at same column
                        # Move end position to same line at column 0
                        start = Position(start.line - 1, start.column)
                        end = Position(end.line, 0)
                    assert start.line >= 0, (start, end)
                    print(
                        f"Wrong indexation (0-indexed) {file_path}: "
                        f"(start={tuple(prev_start)} end={tuple(prev_end)}), "
                        f"fix it by setting start={tuple(start)} end={tuple(end)}")

            # Lines are 1-indexed both in SARIF and Sonar Generic
            # Columns are 1-indexed in SARIF 0-indexed in Sonar Generic
            issue['primaryLocation']['textRange'] = {
                'startLine': start.line + 1,
                'startColumn': start.column,
                'endLine': end.line + 1,
                'endColumn': end.column
            }

            issues.append(issue)

    target.write_text(json.dumps({'issues': issues}, indent=2), encoding='utf-8')


if __name__ == '__main__':
    parser = ArgumentParser(prog='sarif-to-sonar')
    parser.add_argument('-i', '--input', dest='input_file', type=str, required=True, help='Sarif Input File location')
    parser.add_argument('-o', '--output', dest='output_file', type=str, required=True, help='Sonaqube Issues Output File location')
    args = parser.parse_args()

    main(args.input_file, args.output_file)
