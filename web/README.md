# web 디렉토리 설명

## /extension

`Chrome Extension` 소스코드 패키지

열려있는 탭에 대해 다음과 같은 작업들을 수행

* 지정한 위치에 **북마크 생성**
* 내용을 **스크랩하여 서버로 전송**
* **태그 생성 결과** 확인
* ~ 페이지 **링크 버튼**


```html
|-- extension/
|   |
|   |-- background/ # 크롬 드라이버 백그라운드의 동작을 제어
|   |   `-- background.js
|   |
|   |-- css/ # 익스텐션 팝업 레이아웃 설정
|   |   `-- main.css
|   |
|   |-- contentScript.js # 개별 Tab에 대한 접근(Ex. DOM, ...)
|   |-- icon.png
|   |-- icon2.png
|   |-- manifest.json # 익스텐션 configuration
|   |-- popup.html # 익스텐션 클릭 시 나오는 팝업 창 html
|   |-- popup.js # 팝업 창을 제어
|   `-- README.md
`----------------------
```

설치 방법은 **extension 폴더 내의 README.md** 확인 바람

## /myapp

`django`를 사용해 구현된 백엔드 서버

다음과 같은 작업들을 수행 

* Extension을 통해 받아온 **페이지 정보**를 **추론 모델로 전송**
* Extension을 통해 받아온 **유저 정보**를 **추론 결과와 함께 DB에 저장**

서버 구동 관련 자세한 사항은 **myapp 폴더 내의 README.md** 확인 바람

## /ServicePage