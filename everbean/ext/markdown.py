# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import re
from mistune import Renderer, Markdown
from everbean.utils import to_text

_DOUBAN_QUOTE_RE = re.compile('<原文开始>(.*?)</原文结束>', re.S)
_DOUBAN_CODE_RE = re.compile('<代码开始 lang="(.+?)">(.*?)</代码结束>', re.S)
_DOUBAN_IMAGE_RE = re.compile('<图片(\d+)>')


class MarkdownToDoubanRenderer(Renderer):
    def block_quote(self, text):
        return '<原文开始>\n%s</原文结束>' % text

    def block_code(self, code, lang=None):
        if not lang:
            return code
        code = code.rstrip()
        return '<代码开始 lang="%s">\n%s\n</代码结束>' % (lang, code)

    def image(self, src, title, text):
        return '<%s>' % text

    def block_html(self, html):
        return ''

    def header(self, text, level, raw=None):
        return text

    def hrule(self):
        return ''

    def list(self, body, ordered=True):
        return body

    def list_item(self, text):
        return text

    def paragraph(self, text):
        return '%s\n' % text

    def table(self, header, body):
        return ''

    def table_row(self, content):
        return ''

    def table_cell(self, content, **flags):
        return ''

    def double_emphasis(self, text):
        return text

    def emphasis(self, text):
        return text

    def codespan(self, text):
        return text

    def linebreak(self):
        return '\n'

    def strikethrough(self, text):
        return text

    def autolink(self, link, is_email=False):
        return link

    def raw_html(self, html):
        return ''

    def footnote_ref(self, key, index):
        return ''

    def footnote_item(self, key, text):
        return text

    def footnotes(self, text):
        return text


class MarkdownToHTMLRenderer(Renderer):
    def block_quote(self, text):
        return '<blockquote><q>%s\n</q></blockquote>' % text


def markdown_to_douban(text):
    text = to_text(text)
    md = Markdown(renderer=MarkdownToDoubanRenderer())
    return md.render(text)


def douban_to_markdown(text, images=None):
    def _quote(m):
        # remove leading and trailing newlines
        bq = m.group(1)
        bq = re.sub(r'^\n', '', bq)
        bq = re.sub(r'\n$', '', bq)
        return '> %s' % bq

    def _code(m):
        lang = m.group(1)
        code = m.group(2)
        if not code.startswith('\n'):
            code = '\n%s' % code
        if not code.endswith('\n'):
            code = '%s\n' % code
        return '```%s%s```' % (lang, code)

    def _image(m):
        _id = m.group(1)
        return '![图片%s](%s)' % (_id, images[_id])

    text = to_text(text)
    text = _DOUBAN_QUOTE_RE.sub(_quote, text)
    text = _DOUBAN_CODE_RE.sub(_code, text)
    if images:
        text = _DOUBAN_IMAGE_RE.sub(_image, text)
    return text


def markdown_to_html(text):
    md = Markdown(renderer=MarkdownToHTMLRenderer(), use_xhtml=True)
    return md.render(text)
