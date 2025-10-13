'''KBS 헤드라인 뉴스를 표준 라이브러리와 requests만으로 수집합니다.

요구사항 준수:
- 외부 패키지는 사용하지 않고 `requests`만 사용
- 헤드라인 텍스트를 List로 수집 후 출력
- PEP 8 스타일 및 한글 기본 홑따옴표 사용

안정성 전략:
1) 홈페이지의 JSON-LD(구조화 데이터)에서 headline 추출
2) HTML 내 제목 성격의 태그(h1/h2/h3/strong 등) 휴리스틱 추출
3) 부족할 경우 RSS 피드로 보강

실행: 
- python codyssey-2/WEEK03/crawling_KBS.py
- 네트워크 연결이 가능하면 1~20개의 헤드라인이 번호와 함께 출력됨

참고:
- 윈도우 콘솔에서 한글이 깨질 경우, `chcp 65001` 명령으로 UTF-8 모드로 변경
'''

from collections import OrderedDict
from html.parser import HTMLParser
import json
import re
from typing import Iterable, List
import xml.etree.ElementTree as ET

import requests


class ScriptCollector(HTMLParser):
    '''<script type="application/ld+json"> 블록을 수집하는 파서'''

    def __init__(self) -> None:
        super().__init__()
        self._in_jsonld = False
        self._buffer: List[str] = []
        self.snippets: List[str] = []

    def handle_starttag(self, tag: str, attrs: Iterable) -> None:
        if tag.lower() == 'script':
            attr_dict = {k.lower(): v for k, v in attrs}
            if attr_dict.get('type', '').lower() == 'application/ld+json':
                self._in_jsonld = True
                self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == 'script' and self._in_jsonld:
            snippet = ''.join(self._buffer).strip()
            if snippet:
                self.snippets.append(snippet)
        self._in_jsonld = False

    def handle_data(self, data: str) -> None:
        if self._in_jsonld:
            self._buffer.append(data)


class HeadlineTagCollector(HTMLParser):
    '''제목 성격의 태그에서 텍스트를 수집하는 파서'''

    title_tags = {'h1', 'h2', 'h3', 'strong', 'p', 'a'}

    def __init__(self) -> None:
        super().__init__()
        self._stack: List[dict] = []
        self._buffer: List[str] = []
        self.candidates: List[str] = []
        self._article_link_depth: int = 0

    @staticmethod
    def _looks_like_title(attrs: dict) -> bool:
        cls = attrs.get('class', '')
        aria_label = attrs.get('aria-label', '')
        id_attr = attrs.get('id', '')
        hay = ' '.join([cls, aria_label, id_attr]).lower()
        keys = ['headline', 'head', 'title', 'tit', 'news', 'top', 'main']
        return any(key in hay for key in keys)

    def handle_starttag(self, tag: str, attrs: Iterable) -> None:
        tag = tag.lower()
        attr_dict = {k.lower(): v for k, v in attrs}
        # Track when inside an article link
        if tag == 'a':
            href = (attr_dict.get('href') or '').lower()
            if re.search(r"/news/(pc/)?view/?.*\.do|/news/view\.do", href):
                self._article_link_depth += 1

        capture = (
            tag in self.title_tags
            and self._looks_like_title(attr_dict)
            and (self._article_link_depth > 0)
        )
        self._stack.append({'tag': tag, 'capture': capture})
        if capture:
            self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        if not self._stack:
            if tag.lower() == 'a' and self._article_link_depth > 0:
                self._article_link_depth -= 1
            return
        top = self._stack.pop()
        if top.get('capture'):
            text = ''.join(self._buffer).strip()
            text = re.sub(r'\s+', ' ', text)
            if text:
                self.candidates.append(text)
            self._buffer = []
        if tag.lower() == 'a' and self._article_link_depth > 0:
            self._article_link_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._stack and self._stack[-1].get('capture'):
            self._buffer.append(data)


