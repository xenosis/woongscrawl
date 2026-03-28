import sys
import yaml
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
from src.crawler import fetch_posts
from src.store import load_seen_ids, save_seen_ids, is_initialized
from src.notifier import send_new_posts


CONFIG_FILE = Path(__file__).parent / "config" / "sites.yaml"


def run(test_mode: bool = False):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    for site in config["sites"]:
        if not site.get("enabled", True):
            continue

        print(f"\n[{site['name']}] 크롤링 시작...")

        current_posts = fetch_posts(site)
        if not current_posts:
            print(f"[{site['name']}] 게시글을 가져오지 못했습니다.")
            continue

        print(f"[{site['name']}] 게시글 {len(current_posts)}개 수집")

        # 테스트 모드: 첫 번째 글을 강제 발송 (seen_posts.json 변경 없음)
        if test_mode:
            print(f"[{site['name']}] [테스트] 첫 번째 게시글로 알림 발송 테스트")
            send_new_posts([current_posts[0]])
            continue

        current_ids = {p.post_id for p in current_posts}
        seen_ids = load_seen_ids(site["name"])

        # 최초 실행: 현재 목록을 저장만 하고 알림은 보내지 않음
        if not is_initialized(site["name"]):
            print(f"[{site['name']}] 최초 실행 - 현재 상태 저장 (알림 없음)")
            save_seen_ids(site["name"], current_ids)
            continue

        # 신규 게시글 = 현재 목록에 있지만 이전에 보지 못한 것
        new_posts = [p for p in current_posts if p.post_id not in seen_ids]

        if new_posts:
            print(f"[{site['name']}] 신규 게시글 {len(new_posts)}개 발견!")
            for p in new_posts:
                print(f"  - [{p.post_id}] {p.title}")
            send_new_posts(new_posts)
        else:
            print(f"[{site['name']}] 신규 게시글 없음")

        # 최신 ID 목록으로 갱신
        save_seen_ids(site["name"], current_ids)


if __name__ == "__main__":
    run(test_mode="--test" in sys.argv)
