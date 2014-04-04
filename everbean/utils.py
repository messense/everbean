# coding: utf-8
import os
import sys
from datetime import datetime
from douban_client.client import DoubanClient
from douban_client.api.error import DoubanAPIError


class ObjectDict(dict):

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return None

    def __setattr__(self, key, value):
        self[key] = value


def to_unicode(value):
    if isinstance(value, unicode):
        return value
    if isinstance(value, basestring):
        return value.decode('utf-8')
    if isinstance(value, int):
        return str(value)
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return value


def to_str(value):
    if isinstance(value, unicode):
        return value.encode('utf-8')
    if isinstance(value, int):
        return str(value)
    return value


def parse_command_line(app, args=None, final=True):
    if args is None:
        args = sys.argv
    config = dict()
    for i in range(1, len(args)):
        # All things after the last option are command line arguments
        if not args[i].startswith("-"):
            break
        if args[i] == "--":
            break
        arg = args[i].lstrip("-")
        name, equals, value = arg.partition
        name = name.replace('-', '_').upper()
        if not name in app.config:
            app.logger.warning('Unrecognized command line option: %r' % name)
        # convert to bool
        if value == 'True':
            value = True
        if value == 'False':
            value = False
        config[name] = value
        if final:
            app.config[name] = value

    return config


def parse_config_file(app, filename):
    if not os.path.exists(filename):
        app.logger.warning('Configuration file %s does not exist.' % filename)
        return
    if filename.endswith('.py'):
        try:
            app.config.from_pyfile(filename)
        except IOError:
            app.logger.warning("Cannot load configuration from python file %s" % filename)
    else:
        app.config.from_object(filename)


def get_douban_client(app, token=None):
    client = DoubanClient(app.config['DOUBAN_API_KEY'],
                          app.config['DOUBAN_API_SECRET'],
                          app.config['DOUBAN_REDIRECT_URI'],
                          app.config['DOUBAN_API_SCOPE'])
    if token:
        client.auth_with_token(token)
    return client


def get_douban_annotations(app, user, client=None, annotations=None,
                    start=0, count=100, format='html', recursive=True):
    client = client or get_douban_client(app, user.douban_access_token)
    annotations = annotations or []
    entrypoint = 'user/%s/annotations?count=%i&start=%i&format=%s'
    try:
        annos = client.book.get(entrypoint % (user.douban_uid, count, start, format))
    except DoubanAPIError, e:
        app.logger.error('DoubanAPIError status: %s' % e.status)
        app.logger.error('DoubanAPIError reason: %s' % e.reason)
        return annotations
    annotations.extend(annos['annotations'])
    total = annos['total']
    # annos['count'] is always 100, be careful
    real_count = len(annos['annotations'])
    if (total < count) or (start + real_count >= total) or (not recursive):
        return annotations
    start += count
    annotations = get_douban_annotations(app, user, client, annotations, start, count)
    return annotations


def get_books_from_annotations(annotations):
    books = {}
    for annotation in annotations:
        book_id = annotation['book_id']
        if book_id not in books:
            books[book_id] = {
                'book_id': book_id,
                'title': annotation['book']['title'].strip(),
                'subtitle': annotation['book']['subtitle'],
                'author': ', '.join(annotation['book']['author']),
                'alt': annotation['book']['alt'],
                'cover': annotation['book']['image'],
                'updated': None,
                'annotations': {},
            }
        chapter = annotation['chapter']
        if not chapter:
            chapter = '__DEFAULT__'
        if chapter not in books[book_id]['annotations']:
            books[book_id]['annotations'][chapter] = []
        note = {
            'id': annotation['id'],
            'chapter': annotation['chapter'],
            'summary': annotation['summary'],
            'content': annotation['content'],
            'time': annotation['time'],
            'page_no': int(annotation['page_no']),
            'alt': 'http://book.douban.com/annotation/%s/' % annotation['id'],
        }
        if books[book_id]['updated'] is None:
            books[book_id]['updated'] = datetime.strptime(annotation['time'], '%Y-%m-%d %H:%M:%S')
        # reverse notes
        books[book_id]['annotations'][chapter].insert(0, note)
    # sort chapter
    chapter_sort_key = lambda annos: datetime.strptime(annos[1][0]['time'], '%Y-%m-%d %H:%M:%S')
    for book_id in books:
        sorted_annotations_list = sorted(books[book_id]['annotations'].iteritems(), key=chapter_sort_key)
        books[book_id]['annotations'] = sorted_annotations_list
    return books


def generate_enml_makeup(book):
    makeup = '<?xml version="1.0" encoding="UTF-8"?>'
    makeup += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    makeup += '<en-note>%s</en-note>'

    makeup_title = '<h2 style="font-size:18pt; text-align:right;">%s</h2>' % book['title']
    makeup_author = '<h5 style="font-size:12pt; text-align:right; color:gray;">%s</h5>' % book['author']
    makeup_chapter = '<div style="font-size:14pt; text-align:center; margin-top:0.5em; margin-bottom:0.3em;">' \
                     '<div style="position:relative; z-index:-1; top:0.7em; height:2px; max-height:2px; ' \
                     'border-top:1px dotted gray; border-bottom:1px dotted gray;">&nbsp;</div>' \
                     '<span style="font-weight:bold; background-color:white; ' \
                     'position:relative;">%s</span></div>'
    makeup_annotation = '<div style="padding-top:0.5em; padding-bottom:0.5em; border-top:1px dotted lightgray;">' \
                        '<div style="font-size:10pt; margin-bottom:0.2em;">' \
                        '<div style="display:inline-block; width:0.25em; height:0.9em; ' \
                        'margin-right:0.5em; background-color:rgb(100,100,100);">&nbsp;</div>' \
                        '<a href="%s" style="text-decoration:none"><span style="color:darkgray">%s</span></a></div>' \
                        '<div style="font-size:12pt;"><span>%s</span></div></div>'

    makeup_footer = '<div style="margin-top:2em; margin-bottom:1em">' \
                    '<hr style="height:2px; border:0; background-color:#ddd;" />' \
                    '<span style="font-size:10pt; color:gray;">Generated by Everbean</span></div>'

    # book['annotations'] is a list of tuple(string_chapter, list_annotations)
    annotations = book['annotations']
    makeup_annotations = ''

    for chapter_annotations in annotations:
        chapter = chapter_annotations[0]
        if chapter != '__DEFAULT__':
            makeup_annotations += makeup_chapter % chapter
        for annotation in chapter_annotations[1]:
            makeup_annotations += makeup_annotation % (annotation['alt'],
                                                       annotation['time'],
                                                       annotation['content'])

    # Be careful with %%
    makeup_main = '<div style="width:90%%; max-width:600px; margin:0px auto;' \
                  'padding:5px; font-size:12pt; font-family:Times">%s%s%s%s</div>' % (makeup_title,
                                                                                      makeup_author,
                                                                                      makeup_annotations,
                                                                                      makeup_footer)

    return makeup % makeup_main

