02/09 - FEAT:동물등록 기능 추가

문제점: session['userid']로 세션에 저장된 userid를 받아야 하는데, postman에서 keyerror: userid가 떠서 실패
        객체를 받아올 때, db에 등록된 userid를 사용하면 참조키 입력도 성공
