import os
import argparse
from title2bib.crossref import get_bib_from_title
from pdfrw import PdfReader
from bibtexparser.bparser import BibTexParser


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
        title = str(reader.Info.Title)
        if title is None or title == '' or title == '()' or title == 'None' or title == '(Untitled)':
            title = os.path.basename(file_path).replace('.pdf', '')
        else:
            title = title.strip('()')
        return title

    def _get_bib_string(self, title):
        _, bib = get_bib_from_title(title, get_first=True, abbrev_journal=False)
        return bib

    def _get_paper_info(self, bib):
        bib_tex_parser = BibTexParser()
        bib_database = bib_tex_parser.parse(bib)

        paper_info = bib_database.entries[0]
        return paper_info

    def _get_paper_string_md(self, paper_info):
        if hasattr(paper_info, 'journal'):
            journal = paper_info['journal'].replace('{', '').replace('}', '')
        else:
            journal = paper_info['booktitle']

        paper_str = '- [{title}]({url}) - {author}, {journal}, ({year})'.format(
            title=paper_info['title'], url=paper_info['url'], author=paper_info['author'],
            journal=journal, year=paper_info['year'])

        return paper_str

    def parse(self, paper_path):
        paper_title = self._get_paper_title(paper_path)
        paper_bib = self._get_bib_string(paper_title)
        paper_info = self._get_paper_info(paper_bib)
        paper_str = self._get_paper_string_md(paper_info)
        return paper_str




def parse_paper_dicts(paper_dict_list):
    paper_parser = PaperParser()
    for i in range(len(paper_dict_list)):
        paper_str_list = []
        paper_list = paper_dict_list[i]['paper_list']
        for paper_path in paper_list:
            try:
                paper_str = paper_parser.parse(paper_path)
                paper_str_list.append(paper_str)
            except:
                print('Error getting paper:', paper_path)
        paper_dict_list[i]['paper_str_list'] = paper_str_list
    return paper_dict_list


def generate_output_md(paper_dict_list, output_md='paper.md', header_index=2):
    with open(output_md, 'w') as f:
        f.write('## Papers\n')
        pre_classes = ['']
        for paper_dict in paper_dict_list:
            classes = paper_dict['classes']
            classes_print = [x for x in classes if x not in pre_classes]
            for paper_class in classes_print:
                title = '#' * (classes.index(paper_class) + header_index) + ' ' + paper_class
                f.write(title)
                f.write('\n')
            paper_str_list = paper_dict['paper_str_list']
            for paper_str in paper_str_list:
                f.write('- ' + paper_str)
                f.write('\n')
            pre_classes = classes


def main():
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
        "--header_index", required=False, type=int,
        default=2,
    )
    args = vars(ap.parse_args())
    paper_dict_list = load_paper_dicts(args['paper_dir'])
    paper_dict_list = parse_paper_dicts(paper_dict_list)
    generate_output_md(paper_dict_list, args['output_md'], args['header_index'])


if __name__ == '__main__':
    main()
