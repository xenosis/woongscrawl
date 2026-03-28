import json
import os
from pathlib import Path

STATE_FILE = Path(__file__).parent.parent / "data" / "seen_posts.json"


def load_seen_ids(site_name: str) -> set[str]:
    """저장된 게시글 ID 목록을 불러옵니다."""
    if not STATE_FILE.exists():
        return set()
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get(site_name, []))


def save_seen_ids(site_name: str, post_ids: set[str]) -> None:
    """게시글 ID 목록을 저장합니다."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    data[site_name] = list(post_ids)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_initialized(site_name: str) -> bool:
    """해당 사이트가 초기화된 적 있는지 확인합니다."""
    if not STATE_FILE.exists():
        return False
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return site_name in data
