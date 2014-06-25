# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import nose
from everbean.ext.markdown import (
    douban_to_markdown,
    markdown_to_douban,
    markdown_to_html
)


def test_douban_to_markdown_quote():
    s = '<原文开始>\nThis is a quote:\nHello World!\n</原文结束>'
    r = douban_to_markdown(s)
    assert r == '> This is a quote:\nHello World!'

    s = '<原文开始>Quote 1</原文结束>\n<原文开始>Quote 2</原文结束>'
    r = douban_to_markdown(s)
    assert r == '> Quote 1\n> Quote 2'


def test_douban_to_markdown_code():
    s = '<代码开始 lang="python">import this</代码结束>'
    r = douban_to_markdown(s)
    assert r == '```python\nimport this\n```'

    s = '<代码开始 lang="python">\nimport this\n</代码结束>'
    r = douban_to_markdown(s)
    assert r == '```python\nimport this\n```'

    s = '<代码开始 lang="python">import this</代码结束>\n' \
        '<代码开始 lang="python">\nimport os\n</代码结束>'
    r = douban_to_markdown(s)
    assert r == '```python\nimport this\n```\n```python\nimport os\n```'


def test_douban_to_markdown_image():
    images = {
        '1': '1.jpg',
        '2': '2.png',
        '3': '3.gif',
    }
    s = '<图片1>'
    r = douban_to_markdown(s)
    assert r == s

    r = douban_to_markdown(s, images)
    assert r == '![图片1](1.jpg)'

    s = '<图片1><图片2>\n<图片3>'
    r = douban_to_markdown(s, images)
    assert r == '![图片1](1.jpg)![图片2](2.png)\n![图片3](3.gif)'

    s = '<图片1><图片4>'
    r = douban_to_markdown(s, images)
    assert r == '![图片1](1.jpg)'


def test_markdown_to_douban_quote():
    expect = '<原文开始>\n{text}\n</原文结束>'
    s = '>test'
    r = markdown_to_douban(s)
    assert r == expect.format(text='test')

    s = ' > test'
    r = markdown_to_douban(s)
    assert r == expect.format(text='test')

    s = ' > test \n> test'
    r = markdown_to_douban(s)
    print(r)
    assert r == expect.format(text='test \ntest')


def test_markdown_to_douban_code():
    expect = '<代码开始 lang="{lang}">\n{code}\n</代码结束>'
    s = '```python\nimport os\n```'
    r = markdown_to_douban(s)
    assert r == expect.format(
        lang='python',
        code='import os'
    )


def test_markdown_to_douban_image():
    expect = '<图片{id}>\n'
    s = '![图片1](1.jpg)'
    r = markdown_to_douban(s)
    print(r)
    assert r == expect.format(id='1')


def test_markdown_to_html_code():
    s = """```python
    from test import pystone
    pystone.main()
    ```
    """
    r = markdown_to_html(s)
    assert "class=" not in r


if __name__ == '__main__':
    nose.runmodule()
