import re
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Optional


@dataclass
class Post:
    post_id: str
    title: str
    date: str
    url: Optional[str]
    site_name: str


def fetch_posts(site: dict) -> list[Post]:
    """사이트 설정을 받아 현재 게시글 목록을 반환합니다."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ko-KR,ko;q=0.9",
    }

    try:
        response = requests.get(site["url"], headers=headers, timeout=15)
        response.raise_for_status()
        response.encoding = "utf-8"
    except requests.RequestException as e:
        print(f"[{site['name']}] 요청 실패: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select(site["row_selector"])

    posts = []
    for row in rows:
        title_el = row.select_one(site["title_selector"])
        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        if not title:
            continue

        post_id = _extract_id(row, title_el, site)
        date = _extract_date(row, site)
        url = _build_url(site, post_id)

        posts.append(Post(
            post_id=post_id,
            title=title,
            date=date,
            url=url,
            site_name=site["name"],
        ))

    return posts


def _extract_id(row, title_el, site: dict) -> str:
    """게시글 고유 ID 추출. data 속성 → id_selector → 제목 해시 순서로 시도."""
    # 1순위: title 요소의 data 속성 (예: data-id="1247830")
    id_attr = site.get("id_data_attr")
    if id_attr:
        val = title_el.get(id_attr, "").strip()
        if val:
            return val

    # 2순위: id_selector로 지정된 셀에서 숫자 추출
    id_selector = site.get("id_selector")
    if id_selector:
        id_el = row.select_one(id_selector)
        if id_el:
            raw = id_el.get_text(strip=True)
            numeric = re.sub(r"\D", "", raw)
            if numeric:
                return numeric

    # 3순위: 제목 기반 해시
    return _hash_title(title_el.get_text(strip=True))


def _extract_date(row, site: dict) -> str:
    """날짜 추출. em 태그 등 레이블 텍스트는 제거."""
    date_selector = site.get("date_selector")
    if not date_selector:
        return ""
    date_el = row.select_one(date_selector)
    if not date_el:
        return ""
    # em.mTit 같은 레이블 태그 제거 후 텍스트만 추출
    for em in date_el.find_all("em"):
        em.decompose()
    return date_el.get_text(strip=True)


def _build_url(site: dict, post_id: str) -> Optional[str]:
    """게시글 상세 URL 조합."""
    base_url = site.get("base_url")
    if not base_url:
        return site["url"]

    # data-id 또는 숫자 ID가 있으면 상세 URL 조합
    if post_id and post_id.isdigit():
        params = site.get("link_params", {})
        param_str = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{base_url}?nttSn={post_id}&{param_str}"

    return site["url"]


def _hash_title(title: str) -> str:
    import hashlib
    return hashlib.md5(title.encode()).hexdigest()[:8]