def _request(url: str, timeout: int = 10) -> requests.Response:
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/124.0.0.0 Safari/537.36'
        )
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp


def _extract_from_jsonld(html: str) -> List[str]:
    parser = ScriptCollector()
    parser.feed(html)
    headlines: List[str] = []

    def add_headline(value: str) -> None:
        value = (value or '').strip()
        if value:
            headlines.append(value)

    for raw in parser.snippets:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            matches = re.findall(r'\{.*?\}', raw, flags=re.S)
            for m in matches:
                try:
                    obj = json.loads(m)
                except json.JSONDecodeError:
                    continue
                _collect_headlines_from_json(obj, add_headline)
            continue
        _collect_headlines_from_json(data, add_headline)

    return headlines


def _collect_headlines_from_json(data, add_headline) -> None:
    if isinstance(data, dict):
        if data.get('@type') in {'NewsArticle', 'Article'} and 'headline' in data:
            add_headline(str(data.get('headline')))
        if data.get('@type') in {'ItemList', 'CollectionPage'}:
            items = data.get('itemListElement') or data.get('hasPart') or []
            for item in items:
                _collect_headlines_from_json(item, add_headline)
        graph = data.get('@graph')
        if isinstance(graph, list):
            for node in graph:
                _collect_headlines_from_json(node, add_headline)
        for key in ('mainEntity', 'item', 'news'):
            if key in data:
                _collect_headlines_from_json(data[key], add_headline)
    elif isinstance(data, list):
        for node in data:
            _collect_headlines_from_json(node, add_headline)


def _extract_from_html_tags(html: str) -> List[str]:
    parser = HeadlineTagCollector()
    parser.feed(html)
    texts = [t for t in parser.candidates if len(t) >= 8]
    return texts


def _extract_from_rss(xml_text: str) -> List[str]:
    titles: List[str] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return titles
    for item in root.iter():
        if item.tag.lower().endswith('title') and item.text:
            titles.append(item.text.strip())
    if titles and len(titles[0]) < 10:
        titles = titles[1:]
    return titles


def get_kbs_headlines() -> List[str]:
    '''KBS 헤드라인 문자열 리스트를 반환'''
    candidates: List[str] = []

    homepage_urls = [
        'https://news.kbs.co.kr/news/pc/main/main.html',
        'https://news.kbs.co.kr/news/mobile/main/main.html',
        'https://news.kbs.co.kr',
        'http://news.kbs.co.kr',
    ]
    for url in homepage_urls:
        try:
            resp = _request(url)
        except requests.RequestException:
            continue
        html = resp.text
        candidates.extend(_extract_from_jsonld(html))
        if len(candidates) < 5:
            candidates.extend(_extract_from_html_tags(html))
        if candidates:
            break

    if len(candidates) < 3:
        rss_urls = [
            # Known sitemap feeds (stable fallback)
            'https://news.kbs.co.kr/sitemap/recentNewsList.xml',
            'https://news.kbs.co.kr/sitemap/dailyNewsList.xml',
        ]
        for url in rss_urls:
            try:
                resp = _request(url)
            except requests.RequestException:
                continue
            candidates.extend(_extract_from_rss(resp.text))
            if candidates:
                break

    seen = OrderedDict()
    for title in candidates:
        title = re.sub(r'\s+', ' ', (title or '').strip())
        if not title:
            continue
        if '|' in title:
            parts = [p.strip() for p in title.split('|')]
            if parts and len(parts[0]) >= 8:
                title = parts[0]
        seen[title] = None

    return list(seen.keys())[:20]


def _print_headlines(titles: List[str]) -> None:
    if titles:
        print('--- KBS 주요 헤드라인 뉴스 ---')
        for i, title in enumerate(titles, 1):
            print(f'{i}. {title}')
    else:
        print('헤드라인 뉴스를 가져오지 못했습니다.')


if __name__ == '__main__':
    _print_headlines(get_kbs_headlines())
