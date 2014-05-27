# coding=utf-8
from __future__ import unicode_literals
from datetime import datetime
from flask import Blueprint, render_template
from flask import flash, redirect, url_for, abort
from flask.ext.login import current_user, login_required
from everbean.models import Book, Note, UserBook
from everbean.core import db, cache
from everbean.forms import CreateNoteForm, EditNoteForm
from everbean.ext.douban import create_annotation, update_annotation

bp = Blueprint('note', __name__, url_prefix='/note')


@bp.route('/create', defaults={'book_id': 0})
@bp.route('/create/<int:book_id>', methods=("GET", "POST"))
@login_required
def create(book_id):
    @cache.memoize(timeout=300)
    def _user_reading_books(user_id):
        return Book.query.filter(
            Book.user_books.any(
                status='reading',
                user_id=user_id
            )
        ).all()
    books = _user_reading_books(current_user.id)
    book = None
    user_book = None
    if book_id > 0:
        book = Book.query.filter_by(id=book_id).first_or_404()
        user_book = UserBook.query.filter_by(
            user_id=current_user.id,
            book_id=book_id
        ).first()
        if not user_book:
            user_book = UserBook(current_user, book)

    form = CreateNoteForm()
    if book:
        form.book_id.data = book_id
    if form.validate_on_submit():
        note = Note(
            user_id=current_user.id,
            book_id=book_id,
            book=book,
            chapter=form.chapter.data.strip(),
            page_no=form.page_no.data,
            content=form.content.data,
            private=True if form.private.data == 1 else False,
        )
        # TODO: make create annotation async
        note = create_annotation(current_user, note)
        if note and note.douban_id:
            user_book.updated = datetime.now()
            db.session.add(user_book)
            db.session.commit()
            # TODO: sync note to evernote
            flash('撰写笔记成功！', 'success')
            return redirect(url_for('note.create', book_id=book_id))
        else:
            flash('撰写笔记失败！', 'error')

    return render_template('note/create.html',
                           books=books,
                           book=book,
                           form=form)


@bp.route('/<int:note_id>')
def index(note_id):
    note = Note.query.get_or_404(note_id)
    user = note.user
    return render_template('note/index.html',
                           note=note,
                           user=user)


@bp.route('/<int:note_id>/edit')
@login_required
def edit(note_id):
    note = Note.query.get_or_404(note_id)
    if current_user.id != note.user_id:
        abort(403)
    form = EditNoteForm(obj=note)
    if form.validate_on_submit():
        note.chapter = form.chapter.data
        note.page_no = form.page_no.data
        note.content = form.content.data
        note.private = True if form.private.data == 1 else False
        # TODO: Make update annotation async
        note = update_annotation(current_user, note)
        if note:
            flash('编辑笔记成功！', 'success')
            return redirect(url_for('note.index', note_id=note.id))
        else:
            flash('编辑笔记失败！', 'error')
    return render_template('note/edit.html',
                           note=note,
                           form=form)
