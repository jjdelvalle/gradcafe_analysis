from bs4 import BeautifulSoup
import datetime, time
from IPython.core.debugger import Pdb
import sys, re
import os.path
from collections import Counter
import seaborn as sns
import matplotlib.pyplot as plt
import pandas


PROGS = [
    ('Computer Engineering', 'Electrical and Computer Engineering'),
    ('Computer Enginnerin', 'Electrical and Computer Engineering'),
    ('Electrical', 'Electrical and Computer Engineering'),
    ('ECE', 'Electrical and Computer Engineering'),
    ('Computer Sc', 'Computer Science'),
    ('Computer  Sc', 'Computer Science'),
    ('Computer Sicen', 'Computer Science'),
    ('Computer Sien', 'Computer Science'),
    ('Computer S Cience', 'Computer Science'),
    ('Computer,', 'Computer Science'),
    ('Computers,', 'Computer Science'),
    ('ComputerScience', 'Computer Science'),
    ('Human Computer Interaction', 'Human Computer Interaction'),
    ('Human-Computer Interaction', 'Human Computer Interaction'),
    ('Human-computer Interaction', 'Human Computer Interaction'),
    ('software engineering', 'Software Engineering'),
    ('Embedded', 'Electrical and Computer Engineering'),
    ('Computer Eng', 'Electrical and Computer Engineering'),
    ('Computer Vision', 'Computer Science')]

    # ('computer graphics', 'Game Development'),
    # ('computer gam', 'Game Development'),
    # ('Computer Systems', 'Computer Systems Engineering'),
    # ('Computer And Systems', 'Computer Systems Engineering'),
    # ('Computer & Systems', 'Computer Systems Engineering'),
    # ('Information Technology', 'IT'),
    # ('Communication', 'Computers and Communication'),
    # ('Computer Network', 'Computer Networking'),
    # ('Computer And Computational Sciences', 'Computer And Computational Sciences'),
    # ('Computer Music', 'Computer Music'),
    # ('Computer Control And Automation', 'Computer Control And Automation'),
    # ('Computer Aided Mechanical Engineering', 'CAME'),
    # ('Computer Art', 'Computer Art'),
    # ('Computer Animation', 'Computer Art'),
    # ('composition and computer technologies', 'Computer Art'),
    # ('computer forensics', 'Computer Art')]

DEGREE = [
  (' MFA', 'MFA'),
  (' M Eng', 'MEng'),
  (' MEng', 'MEng'),
  (' M.Eng', 'MEng'),
  (' Masters', 'MS'),
  (' PhD', 'PhD'),
  (' MBA', 'MBA'),
  (' Other', 'Other'),
  (' EdD', 'Other'),
]

STATUS = {
  'A': 'American',
  'U': 'International with US Degree',
  'I': 'International',
  'O': 'Other',
}

COLLEGES = [
  ('Stanford', 'Stanford'),
  ('MIT', 'MIT'),
  ('CMU', 'CMU'),
  ('Cornell', 'Cornell')
]

