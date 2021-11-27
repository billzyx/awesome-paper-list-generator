from pdfrw import PdfReader
import os
import json

from semantic_scholar_api import SemanticScholar


class PaperParser:
    def __init__(self, temp_json_file_path='temp.json', update_paper_info=False):
        if os.path.isfile(temp_json_file_path) and not update_paper_info:
            with open(temp_json_file_path) as json_file:
                self.json_database = json.load(json_file)
        else:
            self.json_database = []
        self.temp_json_file_path = temp_json_file_path
        self.semantic_scholar = SemanticScholar()

    def _save_json_database(self):
        with open(self.temp_json_file_path, 'w') as json_file:
            json.dump(self.json_database, json_file, indent=4)

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

    def _get_paper_info(self, paper_title):
        search_result = self.semantic_scholar.search(paper_title)
        if search_result['total'] == 0:
            return None
        paper_id = search_result['data'][0]['paperId']
        paper_info = self.semantic_scholar.paper(paper_id)
        return paper_info

    def _get_paper_string_md(self, paper_info):
        author_str = ' '.join([author['name'] for author in paper_info['authors']])
        url = paper_info['url']
        if paper_info['doi']:
            url = 'https://doi.org/{}'.format(paper_info['doi'])
        elif paper_info['arxivId']:
            url = 'https://arxiv.org/abs/{}'.format(paper_info['arxivId'])
        paper_str = '- [{title}]({url}) - {author}, {journal}, ({year}), Cited By: {cited_by}'.format(
            title=paper_info['title'],
            url=url, author=author_str,
            journal=paper_info['venue'], year=paper_info['year'], cited_by=paper_info['numCitedBy'])

        return paper_str

    def parse(self, paper_path):
        pdf_title, file_title = self._get_paper_title(paper_path)
        for paper_info in self.json_database:
            if paper_info['title_from_file'].lower() == pdf_title.lower() or\
                    paper_info['title_from_file'].lower() == file_title.lower():
                paper_info['paper_str_md'] = self._get_paper_string_md(paper_info)
                return paper_info
        use_file_title = False
        title_from_file = pdf_title
        if pdf_title != '':
            paper_info = self._get_paper_info(pdf_title)
            if paper_info is not None:
                if paper_info['title'].lower() != pdf_title.lower():
                    use_file_title = True
            else:
                use_file_title = True
        else:
            use_file_title = True
        if use_file_title:
            paper_info = self._get_paper_info(file_title)
            title_from_file = file_title
        paper_info['title_from_file'] = title_from_file
        self.json_database.append(paper_info)
        self._save_json_database()
        paper_info['paper_str_md'] = self._get_paper_string_md(paper_info)
        return paper_info