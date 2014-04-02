# coding: utf-8
from __future__ import absolute_import
from flask import current_app
from flask.ext.login import current_user
from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors
from everbean.utils import generate_enml_makeup


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


def find_note(note_store, guid, token=None):
    token = token or current_user.evernote_access_token
    try:
        note = note_store.getNote(token, guid, False, False, False, False)
    except (Errors.EDAMUserException, Errors.EDAMNotFoundException):
        current_app.logger.warning('Evernote note %s not found.' % guid)
        return None
    return note


def create_notebook(note_store, name, token=None):
    token = token or current_user.evernote_access_token
    notebook = Types.Notebook()
    notebook.name = name
    try:
        notebook = note_store.createNotebook(token, notebook)
    except Errors.EDAMUserException:
        pass
    return notebook


def get_notebook(note_store, guid=None, name=None, token=None):
    token = token or current_user.evernote_access_token
    try:
        notebook = note_store.getNotebook(token, guid)
    except (Errors.EDAMUserException, Errors.EDAMNotFoundException):
        # create the Notebook
        notebook = create_notebook(note_store, name, token)
    return notebook


def make_note(book, note=None, notebook=None):
    makeup = generate_enml_makeup(book)

    note = note or Types.Note()
    note.title = book['title']
    note.content = makeup
    if note.notebookGuid is None and notebook and hasattr(notebook, 'guid'):
        note.notebookGuid = notebook.guid

    return note


def create_note(note_store, note, token=None):
    token = token or current_user.evernote_access_token
    try:
        note = note_store.createNote(token, note)
    except (Errors.EDAMUserException, Errors.EDAMNotFoundException), e:
        current_app.logger.warning('Create note failed: %s' % e.message)
    return note


def update_note(note_store, note, token=None):
    token = token or current_user.evernote_access_token
    try:
        note = note_store.updateNote(token, note)
    except (Errors.EDAMUserException, Errors.EDAMNotFoundException), e:
        current_app.logger.warning('Update note (Guid: %s) failed: %s' % (note.guid, e.message))
    return note


def create_or_update_note(note_store, note, token=None):
    if note.guid is None:
        return create_note(note_store, note, token)
    return update_note(note_store, note, token)
