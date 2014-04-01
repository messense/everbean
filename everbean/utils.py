# coding: utf-8
import os
import sys
from evernote.api.client import EvernoteClient
from evernote.edam.type.ttypes import Note
from douban_client.client import DoubanClient


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


def get_evernote_client(app, is_i18n=True, token=None):

    def get_evernote_service_host():
        if app.config['EVERNOTE_SANDBOX']:
            return 'sandbox.evernote.com'
        if is_i18n:
            return 'wwww.evernote.com'
        else:
            return 'app.yinxiang.com'

    if token:
        client = EvernoteClient(token=token,
                                sandbox=app.config['EVERNOTE_SANDBOX'],
                                service_host=get_evernote_service_host())
    else:
        client = EvernoteClient(consumer_key=app.config['EVERNOTE_CONSUMER_KEY'],
                                consumer_secret=app.config['EVERNOTE_CONSUMER_SECRET'],
                                sandbox=app.config['EVERNOTE_SANDBOX'],
                                service_host=get_evernote_service_host())

    return client


def get_douban_client(app, token=None):
    client = DoubanClient(app.config['DOUBAN_API_KEY'],
                          app.config['DOUBAN_API_SECRET'],
                          app.config['DOUBAN_REDIRECT_URI'],
                          app.config['DOUBAN_API_SCOPE'])
    if token:
        client.auth_with_token(token)
    return client


def get_books_from_annotations(annotations):
    books = {}
    for annotation in annotations:
        book_id = annotation['book_id']
        if book_id not in books:
            books[book_id] = {
                'book_id': book_id,
                'title': annotation['book']['title'],
                'subtitle': annotation['book']['subtitle'],
                'author': annotation['book']['author'],
                'alt': annotation['book']['alt'],
                'cover': annotation['book']['image'],
                'annotations': {},
            }
        chapter = annotation['chapter']
        if not chapter:
            chapter = '__DEFAULT__'
        if chapter not in books[book_id]['annotations']:
            books[book_id]['annotations'][chapter] = []
        note = {
            'chapter': annotation['chapter'],
            'summary': annotation['summary'],
            'content': annotation['content'],
            'time': annotation['time'],
            'page_no': int(annotation['page_no']),
        }
        # reverse notes
        books[book_id]['annotations'][chapter].insert(0, note)
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
                        '<span style="color:darkgray">%s</span></div>' \
                        '<div style="font-size:12pt;"><span>%s</span></div></div>'

    makeup_footer = '<div style="margin-top:2em; margin-bottom:1em">' \
                    '<hr style="height:2px; border:0; background-color:#ddd;">' \
                    '<span style="font-size:10pt; color:gray;">Generated by Everbean</span></div>'

    annotations = book['annotations']
    makeup_annotations = ''

    for chapter in annotations:
        if chapter != '__DEFAULT__':
            makeup_annotations += makeup_chapter % chapter
        for annotation in annotations[chapter]:
            makeup_annotations += makeup_annotation % (annotation['time'], annotation['content'])

    # Be careful with %%
    makeup_main = '<div style="width:90%%; max-width:600px; margin:0px auto;' \
                  'padding:5px; font-size:12pt; font-family:Times">%s%s%s%s</div>' % (makeup_title,
                                                                                      makeup_author,
                                                                                      makeup_annotations,
                                                                                      makeup_footer)

    return makeup % makeup_main


def make_note(book, note=None):

    makeup = generate_enml_makeup(book)

    note = note or Note()
    note.title = book['title']
    note.content = makeup

    return note
