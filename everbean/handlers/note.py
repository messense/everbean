# coding=utf-8
from flask import (Blueprint, render_template,
                   flash, redirect, url_for)
from flask.ext.login import current_user, login_required
from everbean.models import Book, Note
from everbean.core import cache
from everbean.forms import CreateNoteForm
from everbean.ext.douban import create_annotation

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
    if book_id > 0:
        book = Book.query.filter_by(id=book_id).first_or_404()

    form = CreateNoteForm()
    if book:
        form.book_id.data = book_id
    if form.validate_on_submit():
        private = False
        if form.private.data == 1:
            private = True
        note = Note(
            user_id=current_user.id,
            book_id=book_id,
            book=book,
            chapter=form.chapter.data.strip(),
            page_no=form.page_no.data,
            content=form.content.data,
            private=private
        )
        note = create_annotation(current_user, note)
        if note and note.douban_id:
            flash(u'撰写笔记成功！', 'success')
            return redirect(url_for('note.create', book_id=book_id))
        else:
            flash(u'撰写笔记失败！', 'error')

    return render_template('note/create.html', books=books, book=book, form=form)



