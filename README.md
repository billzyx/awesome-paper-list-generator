# Awesome Paper List Generator

> Generate markdown paper list from PDF files. Get paper info automatically from online resources.

## Usage
1. Put your papers into folders, where folders stand for categories. Try to name your paper file as "paper title".pdf. If the filename is not a paper title, it is still OK for most cases. Our program will try to get the paper title from the PDF files, although it may failed sometimes.
![Put paper into folders](pics/folders.png)
2. Run the program
```
$ python generate.py --paper_dir "/your/paper/dir"
```
3. Check paper.md file

## Example 

[awesome-dementia-detection](https://github.com/billzyx/awesome-dementia-detection)

## Other parameters

- --output_md Output markdown file path
- --header_start_index Start index of headers
- --before_md Markdown file before the paper section
- --after_md Markdown file after the paper section
- --update_paper_info Update the latest paper info instead of using the fetched temp file (temp.json). You may also delete the temp.json to do the same job. Note that Semantic Scholar API has a limit of 100 requests per 5 minutes. 

## Miscellaneous
- For Table of contents in "before.md", you may use [GitHub Wiki TOC generator](https://ecotrust-canada.github.io/markdown-toc/)



## Acknowledgements

Some code forked from https://github.com/danielnsilva/semanticscholar
