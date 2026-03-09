import os
import json
import argparse
from pathlib import Path

# Standalone configuration reading to avoid depending on 'requests' or 'dotenv'
BASE_DIR = Path("./data")
if Path(".env").exists():
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("BASE_DIR="):
                val = line.split("=", 1)[1].strip()
                # Remove quotes if present
                if val and (val.startswith('"') or val.startswith("'")) and (val.endswith('"') or val.endswith("'")):
                    val = val[1:-1]
                BASE_DIR = Path(val)
                break

def get_dir_size(path: Path) -> int:
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def format_size(size: float) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def get_stats() -> dict:
    """진행 상황을 계산하여 반환하는 함수. UI 백엔드에서 import하여 사용할 수 있습니다."""
    backfill_dir = BASE_DIR / "backfill"
    
    if not backfill_dir.exists():
        return {
            "status": "error",
            "message": f"Directory not found: {backfill_dir}",
            "dir_path": str(backfill_dir)
        }

    total_size_bytes = get_dir_size(backfill_dir)
    file_count: int = 0
    line_count: int = 0

    for path in backfill_dir.rglob('*.jsonl'):
        if path.is_file():
            file_count += 1
            # 바이트(rb) 모드로 읽어서 줄 수를 세는 것이 더 빠름
            with open(path, 'rb') as f:
                line_count += sum(1 for _ in f)

    return {
        "status": "success",
        "dir_path": str(backfill_dir),
        "total_size_bytes": total_size_bytes,
        "total_size_formatted": format_size(float(total_size_bytes)),
        "total_files": file_count,
        "total_messages": line_count
    }

def main():
    parser = argparse.ArgumentParser(description="Check TeamsCollector syncing progress")
    parser.add_argument("--json", action="store_true", help="Output in JSON format for UI integration")
    args = parser.parse_args()

    stats = get_stats()

    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        if stats["status"] == "error":
            print(f"[{stats['status'].upper()}] {stats['message']}")
            return
            
        print("📊 TeamsCollector 백필(Backfill) 진행 상황 📊")
        print("-" * 45)
        print(f"📁 저장 경로     : {stats['dir_path']}")
        print(f"💾 전체 용량     : {stats['total_size_formatted']}")
        print(f"📄 채널(파일) 수 : {stats['total_files']:,} 개")
        print(f"💬 총 메시지 수  : {stats['total_messages']:,} 라인")
        print("-" * 45)

if __name__ == "__main__":
    main()
