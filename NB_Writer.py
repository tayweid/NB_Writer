# Path: NB_Writer/NB_Writer.py

import json
from IPython.display import Image


def Markdown_Cell_to_LaTeX(cell):
    """ Takes a markdown cell and converts it to LaTeX. """

    tex = ''
    unordered_list = False
    ordered_list = False

    for line in cell:

        # Add Bold Text
        try:
            while '**' in line:
                line = line.replace('**',r'\textbf{', 1).replace('**','}', 1)
        except:
            pass

        # Add Italics Text
        try:
            while '*' in line:
                line = line.replace('*',r'\textit{', 1).replace('*','}', 1)
        except:
            pass

        # Percentages
        try:
            if '%' in line:
                line = line.replace('%',r'\%')
        except:
            pass

        # Underscores
        try:
            while '_' in line:
                # find how long the underscore is
                underscore_length = 1
                while line[line.find('_')+underscore_length] == '_':
                    underscore_length += 1
                line = line.replace('_'*underscore_length, r'\raisebox{-1ex}{\rule{'+str(3*underscore_length/10)+'cm}{1pt}}')
        except:
            pass

        # Add Unodered Lists
        try:
            if line[0:2] == '- ':
                line = r'\item ' + line.replace('- ','')
                if not unordered_list:
                    line = r'\begin{itemize}' + '\n' + line
                unordered_list = True
            else:
                if unordered_list:
                    line = r'\end{itemize}' + '\n' + line
                    unordered_list = False
        except:
            pass

        # Add Ordered Lists
        enumerate_map = {'a)':1, 'b)':2, 'c)':3, 'd)':4, 'e)':5, 'f)':6, 'g)':7, 'h)':8, 'i)':9, 'j)':10, 'k)':11, 'l)':12, 'm)':13, 'n)':14, 'o)':15, 'p)':16, 'q)':17, 'r)':18, 's)':19, 't)':20}
        try:
            for key in enumerate_map.keys():
                if line[0:3] == key + ' ':
                    line = r'\begin{enumerate}[label=\alph*), start=' + str(enumerate_map[key]) + ']' + '\n' + r'\item ' + line.replace(key,'') + '\n' + r'\end{enumerate}'
        except:
            pass

        # Add Section Headers
        try:
            if line[0:2] == '# ':
                line = r'\section*{' + line.replace('# ','') + r'}'
            if line[0:3] == '## ':
                line = r'\subsection*{' + line.replace('## ','') + r'}'
            if line[0:4] == '### ':
                line = r'\subsubsection*{' + line.replace('### ','') + r'}'
            if line[0:5] == '#### ':
                line = line.replace('#### ',r'\ \ \ \ ')
        except:
            pass

        tex = tex + line

    if '\item ' in line:
        if unordered_list:
            tex = tex + r'\end{itemize}' + '\n'

    tex = tex + '\n\n'

    return tex

def Code_Cell_to_Latex(cell):
    """ This function takes a code cell and returns the latex code for the cell. """
    
    tex = ''
    lines = '\n'.join(cell)

    if 'NB_Writer: ' in lines:
        formatting = lines.split('NB_Writer: ')[1].split('\n')[0]

        if '\nImage(' in lines:
            filename =  lines.split("\nImage('")[1].split("')")[0]

            tex = r'\begin{figure}[h!]' + '\n'
            tex = tex + r'\centering' + '\n'
            tex = tex + str(formatting) + '{' + str(filename) + '}\n'
            tex = tex + r'\end{figure}' + '\n\n'

    return tex

def NB_Write(notebook, title='', author='', date='', template='template', keep=False):

    # Load Template and Notebook

    with open(f'{template}.tex', 'r') as f:
        tex = f.read()
    with open(f'{notebook}.ipynb', 'r') as f:
        nb_json = json.load(f)

    # Start The Document

    tex = tex + '\n'
    tex = tex + r'\title{' + str(title) + '}\n'
    tex = tex + r'\author{' + str(author) + '}\n'
    tex = tex + r'\date{' + str(date) + '}\n'

    tex = tex + '\n'
    tex = tex + r'\begin{document}' + '\n'
    tex = tex + r'\maketitle' + '\n'
    tex = tex + r'\vspace{-2cm}' + '\n'

    # Format the Notebook

    for cell in nb_json['cells']:
        if cell['cell_type'] != 'code':
            tex = tex + Markdown_Cell_to_LaTeX(cell['source'])

        if cell['cell_type'] == 'code':
            tex = tex + Code_Cell_to_Latex(cell['source'])

    # End The Document

    tex = tex + '\n\end{document}'

    # Write the LaTeX to a file

    with open(f'{notebook}.tex', 'w') as f:
        f.write(tex)

    # Compile the LaTeX to a PDF

    import os
    import subprocess

    notebook_path = os.path.abspath(f'{notebook}.ipynb')
    notebook_dir = os.path.dirname(notebook_path)
    os.chdir(notebook_dir)
    pdflatex_path = "/Library/TeX/texbin/pdflatex"
    subprocess.run([pdflatex_path, f'{notebook}.tex'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Clean up the directory

    os.remove(f'{notebook}.aux')
    os.remove(f'{notebook}.log')
    os.remove(f'{notebook}.out')
    if not keep:
        os.remove(f'{notebook}.tex')


def Syllabus(course, semester, instructor='Taylor J. Weidman', details='4702 Posvar | taylorjweidman@pitt.edu'):
    """ Renders the syllabus and merges with the calendar page. """

    from PyPDF2 import PdfMerger
    from datetime import date
    import shutil

    # Render the syllabus

    title = '\\textbf{' + course + ' | ' + semester + '} \\\\ ' + instructor + ' \\\\ ' + details
    NB_Write('Syllabus', title=title)

    # Merge the syllabus with the calendar page

    pdfs = ['Syllabus.pdf', 'Calendar_Page.pdf']
    merger = PdfMerger()
    for pdf in pdfs:
        merger.append(pdf)

    merger.write('Syllabus.pdf')
    merger.close()

    # Copy the syllabus and save with the current date

    today = date.today()
    savedate = '.'.join([str(today.year),str(today.strftime('%m')),str(today.strftime('%d'))])
    shutil.copy('Syllabus.pdf', 'History/Syllabus_'+savedate+'.pdf')

def MiniExam(course, ME_number, date, keep=False):
    """ Render a ME. """

    title = '\\textbf{' + str(course) + ' | ' + 'MiniExam ' + str(ME_number) + '} \\\\ Given: ' + date
    NB_Write(f'ME_{ME_number}', title=title, keep=keep)

def Exam(course, ME_value, date, keep=True, ME=True):
    """ Render an Exam. """

    ME_str = str(ME_value)
    if ME:
        ME_str = 'MiniExam ' + ME_str

    title = '\\textbf{' + str(course) + ' | ' + ME_str + ' Exam} \\\\ Given: ' + date
    NB_Write(ME_str, title=title, keep=keep)