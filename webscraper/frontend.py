import requests
from utils import *
import lxml.html

# Parse the data found from the json response
def parse_competition(contestID):
    url = 'https://strongmanarchives.com/viewContest.php?id=' + str(contestID)

    request = requests.get(url)
    if request.status_code == 500:
        raise EmptyPageError('No record found')
    doc = lxml.html.fromstring(request.content)

    # section off unwanted content - limit to only first table
    root = lxml.etree.HTML(request.content)
    path = root[1][1][0]
    correctChildren = list(path)[0:1]
    for child in list(path)[1:]:
        tag = child.tag
        if tag == 'h3': break
        correctChildren.append(child)
    
    for child in list(path):
        if child not in correctChildren:
            path.remove(child)
    
    doc_string = lxml.etree.tostring(root, encoding='UTF-8', method="html", xml_declaration=None, pretty_print=True, with_tail=True, standalone=None, doctype=None, exclusive=False, inclusive_ns_prefixes=None, with_comments=True, strip_text=False, )
    doc = lxml.html.fromstring(doc_string)

    # select title
    title = doc.xpath('/html/head/title')[0].text.split('Strongman Archives -')[1].strip()

    # select header information
    header_information = []

    # Usually the header information is formatted into a table
    header = doc.xpath('/html/body/center/div/table/thead/tr/th/center/*')
    for item in header:
        header_information.append(item.text_content())

    # Sometimes it's formatted as a random piece of text for some ungodly reason
    if (len(header_information) == 0):
        header = doc.xpath('/html/body/center/div/*')

        for item in header:
            if (item.tag == 'br'):
                break
            header_information.append(item.text_content())
    
    # Summarize extra header content
    header_additional = ",".join(header_information[2:])

    # Find the event information
    event_list = {}
    contest_notes = "None"
    if (len(doc.find_class('content')) != 0):
        event_content = doc.find_class('content')[0].text_content()
        notes_info = processNotes(event_content)
        event_list = notes_info[0]
        contest_notes = notes_info[1]
    
    # Now time to extract the column names and pray so we can splice together our two information sources
    table = doc.cssselect('thead')
    column_labels = []
    for item in table:
        column_labels.append(item.text_content())

    # remove labels for the header table because god forbid you could actually use ids
    for item in header_information:
        for label in column_labels:
            if (item in label):
                column_labels.remove(label)
    
    # prettify entries
    column_labelset = []
    for row in column_labels:
        column_labelset.append(prettifyEntry(row))
    
    # store information as json object
    info = {
        'title': title,
        'competition': header_information[0],
        'location_info': header_information[1],
        'additional_header_information': header_additional,
        'column_headers': column_labelset[0],
        'event_info': event_list,
        'comp_id': contestID,
        'contest_notes': contest_notes            
    }

    return info

@staticmethod
def processNotes(content):
  event_list = {}
  contest_notes = "None"
  # Handle the contest notes case
  if ('Contest Notes' or 'Source') in content:
      content_split = splitIntoLines(content)
      source_line = ""
      content_line = ""
      event_lines = []
      for n in content_split:
          if 'Source:' in n:
              source_line =  prettifyEntry(n)[0]
          elif 'Contest Notes:' in n:
              content_line =  prettifyEntry(n)[0]
          else:
              event_lines.append(n)

      contest_notes = (content_line + ' ' + source_line).strip()
      content = '.'.join((str(n)for n in event_lines))

  event_info = prettifyEntry(content)

  # convert events to dictionary
  for event in event_info:
      e = list(map(lambda a: a.strip(), event.split(':')))
      event_list[e[0]] = e[1]

  return [event_list, contest_notes]

@staticmethod
def splitIntoLines(content):
  contest_notes_raw = content.split(':')
  line = []
  buffer = ''
  next = ''
  for n in contest_notes_raw:
      parity = contest_notes_raw.index(n) % 2
      if parity == 0:
          if len(next) != 0:
              buffer = next + ": "
              process = splitOnPeriod(line, buffer, next, n)
              line = process[0]
              buffer = process[1]
              next = process[2]
          else:
              buffer = n + ": "
      else:
        if len(next) != 0:
            buffer = next + ': '
        process = splitOnPeriod(line, buffer, next, n)
        line = process[0]
        buffer = process[1]
        next = process[2]
  return line

def splitOnPeriod(line, buffer, next, n):
    subelements = n.split('.')
    next = subelements.pop()
    if ('\r\n' in next):
        p = next.split('\r\n')
        end = p.pop(0).strip()
        if len(end) != 0:
            subelements.append(end)
            next = ''.join(('\r\n' + str(n) for n in p))

    buffer = buffer + '.'.join((str(n).strip() for n in subelements))
    line.append(buffer)
    buffer = ""
    return [line, buffer, next]
