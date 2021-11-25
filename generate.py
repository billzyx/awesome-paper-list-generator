import os
import argparse
from title2bib.crossref import get_bib_from_title
from pdfrw import PdfReader
from bibtexparser.bparser import BibTexParser
import re
import logging

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


class PaperParser:
    def _get_paper_title(self, file_path):
        # Use filename as paper title if get filename from pdf failed.
        reader = PdfReader(file_path)
        pdf_title = str(reader.Info.Title)
        if pdf_title is None or pdf_title == '' or pdf_title == '()' or pdf_title == 'None' or pdf_title == '(Untitled)':
            pdf_title = ''
        else:
            pdf_title = pdf_title.strip('()')
        file_title = os.path.basename(file_path).replace('.pdf', '')
        return pdf_title, file_title

    def _get_bib_string(self, title):
        _, bib = get_bib_from_title(title, get_first=True, abbrev_journal=False)
        return bib

    def _get_paper_info(self, bib):
        bib_tex_parser = BibTexParser()
        bib_database = bib_tex_parser.parse(bib)

        paper_info = bib_database.entries[0]
        return paper_info

    def _get_paper_string_md(self, paper_info):
        if 'journal' in paper_info:
            journal = paper_info['journal'].replace('{', '').replace('}', '')
        elif 'booktitle' in paper_info:
            journal = paper_info['booktitle']
        else:
            journal = ''

        paper_str = '- [{title}]({url}) - {author}, {journal}, ({year})'.format(
            title=re.sub("[^\\-0-9a-zA-Z ]+", "", paper_info['title']),
            url=paper_info['url'], author=paper_info['author'],
            journal=journal, year=paper_info['year'])

        return paper_str

    def parse(self, paper_path):
        pdf_title, file_title = self._get_paper_title(paper_path)
        if pdf_title != '':
            paper_bib = self._get_bib_string(pdf_title)
            paper_info = self._get_paper_info(paper_bib)
            if paper_info['title'] != pdf_title:
                paper_bib = self._get_bib_string(file_title)
                paper_info = self._get_paper_info(paper_bib)
        else:
            paper_bib = self._get_bib_string(file_title)
            paper_info = self._get_paper_info(paper_bib)
        paper_str = self._get_paper_string_md(paper_info)
        paper_info['paper_str_md'] = paper_str
        return paper_info


def parse_paper_dicts(paper_dict_list):
    paper_parser = PaperParser()
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
        f.write('## Papers\n')
        pre_classes = ['']
        for paper_dict in paper_dict_list:
            classes = paper_dict['classes']
            classes_print = [x for x in classes if x not in pre_classes]
            for paper_class in classes_print:
                header_index = classes.index(paper_class) + header_start_index
                title = '#' * (header_index) + ' ' + paper_class
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

        if os.path.isfile(after_md):
            with open(after_md, 'r') as fa:
                lines = fa.readlines()
                f.writelines(lines)


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
    args = vars(ap.parse_args())
    paper_dict_list = load_paper_dicts(args['paper_dir'])
    paper_dict_list = parse_paper_dicts(paper_dict_list)
    generate_output_md(paper_dict_list, args['output_md'], args['header_start_index'],
                       before_md=args['before_md'], after_md=args['after_md'])


if __name__ == '__main__':
    main()
