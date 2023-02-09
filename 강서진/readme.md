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
- 일상 기록 기능
- 일상 기록 수정 기능 

---2023.02.09---
- 건강 기록 기능 
