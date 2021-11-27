from title2bib.crossref import get_bib_from_title
from pdfrw import PdfReader
from bibtexparser.bibdatabase import BibDatabase
import bibtexparser
import re
import os


class PaperParser:
    def __init__(self, temp_bib_file_path='temp.bib'):
        if os.path.isfile(temp_bib_file_path):
            with open(temp_bib_file_path) as bibtex_file:
                self.bib_database = bibtexparser.load(bibtex_file)
        else:
            self.bib_database = BibDatabase()
        self.temp_bib_file_path = temp_bib_file_path

    def _save_bib_database(self):
        with open(self.temp_bib_file_path, 'w') as bibtex_file:
            bibtexparser.dump(self.bib_database, bibtex_file)

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
        found, bib = get_bib_from_title(title, get_first=True, abbrev_journal=False)
        if not found:
            return None
        return bib

    def _get_paper_info(self, bib):
        bib_database = bibtexparser.loads(bib)

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
        for paper_info in self.bib_database.entries:
            if paper_info['title_from_file'].lower() == pdf_title.lower() or\
                    paper_info['title_from_file'].lower() == file_title.lower():
                return paper_info
        use_file_title = False
        title_from_file = pdf_title
        if pdf_title != '':
            paper_bib = self._get_bib_string(pdf_title)
            if paper_bib is not None:
                paper_info = self._get_paper_info(paper_bib)
                if paper_info['title'].lower() != pdf_title.lower():
                    use_file_title = True
            else:
                use_file_title = True
        else:
            use_file_title = True
        if use_file_title:
            paper_bib = self._get_bib_string(file_title)
            paper_info = self._get_paper_info(paper_bib)
            title_from_file = file_title
        paper_info['title_from_file'] = title_from_file
        paper_str = self._get_paper_string_md(paper_info)
        paper_info['paper_str_md'] = paper_str
        self.bib_database.entries.append(paper_info)
        self._save_bib_database()
        return paper_info