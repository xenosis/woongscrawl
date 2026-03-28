import os
import requests
from src.crawler import Post


TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")


def send_new_posts(new_posts: list[Post]) -> None:
    """신규 게시글을 텔레그램으로 알림 발송합니다."""
    if not new_posts:
        return

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[알림] TELEGRAM_TOKEN 또는 TELEGRAM_CHAT_ID 환경변수가 설정되지 않았습니다.")
        return

    for post in new_posts:
        message = _format_message(post)
        _send_telegram(message)


def _format_message(post: Post) -> str:
    lines = [
        f"새 게시글 알림",
        f"",
        f"게시판: {post.site_name}",
        f"제목: {post.title}",
    ]
    if post.date:
        lines.append(f"날짜: {post.date}")
    if post.url:
        lines.append(f"링크: {post.url}")
    return "\n".join(lines)


def _send_telegram(text: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print(f"[텔레그램] 발송 완료")
    except requests.RequestException as e:
        print(f"[텔레그램] 발송 실패: {e}")
