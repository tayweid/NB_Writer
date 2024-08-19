# Path: NB_Writer/NB_Writer.py

import json
from IPython.display import Image


def Markdown_Cell_to_LaTeX(cell):
    """ Takes a markdown cell and converts it to LaTeX. """

    tex = ''
    unordered_list = False
    unordered_sublist = False
    numbered_list = False
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

            new_item = line[0:2] == '- '
            new_subitem = line[0:6] == '    - '
            open_list = not unordered_list and new_item
            open_sublist = not unordered_sublist and new_subitem
            add_item = unordered_list and new_item
            add_subitem = unordered_list and unordered_sublist and new_subitem
            close_sublist_only = unordered_sublist and new_item
            close_sublist_list = unordered_sublist and not new_subitem and not new_item
            close_list_only = unordered_list and not unordered_sublist and not new_item and not new_subitem

            if open_list:
                line = r'    \item ' + line.replace('- ','')
                line = r'\begin{itemize}' + '\n' + line
                unordered_list = True
                unordered_sublist = False

            if open_sublist:
                line = r'        \item ' + line.replace('    - ','')
                line = r'    \begin{itemize}' + '\n' + line
                unordered_list = True
                unordered_sublist = True

            if add_item:
                line = r'    \item ' + line.replace('- ','')

            if add_subitem:
                line = r'        \item ' + line.replace('    - ','')

            if close_sublist_only:
                line = r'    \item ' + line.replace('- ','')
                line = r'    \end{itemize}' + '\n' + line
                unordered_list = True
                unordered_sublist = False

            if close_sublist_list:
                line = r'    \end{itemize}' + '\n' + r'\end{itemize}' + '\n' + line
                unordered_list = False
                unordered_sublist = False
            
            if close_list_only:
                line = r'\end{itemize}' + '\n' + line
                unordered_list = False
                unordered_sublist = False

        except:
            pass

        # Add Numbered Lists

        try:
            if numbered_list: # The previous line was a list item
                if line[0:3] in ['1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ']:
                    line = r'    \item ' + line.replace(line[0:3],'')
                else:
                    line = r'\end{enumerate}' + '\n' + line
                    numbered_list = False
            else:
                if line[0:3] in ['1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ']:
                    line = r'    \item ' + line.replace(line[0:3],'')
                    line = r'\begin{enumerate}' + '\n' + line
                    numbered_list = True
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
                line = r'\section*{' + line.replace('# ','').replace('\n','') + r'}' + '\n'
            if line[0:3] == '## ':
                line = r'\subsection*{' + line.replace('## ','') + r'}'
            if line[0:4] == '### ':
                line = r'\subsubsection*{' + line.replace('### ','') + r'}'
            if line[0:5] == '#### ':
                line = line.replace('#### ',r'\ \ \ \ ')
        except:
            pass

        tex = tex + line

    # If the list ends with no more lines

    if unordered_sublist:
        tex = tex + r'    \end{itemize}' + '\n'
    if unordered_list:
        tex = tex + r'\end{itemize}' + '\n'
    if numbered_list:
        tex = tex + r'\end{enumerate}' + '\n'

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

def NB_Write(notebook, title='', author='', date='', template='/Users/taylorjweidman/PROJECTS/NB_Writer/Template', keep=False):

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
    tex = tex + r'\vspace{-2cm}' + '\n\n\n'

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


def Syllabus(course, semester, instructor='Taylor J. Weidman', details='4702 Posvar | taylorjweidman@pitt.edu', keep=False):
    """ Renders the syllabus and merges with the calendar page. """

    from PyPDF2 import PdfMerger
    from datetime import date
    import shutil
    import os

    # Render the syllabus

    title = '\\textbf{' + course + ' | ' + semester + '} \\\\ ' + instructor + ' \\\\ ' + details
    NB_Write('Syllabus', title=title, keep=keep)

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
    if 'History' not in os.listdir():
        os.mkdir('History')
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