errlog = {'major': [], 'gpa': [], 'general': [], 'subject': []}
def process(index, col):
    global err
    inst, major, degree, season, status, date_add, date_add_ts, comment = None, None, None, None, None, None, None, None

    if len(col) != 6:
        return []
    try:
        inst = col[0].text.strip()
    except:
        print("Couldn't retrieve institution")
    try:
        major = None
        progtext = col[1].text.strip()

        if not ',' in progtext:
            print('no comma')
            errlog['major'].append((index, col))
        else:
            parts = progtext.split(',')
            major = parts[0].strip()
        progtext = ' '.join(parts[1:])
        for p, nam in PROGS:
            if p.lower() in major.lower():
                major = nam
                break

        degree = None
        for (d, deg) in DEGREE:
          if d in progtext:
            degree = deg
            break
        if not degree:
            degree = 'Other'

        season = None
        mat = re.search('\([SF][012][0-9]\)', progtext)
        if mat:
            season = mat.group()[1:-1]
        else:
            mat = re.search('\(\?\)', progtext)
            if mat:
                season = None
    except NameError  as e:
        print(e)
    except:
        print("Unexpected error:", sys.exc_info()[0])
    try:
        extra = col[2].find(class_='extinfo')
        gpafin, grev, grem, grew, new_gre, sub = None, None, None, None, None, None
        if extra:
            gre_text = extra.text.strip()
            gpa = re.search('Undergrad GPA: ((?:[0-9]\.[0-9]{1,2})|(?:n/a))', gre_text)
            general = re.search('GRE General \(V/Q/W\): ((?:1[0-9]{2}/1[0-9]{2}/(?:(?:[0-6]\.[0-9]{2})|(?:99\.99)|(?:56\.00)))|(?:n/a))', gre_text)
            new_gref = True
            subject = re.search('GRE Subject: ((?:[2-9][0-9]0)|(?:n/a))', gre_text)

            if gpa:
                gpa = gpa.groups(1)[0]
                if not gpa == 'n/a':
                    try:
                        gpafin = float(gpa)
                    except:
                        print("Couldn't convert gpa to float")
            else:
                errlog['gpa'].append((index, gre_text))
            if not general:
                general = re.search('GRE General \(V/Q/W\): ((?:[2-8][0-9]0/[2-8][0-9]0/(?:(?:[0-6]\.[0-9]{2})|(?:99\.99)|(?:56\.00)))|(?:n/a))', gre_text)
                new_gref = False

            if general:
                general = general.groups(1)[0]
                if not general == 'n/a':
                    try:
                        greparts = general.split('/')
                        if greparts[2] == '99.99' or greparts[2] == '0.00' or greparts[2] == '56.00':
                            grew = None
                        else:
                            grew = float(greparts[2])
                        grev = int(greparts[0])
                        grem = int(greparts[1])
                        new_gre = new_gref
                        if new_gref and (grev > 170 or grev < 130 or grem > 170 or grem < 130 or (grew and (grew < 0 or grew > 6))):
                            errlog['general'].append((index, gre_text))
                            grew, grem, grev, new_gre = None, None, None, None
                        elif not new_gref and (grev > 800 or grev < 200 or grem > 800 or grem < 200 or (grew and (grew < 0 or grew > 6))):
                            errlog['general'].append((index, gre_text))
                            grew, grem, grev, new_gre = None, None, None, None
                    except Exception as e:
                        print(e)
            else:
                errlog['general'].append((index, gre_text))

            if subject:
                subject = subject.groups(1)[0]
                if not subject == 'n/a':
                    sub = int(subject)
            else:
                errlog['subject'].append((index, gre_text))

            extra.extract()
        decision = col[2].text.strip()
        try:
            decisionfin, method, decdate, decdate_ts = None, None, None, None
            (decisionfin, method, decdate)  = re.search('((?:Accepted)|(?:Rejected)|(?:Wait listed)|(?:Other)|(?:Interview))? ?via ?((?:E-[mM]ail)|(?:Website)|(?:Phone)|(?:Other)|(?:Postal Service)|(?:POST)|(?:Unknown))? ?on ?([0-9]{1,2} [A-Z][a-z]{2} [0-9]{4})?' , decision).groups()
            if method and method == 'E-Mail':
                method = 'E-mail'
            if method and method=='Unknown':
                method = 'Other'
            if method and method=='POST':
                method = 'Postal Service'
            if decdate:
                try:
                    decdate_date = datetime.datetime.strptime(decdate, '%d %b %Y')
                    decdate_ts = decdate_date.strftime('%s') 
                    decdate = decdate_date.strftime('%d-%m-%Y')
                except Exception as e:
                    decdate_date, decdate_ts, decdate = None, None, None
        except Exception as e:
            print("Couldn't assign method of reporting")
    except Exception as e:
        print("Extra information error")
    try:
        statustxt = col[3].text.strip()
        if statustxt in STATUS:
            status = STATUS[statustxt]
        else:
            status = None
    except:
        print("Couldn't retrieve status")
    try:
        date_addtxt = col[4].text.strip()
        date_add_date = datetime.datetime.strptime(date_addtxt, '%d %b %Y')
        date_add_ts = date_add_date.strftime('%s')
        date_add = date_add_date.strftime('%d-%m-%Y')
    except:
        print("Couldn't retrieve date_add")
    try:
        comment = col[5].text.strip()
    except:
        print("Couldn't retrieve the comment")
    res = [inst, major, degree, season, decisionfin, method, decdate, decdate_ts, gpafin, grev, grem, grew, new_gre, sub, status, date_add, date_add_ts,  comment]
    return res

if __name__ == '__main__':
    args = sys.argv
    if len(args) < 4:
        exit()
    if not args[-1].isdigit():
        exit()

    path = args[1]
    title = args[2]
    n_pages = int(args[3])
    data = []
    for page in range(1, n_pages):
        if not os.path.isfile('{0}/{1}.html'.format(path, page)):
            print("Page {0} not found.".format(page))
            continue
        with open('{0}/{1}.html'.format(path, page), 'r') as f:
            soup = BeautifulSoup(f.read(), features="html.parser")
        tables = soup.findAll('table', class_='submission-table')
        for tab in tables:
            rows = tab.findAll('tr')
            for row in rows[1:]:
                cols = row.findAll('td')
                pro = process(page, cols)
                if len(pro) > 0:
                    data.append(pro)
        if page % 10 == 0:
          print("Processed 10 more pages (page {0})".format(page))

    df = pandas.DataFrame(data)
    df.columns = ['institution', 'major', 'degree', 'season', 'decisionfin', 'method', 'decdate', 'decdate_ts', 'gpafin', 'grev', 'grem', 'grew', 'new_gre', 'sub', 'status', 'date_add', 'date_add_ts',  'comment']

    df.to_csv("data/{0}.csv".format(title))
