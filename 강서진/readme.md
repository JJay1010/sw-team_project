---2023.02.01~05---
- checklist 기능 

---2023.02.06---
- app.py에서 checklist와 update로 구분하였음, Blueprint 사용. 구동은 checklist.py
- routine과 합쳤을 때 기능 돌아가는 것 확인.
- 일상/건강기록기능 Journal, Health model 생성 (models.py)
- dict_to_json 함수 &, update로 redirect 수정 (에러)

---2023.02.07---
- checklist-update redirect 오류 수정
- aws s3 테스트용으로 공개 버킷 cosmosaurtest 생성 - iam 사용자 생성, amazons3fullaccess 
- 일상 기록 --> 따로는 저장이 되는데 이미지랑 기록 한 번에 전송하면 오류

---2023.02.08---
- 일상 기록 기능 (조회, 수정, 삭제)
- multipart/form-data 안에 json 함께 전송 -> request.file & request.form으로 받음

---2023.02.09---
- 일상기록 기능 오류 수정 (['_sa_instance_state'])
- checklist 함수 제거, update.py와 합침
- get에 필요한 정보는 request.header
- 일상 기록 사진을 삭제할 경우 받을 정보 필요
- health 테이블 title -> content 

---2023.02.10---
- models.py 수정 (외래키 참조 관계 사용)
- 로그인, 루틴, 체크리스트, 일상기록 기능 blueprint로 연결 (루틴 수정 필요)

---2023.02.11---
- db model 수정에 맞춰 checklist, journal 외래키 참조 수정.
- routine 테이블에 index(기본키)와 routine_id 구분(앱 알람 id), checklist_routine 외래키 수정 (pet_test.db)
- health 테이블에 개/고양이 구분, 환부 칼럼 추가 (건강 기록 생성 시 문자열로 받음)
- 동물 정보 조회/수정, 동물 프로필 이미지 업로드/수정 기능 추가 (authentification.register_animal / pet.py)
- 건강 기록 기능 (health.py) 목록, 조회, 삭제 구현(수정 기능은 x) (생성은 인공지능 모델 전달받은 후 구현, lazy loading 등에 대한 공부 필요)
- session['login'] 요청 구분 ?
- 시간이 되면 주말동안 ngrok 으로 백, 프론트 연결
