---2023.02.01~05---
- checklist 기능 구현

---2023.02.06---
- app.py에서 checklist와 update로 구분하였음, Blueprint 사용. 구동은 checklist.py
- routine과 합쳤을 때 기능 돌아가는 것 확인.
- 일상/건강기록기능 Journal, Health model 생성 (models.py)
- dict_to_json 함수 &, update로 redirect 수정 (에러)

---2023.02.07---
- checklist-update redirect 오류 수정
- aws s3 테스트용으로 공개 버킷 cosmosaurtest 생성 - iam 사용자 생성, amazons3fullaccess 
- 폼으로 이미지 받아 로컬에 저장 - 해당 이미지 s3에 업로드 - 이미지 링크 가져와서 출력 되는 것 확인. 
- 일상 기록 기능 구현
- login과 합치기

