# coding=utf-8
from __future__ import absolute_import
from datetime import datetime
from collections import OrderedDict
from flask import render_template, current_app as app
from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors
from everbean.utils import to_str


def get_service_host(is_i18n=True):
    if app.config['EVERNOTE_SANDBOX']:
        return 'sandbox.evernote.com'
    if is_i18n:
        return 'wwww.evernote.com'
    else:
        return 'app.yinxiang.com'


def get_evernote_client(is_i18n=True, token=None):
    if token:
        client = EvernoteClient(
            token=token,
            sandbox=app.config['EVERNOTE_SANDBOX'],
            service_host=get_service_host(is_i18n)
        )
    else:
        consumer_key = 'EVERNOTE_CONSUMER_KEY'
        consumer_secret = 'EVERNOTE_CONSUMER_SECRET'
        client = EvernoteClient(
            consumer_key=app.config[consumer_key],
            consumer_secret=app.config[consumer_secret],
            sandbox=app.config['EVERNOTE_SANDBOX'],
            service_host=get_service_host(is_i18n)
        )
    return client


def find_note(note_store, guid):
    note = None
    try:
        note = note_store.getNote(guid, False, False, False, False)
    except Errors.EDAMUserException, eue:
        app.logger.warning(
            '[find_note] EDAMUserException code: %i, '
            'paramter: %s' % (eue.errorCode, eue.parameter)
        )
    except Errors.EDAMNotFoundException:
        app.logger.warning(
            '[find_note] EDAMNotFoundException: '
            'Invalid note GUID (%s).' % guid
        )
    return note


def get_notebooks(note_store):
    notebooks = []
    try:
        notebooks = note_store.listNotebooks()
    except Errors.EDAMUserException, eue:
        app.logger.warning(
            '[get_notebooks] EDAMUserException code: %i, '
            'paramter: %s' % (eue.errorCode, eue.parameter)
        )
    return notebooks


def create_notebook(note_store, name):
    notebook = Types.Notebook()
    if name is None:
        return notebook
    notebook.name = to_str(name)
    try:
        notebook = note_store.createNotebook(notebook)
    except Errors.EDAMUserException, eue:
        app.logger.warning(
            '[create_notebook] EDAMUserException code: %i, '
            'paramter: %s' % (eue.errorCode, eue.parameter)
        )
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
        app.logger.warning(
            '[get_notebook] EDAMUserException code: %i, '
            'paramter: %s' % (eue.errorCode, eue.parameter)
        )
        error = True
    except Errors.EDAMNotFoundException:
        app.logger.warning(
            '[get_notebook] EDAMNotFoundException: '
            'Invalid notebook GUID (%s).' % guid
        )
        error = True
    if error:
        # create the Notebook
        notebook = create_notebook(note_store, name)
    return notebook


def create_note(note_store, note):
    try:
        note = note_store.createNote(note)
    except Errors.EDAMUserException, eue:
        app.logger.warning(
            '[create_note] EDAMUserException code: %i, '
            'paramter: %s' % (eue.errorCode, eue.parameter)
        )
    except Errors.EDAMNotFoundException:
        app.logger.warning(
            '[create_note] EDAMNotFoundException: '
            'Invalid notebook GUID (%s).' % note.notebookGuid
        )
    return note


def update_note(note_store, note):
    try:
        note = note_store.updateNote(note)
    except Errors.EDAMUserException, eue:
        app.logger.warning(
            '[update_note] EDAMUserException code: %i, '
            'paramter: %s' % (eue.errorCode, eue.parameter)
        )
    except Errors.EDAMNotFoundException:
        app.logger.warning(
            '[update_note] EDAMNotFoundException: '
            'Invalid notebook or note GUID.'
        )
    return note


def create_or_update_note(note_store, note):
    if note.guid is None:
        return create_note(note_store, note)
    return update_note(note_store, note)


def generate_enml_makeup(book, notes=None, template='default'):
    notes = notes or book.notes
    template = 'evernote/%s.xml' % template
    annotations = OrderedDict()
    for note in notes:
        chapter = note.chapter
        if not chapter:
            chapter = '__DEFAULT__'
        if chapter not in annotations:
            annotations[chapter] = []
        annotations[chapter].append(note)

    return render_template(template,
                           book=book,
                           notes=annotations,
                           created=datetime.now())


def make_note(book, notes=None, note=None,
              notebook=None, template='default'):
    makeup = generate_enml_makeup(book, notes, template)

    note = note or Types.Note()
    note.title = to_str(book.title)
    note.content = to_str(makeup)
    if note.notebookGuid is None and \
            notebook and hasattr(notebook, 'guid'):
        note.notebookGuid = notebook.guid

    return note
