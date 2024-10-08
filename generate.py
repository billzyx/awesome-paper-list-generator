import os
import argparse
import logging
from datetime import date

from paper_parser import PaperParser

logger = None


def init_logging():
    logger_init = logging.getLogger()
    formatter = logging.Formatter("%(asctime)s;%(levelname)s    %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger_init.addHandler(stream_handler)
    logger_init.setLevel(logging.DEBUG)
    return logger_init


def load_paper_dicts(root_dir):
    paper_dict_list = []

    for path, dirs, files in sorted(os.walk(root_dir)):
        paper_list = [os.path.join(path, file) for file in files if file.endswith('.pdf')]
        if paper_list:
            folders = path.replace(root_dir, '').split(os.sep)
            paper_dict = dict()
            paper_dict['classes'] = folders
            paper_dict['paper_list'] = paper_list
            paper_dict_list.append(paper_dict)
    return paper_dict_list


def parse_paper_dicts(paper_dict_list, update_paper_info=False, semantic_scholar_api_key=None):
    paper_parser = PaperParser(update_paper_info=update_paper_info, semantic_scholar_api_key=semantic_scholar_api_key)
    for i in range(len(paper_dict_list)):
        paper_info_list = []
        paper_list = paper_dict_list[i]['paper_list']
        for paper_path in paper_list:
            try:
                logging.info('Getting paper:' + paper_path)
                paper_str = paper_parser.parse(paper_path)
                paper_info_list.append(paper_str)
            except:
                logger.warning('Error getting paper: ' + paper_path)
        paper_dict_list[i]['paper_info_list'] = paper_info_list
    return paper_dict_list


def generate_output_md(paper_dict_list, output_md='paper.md', header_start_index=2,
                       before_md='before.md', after_md='after.md'):
    with open(output_md, 'w') as f:
        if os.path.isfile(before_md):
            with open(before_md, 'r') as fb:
                lines = fb.readlines()
                f.writelines(lines)
                f.write('\n')
        f.write('\n')
        f.write('#' * header_start_index + ' Papers\n')
        pre_classes = ['']
        for paper_dict in paper_dict_list:
            classes = paper_dict['classes']
            classes_print = [x for x in classes if x not in pre_classes]
            for paper_class in classes_print:
                header_index = classes.index(paper_class) + header_start_index
                title = '#' * header_index + ' ' + paper_class
                f.write('\n')
                f.write(title)
                f.write('\n')
            paper_info_list = paper_dict['paper_info_list']
            year_list = list(set([paper_info['year'] for paper_info in paper_info_list]))
            for year in reversed(sorted(year_list)):
                title = '- {year}'.format(year=year)
                f.write(title)
                f.write('\n')
                for paper_info in paper_info_list:
                    if paper_info['year'] == year:
                        f.write('\t{paper_str_md}'.format(paper_str_md=paper_info['paper_str_md']))
                        f.write('\n')
            pre_classes = classes

        f.write('\n')
        if os.path.isfile(after_md):
            with open(after_md, 'r') as fa:
                lines = fa.readlines()
                f.writelines(lines)
                f.write('\n')

        today = date.today()
        footnote = '\n***\n\n_This file was generated by [awesome-paper-list-generator]' \
                   '(https://github.com/billzyx/awesome-paper-list-generator), on {date}_\n'.format(date=today)
        f.write(footnote)


def main():
    global logger
    logger = init_logging()
    logger.info('Started.')
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--paper_dir", required=True,
        default=None,
    )
    ap.add_argument(
        "--output_md", required=False,
        default='paper.md',
    )
    ap.add_argument(
        "--header_start_index", required=False, type=int,
        default=2,
    )
    ap.add_argument(
        "--before_md", required=False,
        default='before.md',
    )
    ap.add_argument(
        "--after_md", required=False,
        default='after.md',
    )
    ap.add_argument(
        "--update_paper_info", required=False, action='store_true',
        default=False,
    )
    ap.add_argument(
        "--semantic_scholar_api_key", required=False,
        default=None,
    )
    args = vars(ap.parse_args())
    paper_dict_list = load_paper_dicts(args['paper_dir'])
    paper_dict_list = parse_paper_dicts(
        paper_dict_list,
        update_paper_info=args['update_paper_info'],
        semantic_scholar_api_key=args['semantic_scholar_api_key']
    )
    generate_output_md(paper_dict_list, args['output_md'], args['header_start_index'],
                       before_md=args['before_md'], after_md=args['after_md'])


if __name__ == '__main__':
    main()
