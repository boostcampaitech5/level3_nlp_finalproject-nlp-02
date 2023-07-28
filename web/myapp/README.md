# 서버 구동 방법

# 설치

`django` 명령어를 사용하기 위해 아래처럼 설치

```bash
pip install django
```

# 서버 IP 및 Port 확인

서버 구동을 위해 2가지  정보가 필요함

필요한 정보
- `public server ip`: ai stages에서 서버 정보에 나와있는 IP (ssh 접속을 위한 IP)
- `port`: ai stages에서 서버 정보에 나와있는 port

# Migration

```bash
cd web/myapp
python manage.py makemigrations
python manage.py migrate
```

# 서버 구동

```bash
cd web/myapp # 현재 root 기준
python manager.py runserver 0:{port}
```

그러면 서버가 정상 작동되고 `http://{public server ip}:{port}` 주소로 web 접속 가능
(*https 지원 안 함)

서비스 페이지: `http://{public server ip}:{port}/SEVICE`    
admin 페이지: `http://{public server ip}:{port}/admin`    
서버 구동 후 extention upload
