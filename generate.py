import os
import argparse


def get_directory_structure(root_dir, out_file='paper.md'):
    with open(out_file, 'w') as f:
        f.write('## Papers\n')
        pre_folders = ['']
        for path, dirs, files in sorted(os.walk(root_dir)):
            # print(path, dirs, files)
            paper_list = [file.replace('.pdf', '') for file in files if file.endswith('.pdf')]
            if paper_list:
                folders = path.replace(root_dir, '').split(os.sep)
                folders_print = [x for x in folders if x not in pre_folders]
                for i, folder in enumerate(folders_print):
                    title = '#' * (folders.index(folder) + 2) + ' ' + folder
                    print(title)
                    f.write(title)
                    f.write('\n')
                print(paper_list)
                for paper in paper_list:
                    f.write('- ' + paper)
                    f.write('\n')
                pre_folders = folders


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--root_dir", required=True,
        default=None,
    )
    args = vars(ap.parse_args())
    get_directory_structure(args['root_dir'])


if __name__ == '__main__':
    main()
