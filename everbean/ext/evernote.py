# coding=utf-8
from __future__ import absolute_import
from collections import OrderedDict
from flask import current_app
from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors
from everbean.utils import to_str


def get_evernote_service_host(app=None, is_i18n=True):
    app = app or current_app
    if app.config['EVERNOTE_SANDBOX']:
        return 'sandbox.evernote.com'
    if is_i18n:
        return 'wwww.evernote.com'
    else:
        return 'app.yinxiang.com'


def get_evernote_client(app=None, is_i18n=True, token=None):
    app = app or current_app
    if token:
        client = EvernoteClient(token=token,
                                sandbox=app.config['EVERNOTE_SANDBOX'],
                                service_host=get_evernote_service_host(app, is_i18n))
    else:
        client = EvernoteClient(consumer_key=app.config['EVERNOTE_CONSUMER_KEY'],
                                consumer_secret=app.config['EVERNOTE_CONSUMER_SECRET'],
                                sandbox=app.config['EVERNOTE_SANDBOX'],
                                service_host=get_evernote_service_host(app, is_i18n))
    return client


def find_note(note_store, guid):
    note = None
    try:
        note = note_store.getNote(guid, False, False, False, False)
    except Errors.EDAMUserException, eue:
        current_app.logger.warning('[find_note] EDAMUserException code: %i, '
                                   'paramter: %s' % (eue.errorCode, eue.parameter))
    except Errors.EDAMNotFoundException:
        current_app.logger.warning('[find_note] EDAMNotFoundException: '
                                   'Invalid note GUID (%s).' % guid)
    return note


def create_notebook(note_store, name):
    notebook = Types.Notebook()
    if name is None:
        return notebook
    notebook.name = to_str(name)
    try:
        notebook = note_store.createNotebook(notebook)
    except Errors.EDAMUserException, eue:
        current_app.logger.warning('[create_notebook] EDAMUserException code: %i, '
                                   'paramter: %s' % (eue.errorCode, eue.parameter))
    return notebook


def get_notebook(note_store, guid=None, name=None):
    if guid is None:
        if name is not None:
            return create_notebook(note_store, name)
        else:
            return note_store.getDefaultNotebook()
    error = False
    notebook = None
    try:
        notebook = note_store.getNotebook(guid)
    except Errors.EDAMUserException, eue:
        current_app.logger.warning('[get_notebook] EDAMUserException code: %i, '
                                   'paramter: %s' % (eue.errorCode, eue.parameter))
        error = True
    except Errors.EDAMNotFoundException:
        current_app.logger.warning('[get_notebook] EDAMNotFoundException: '
                                   'Invalid notebook GUID (%s).' % guid)
        error = True
    if error:
        # create the Notebook
        notebook = create_notebook(note_store, name)
    return notebook


def create_note(note_store, note):
    try:
        note = note_store.createNote(note)
    except Errors.EDAMUserException, eue:
        current_app.logger.warning('[create_note] EDAMUserException code: %i, '
                                   'paramter: %s' % (eue.errorCode, eue.parameter))
    except Errors.EDAMNotFoundException:
        current_app.logger.warning('[create_note] EDAMNotFoundException: '
                                   'Invalid notebook GUID (%s).' % note.notebookGuid)
    return note


def update_note(note_store, note):
    try:
        note = note_store.updateNote(note)
    except Errors.EDAMUserException, eue:
        current_app.logger.warning('[update_note] EDAMUserException code: %i, '
                                   'paramter: %s' % (eue.errorCode, eue.parameter))
    except Errors.EDAMNotFoundException:
        current_app.logger.warning('[update_note] EDAMNotFoundException: '
                                   'Invalid notebook or note GUID.')
    return note


def create_or_update_note(note_store, note):
    if note.guid is None:
        return create_note(note_store, note)
    return update_note(note_store, note)


def generate_enml_makeup(book, notes=None):
    notes = notes or book.notes

    makeup = '<?xml version="1.0" encoding="UTF-8"?>'
    makeup += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
    makeup += '<en-note>%s</en-note>'

    makeup_title = '<h2 style="font-size:18pt; text-align:right;">%s</h2>' % book.title
    makeup_author = '<h5 style="font-size:12pt; text-align:right; color:gray;">%s</h5>' % book.author
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

    annotations = OrderedDict()
    for note in notes:
        chapter = note.chapter
        if not chapter:
            chapter = '__DEFAULT__'
        if chapter not in annotations:
            annotations[chapter] = []
        annotations[chapter].append(note)

    makeup_annotations = ''

    for chapter in annotations:
        if chapter != '__DEFAULT__':
            makeup_annotations += makeup_chapter % chapter
        for annotation in annotations[chapter]:
            makeup_annotations += makeup_annotation % (annotation.alt,
                                                       annotation.created.strftime('%Y-%m-%d %H:%M:%S'),
                                                       annotation.content)

    # Be careful with %%
    makeup_main = '<div style="width:90%%; max-width:600px; margin:0px auto;' \
                  'padding:5px; font-size:12pt; font-family:Times">%s%s%s%s</div>' % (makeup_title,
                                                                                      makeup_author,
                                                                                      makeup_annotations,
                                                                                      makeup_footer)

    return makeup % makeup_main


def make_note(book, notes=None, note=None, notebook=None):
    makeup = generate_enml_makeup(book, notes)

    note = note or Types.Note()
    note.title = to_str(book.title)
    note.content = to_str(makeup)
    if note.notebookGuid is None and notebook and hasattr(notebook, 'guid'):
        note.notebookGuid = notebook.guid

    return note
