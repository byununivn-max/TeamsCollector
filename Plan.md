🎯 현재 진행 상황 (완료된 항목)
✔ Entra ID 앱 등록 완료

앱 이름: TeamsChannelCollector
Application 권한:

ChannelMessage.Read.All
Group.Read.All
Team.ReadBasic.All


관리자 동의(Admin consent) 완료
client_credentials 플로우 정상 작동
→ 전사 Teams 채널 메시지 조회 가능 상태

✔ Mac Studio 기반 Graph API 테스트 성공

Python venv 생성
.env 구성 완료
test_collect.py 실행 성공

Teams 74개 확인
특정 채널 메시지가 연속적으로 정상 출력됨
→ Graph API 호출 경로 100% 정상



✔ 전체 파이프라인 설계 완료

common.py
backfill.py (전사 백필)
sync_state.py (delta 저장)
incremental.py (증분 수집)
NAS 저장 구조 및 jsonl 포맷 설계 완료


3) 요청하신 “상기 내용을 Markdown으로” 정리 (최종 버전)
아래 전체를 그대로 복사해서 노션/Confluence/Docs에 붙여넣기 하시면 됩니다.

📄 Teams 채널 메시지 RAW 수집 파이프라인 (Graph API + Mac Studio + NAS)
1. 개요
이 문서의 목적은:

Microsoft Teams 채널 메시지 전체를
Mac Studio + Graph API + NAS 조합으로
RAW(jsonl) 형태로 백업·증분 수집하는 데이터 파이프라인 구축

을 위한 설계 및 코드 구조를 정의하는 것입니다.

2. 시스템 구성 요소
✔ 2.1 Entra ID App (Application permissions)

항목값앱 이름TeamsChannelCollector권한 모델Application (app-only)Graph 권한ChannelMessage.Read.All, Group.Read.All, Team.ReadBasic.All관리자 동의완료인증 방식client_credentials



























항목값앱 이름TeamsChannelCollector권한 모델Application (app-only)Graph 권한ChannelMessage.Read.All, Group.Read.All, Team.ReadBasic.All관리자 동의완료인증 방식client_credentials

3. Mac Studio 환경
디렉터리 구조
Plain Text~/teams_collector/  venv/  .env  common.py  backfill.py  incremental.py  sync_state.py  sync_state.db  data/                     # → 이후 NAS 마운트 경로로 변경    backfill/    incremental/더 많은 선 표시
.env 구성
Plain Textdotenv 완전히 지원되지 않습니다. 구문 강조 표시는 Plain Text 기반합니다.TENANT_ID=<Directory ID>CLIENT_ID=<Application ID>CLIENT_SECRET=<Client Secret>BASE_DIR=/Users/eximtech/teams_collector/data더 많은 선 표시
venv 생성
Shellcd ~/teams_collectorpython3 -m venv venvsource venv/bin/activatepip install requests python-dotenv더 많은 선 표시

4. 테스트 코드 (test_collect.py)
→ 전사 Teams/채널/메시지 조회까지 성공했음.
출력 예:
Teams 개수: 74
테스트 팀: Legal 4df1a2ef-...
채널 개수: 1
테스트 채널: General ...
<메시지ID> 2023-07-23T17:30:06Z
...


5. Full Backfill (backfill.py)

전사 Teams 목록 조회
모든 채널 조회
모든 메시지 페이지네이션 수집
NAS에 jsonl 저장


6. Incremental Delta Sync (incremental.py)

deltaLink 기반 증분 메시지 수집
SQLite(sync_state.db)에 채널별 deltaLink 저장
날짜별 incremental 파일 생성


7. NAS 구조
Plain Text<NAS>/TeamsRaw/  backfill/    team_<id>/channel_<id>.jsonl  incremental/    team_<id>/channel_<id>_YYYYMMDD.jsonl더 많은 선 표시

8. 향후 확장

Azure SQL 또는 온프레 DB로 정규화
Azure Cognitive Search 인덱스 구축
Azure OpenAI 또는 자체 LLM 기반 RAG 검색
Copilot Studio Agent 제작 가능


요약

IDE 안에서 저를 직접 실행하는 것은 불가능
그러나 VS Code + GitHub Copilot 조합이 사실상 동일한 개발 경험 제공
현재 컨텍스트는
→ Teams RAW 파이프라인의 핵심 구조가 모두 준비된 완전 정상 상태
Markdown 문서는 그대로 저장해도 되는 품질로 정리 완료


대표님, 다음 단계로 어떤 걸 진행하고 싶으신가요?

NAS 마운트 경로 설계
백필 스크립트 실제 실행 플랜
JSONL → DB 변환 스크립트
Azure Search 인덱스 설계
전체 파이프라인 운영 체계 설계