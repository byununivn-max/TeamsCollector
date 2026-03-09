import json
import glob
import textwrap

# 백필 데이터 폴더 경로
base_path = "/Users/eximtech/TeamsCollector/data/backfill"

# 첫 번째 JSONL 파일을 찾아서 파싱
file_list = glob.glob(f"{base_path}/**/*.jsonl", recursive=True)

if not file_list:
    print("저장된 메시지가 없습니다.")
else:
    sample_file = file_list[0]
    print(f"=== 파일: {sample_file}의 메시지 미리보기 ===")
    
    count = 0
    with open(sample_file, "r", encoding="utf-8") as f:
        for line in f:
            if count >= 5: # 가장 최근 5개 메시지만 출력
                break
            
            msg = json.loads(line)
            
            # 발신자 정보 추출
            from_info = msg.get("from", {})
            user_info = from_info.get("user", {}) if from_info else {}
            sender_name = user_info.get("displayName", "알 수 없음")
            
            # 메시지 내용 추출 (HTML 태그가 포함될 수 있음)
            body = msg.get("body", {})
            content = body.get("content", "(내용 없음)")
            
            # 작성 시간
            created_dt = msg.get("createdDateTime", "")
            
            print(f"\n[{created_dt}] 👤 {sender_name}:")
            # 내용 100자까지만 자르고 줄바꿈 이쁘게 출력
            short_content = textwrap.shorten(content, width=100, placeholder="...")
            print(f"  {short_content}")
            
            count += 1
