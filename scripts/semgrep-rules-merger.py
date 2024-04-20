from argparse import ArgumentParser
from os import listdir, makedirs
from os.path import join as path_join, dirname, exists as path_exists
from yaml import safe_load, dump
    

def merge_rules(rules_dir_path:str, output_file_path:str):
    # List of rule files to merge
    rule_files = list(filter(lambda file_path: file_path.endswith(('.yaml','.yml')), listdir(rules_dir_path)))
    rule_files = list(map(lambda file_path: path_join(rules_dir_path, file_path), rule_files))


    # Initialize an empty list to store merged rules
    merged_rules = []

    # Iterate over each rule file and extract rules
    for rule_file in rule_files:
        with open(rule_file, "r", encoding="utf-8") as file:
            rules = safe_load(file)
            if "rules" in rules:
                merged_rules.extend(rules["rules"])

    # Create a new rule dictionary with the merged rules
    merged_rule_dict = {"rules": merged_rules}

    # Create path if not found
    dir_name = dirname(output_file_path)
    if not path_exists(dir_name):
        makedirs(dir_name)

    # Write the merged rule to a new file
    with open(output_file_path, "w", encoding="utf-8") as file:
        dump(merged_rule_dict, file)

    return merged_rule_dict

if __name__ == '__main__':
    parser = ArgumentParser(prog='semgrep-rules-merger')
    parser.add_argument('-o', '--output', type=str, required=False, dest='output_file_path',help='path of file to store semgrep merged rule')
    parser.add_argument('-rd', '--rules-dir', type=str, required=True, dest='rules_dir',help='path of git repository directory')

    args = parser.parse_args()

    merge_rules(
        rules_dir_path=args.rules_dir,
        output_file_path=args.output_file_path,
    )
