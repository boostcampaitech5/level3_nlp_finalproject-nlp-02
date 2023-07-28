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

`django`를 사용해 구현된 백엔드 서버, `JavaScript`를 사용해 구현된 서비스 페이지

다음과 같은 작업들을 수행 

* Extension을 통해 받아온 `페이지 정보`를 `추론 모델로 전송`
* Extension을 통해 받아온 `유저 정보`를 `추론 결과와 함께 DB에 저장`

서버 구동 관련 자세한 사항은 `myapp 폴더 내의 README.md` 확인 바람

* DB에 저장된 북마크 페이지가 `유저 별로` 서비스 페이지에 표시
* AI 모델에 의해 생성된 태그로 북마크를 `모아보기`할 수 있는 기능 및 북마크 관련 `각종 편의 기능`을 제공하는 `서비스 웹 페이지`

```
| myapp
|-- API
|   |-- admin.py
|   |-- apps.py
|   |-- migrations
|   |   |-- 0001_initial.py
|   |-- models.py
|   |-- templates
|   |   `-- html
|   |-- tests.py
|   |-- urls.py
|   |-- utils.py
|   `-- views.py
|-- README.md
|-- SERVICE
|   |-- __init__.py
|   |-- admin.py
|   |-- apps.py
|   |-- migrations
|   |-- models.py
|   |-- templates
|   |   |-- SERVICE
|   |   |   `-- index.html    # 웹서비스 프론트엔드 HTML 파일
|   |   `-- test_for_search.html
|   |-- tests.py
|   |-- urls.py
|   `-- views.py
|-- db.sqlite3
|-- manage.py
|-- myapp
|   |-- asgi.py
|   |-- settings.py
|   |-- urls.py
|   `-- wsgi.py
`-- static
    |-- css
    |   `-- styles.css   # 웹서비스 프론트엔드 CSS 파일
    |-- image
    |   `-- Logo.png   # 웹서비스 프론트엔드 상단 Logo 파일
    `-- js
        `-- main.js   # 웹서비스 프론트엔드 JavaScript 파일
```        

    


&emsp;     
&emsp;     
&emsp;     
&emsp;     
&emsp;     
&emsp; 