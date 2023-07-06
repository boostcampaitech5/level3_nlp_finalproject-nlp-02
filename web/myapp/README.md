# 서버 구동 방법

# 설치

`django`와 `ifconfig` 명령어를 사용하기 위해 아래처럼 설치

```bash
pip install django
apt install net-tools
```

# 서버 IP 및 Port 확인

서버 구동을 위해 3가지  정보가 필요함

필요한 정보
- `public server ip`: ai stages에서 서버 정보에 나와있는 IP (ssh 접속을 위한 IP)
- `private server ip`: `ifconfig`를 통해 얻은 서버 IP
  - 터미널에서 `ifconfig` 입력하면 네트워크 정보가 출력되는데 맨 위에 `inet xxx.xxx.xxx.xxx` 부분이 `private server ip`임
- `port`: ai stages에서 서버 정보에 나와있는 port

# 서버 구동

```bash
cd web/myapp # 현재 root 기준
python manager.py runserver {private server ip}:{port}
```

그러면 서버가 정상 작동되고 `http://{public server ip}:{port}` 주소로 web 접속 가능
(*https 지원 안 함)
