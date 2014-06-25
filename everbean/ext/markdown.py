# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import re
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from everbean.utils import to_text

_DOUBAN_QUOTE_RE = re.compile('<原文开始>(.*?)</原文结束>', re.S)
_DOUBAN_CODE_RE = re.compile('<代码开始 lang="(.+?)">(.*?)</代码结束>', re.S)
_DOUBAN_IMAGE_RE = re.compile('<图片(\d+)>')


class MarkdownToDoubanRenderer(mistune.Renderer):
    def block_quote(self, text):
        return '<原文开始>\n{text}</原文结束>'.format(text=text)

    def block_code(self, code, lang=None):
        if not lang:
            return code
        code = code.rstrip()
        return '<代码开始 lang="{lang}">\n{code}\n</代码结束>'.format(
            lang=lang,
            code=code
        )

    def image(self, src, title, text):
        return '<{text}>'.format(text=text)

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
        return '{text}\n'.format(text=text)

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


class MarkdownToHTMLRenderer(mistune.Renderer):
    def block_quote(self, text):
        return '<blockquote>{text}\n</blockquote>'.format(text=text)

    def block_code(self, code, lang=None):
        if not lang:
            return '\n<pre><code>{code}</code></pre>\n'.format(code=mistune.escape(code))
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter(noclasses=True)
        text = highlight(code, lexer, formatter)
        return text.replace('class="highlight" ', '')


def markdown_to_douban(text):
    text = to_text(text)
    md = mistune.Markdown(renderer=MarkdownToDoubanRenderer())
    return md.render(text)


def douban_to_markdown(text, images=None):
    def _quote(m):
        # remove leading and trailing newlines
        bq = m.group(1)
        bq = re.sub(r'^\n', '', bq)
        bq = re.sub(r'\n$', '', bq)
        return '> {quote}'.format(quote=bq)

    def _code(m):
        lang = m.group(1)
        code = m.group(2)
        if not code.startswith('\n'):
            code = '\n{code}'.format(code=code)
        if not code.endswith('\n'):
            code = '{code}\n'.format(code=code)
        return '```{lang}{code}```'.format(
            lang=lang,
            code=code
        )

    def _image(m):
        _id = m.group(1)
        if _id in images:
            return '![图片{id}]({url})'.format(
                id=_id,
                url=images[_id]
            )
        else:
            return ''

    text = to_text(text)
    text = _DOUBAN_QUOTE_RE.sub(_quote, text)
    text = _DOUBAN_CODE_RE.sub(_code, text)
    if images:
        text = _DOUBAN_IMAGE_RE.sub(_image, text)
    return text


def markdown_to_html(text):
    md = mistune.Markdown(renderer=MarkdownToHTMLRenderer(), use_xhtml=True)
    return md.render(text)
