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
- 일상 기록 기능 (열람, 수정, 삭제)
- multipart/form-data 안에 json 함께 전송 -> request.file & request.form으로 받음

---2023.02.09---
- checklist url 구분 작업 목표
- 날짜는 request.header
- 일상 기록 사진을 삭제할 경우 받아야 할 신호같은 게 있어야 할 것 같음

