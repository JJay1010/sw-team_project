루틴 함수 구현
(1)루틴요일저장:
json 예시
{
   "animal_id":1,
   "date":{
      "mon":"true",
      "tue":"true",
      "wed":"false",
      "thur":"false",
      "fri":"false",
      "sat":"false",
      "sun":"false"
     
      
   },
   "routine_name":"d"
}

이때 true인 요일만 따로 db에 저장

(2)routine_id 는 primarykey로 autoincrement
