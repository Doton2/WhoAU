# WhoAU

## 목차
[1. 프로젝트 정보](# -프로젝트 정보)
[2. 프로젝트 소개}(# -프로젝트 소개)
[3. 요구 사항](# -요구 사항)
[4. 사용 설명서](# -사용 설명서)
[5. 의사 결정](# -의사 결정)


###

## 📄 프로젝트 정보

제작기간 
2024.09 ~ 2024.10(4주)

개발자 
김병민

개발목적
Django-Channels를 활용한 실시간 양방향 통신의 설계와 구현에 대한 이해하고, 
이를 통해 Python 프로그래밍 실력을 향상시키는 것을 목표로 했습니다.

기술 스택 
Python, Django, Django Channels, Redis, WebSocket, Celery, HTML, Nginx, Amazon EC2


###


## 📢 프로젝트 소개
WhoAU 누구인지 모른 상대와 램덤으로 말하지 못할 고민과 속사정을 털어 놓는 채팅 웹싸이트 입니다.

혹시 전래동화 ‘임금님 귀는 당나귀 귀’를 아시나요? 
이 이야기에서 이발사는 임금님의 비밀을 알게 되어 심리적 부담을 겪지만, 결국 외딴 곳에서 비밀을 외침으로써 마음의 짐을 덜게 됩니다.

이 프로젝트는 이러한 점에서 영감을 얻어, 누구에게도 말하기 어려운 고민이나 속사정을 무작위로 연결된 익명의 상대에게 
털어놓음으로써 심리적 부담을 덜 수 있는 공간을 제공하고자 합니다.


###


## 💬 요구 사항
1. 누구나 접속할 수 있어야 한다
2. 접속한 사용자는 랜덤하게 매칭된 상대와 채팅할 수 있어야 한다.
3. 상대가 브라우저를 닫거나 일정 시간 동안 채팅이 없을 경우 채팅방은 자동으로 사라져야 한다.


###


## 📕 사용 설명서
1. 연결 상대가 없는 경우
    - 사이트에 접속시,  현재 접속한 상대가 있는지 확인합니다.
    - 연결 상대가 없으면  ‘대화 상대를 기다리고 있습니다.’ 메시지가 표시 되고 ㄴend 버튼이 비활성화 됩니다.
    - **Refresh** 버튼을 클릭하면 새로고침됩니다.
    <details>
    <summary>이미지</summary>
    <div markdown="1">
        <img width="473" alt="스크린샷 2024-11-02 17 04 44" src="https://github.com/user-attachments/assets/14bd0f44-a995-4580-97cc-d414ebc7bf9c">
    </div>
    </details>
2. 연결 상대가 있는 경우 
    - 상대방이 접속하면 **‘대화 상대가 연결되었습니다.’** 메시지가 표시되고, **Send** 버튼이 활성화됩니다.
      <details>
    <summary>이미지</summary>
    <div markdown="1">
        <img width="990" alt="스크린샷 2024-11-02 17 04 10" src="https://github.com/user-attachments/assets/c8a34121-0e17-4728-9f2f-7aacfef4b6c8">
    </div>
    </details>
3. 채팅 화면 
    - 내가 보낸 메시지는 화면의 오른쪽에, 상대방의 메시지는 왼쪽에 표시됩니다.
    - 연결이 유지되는 동안 자유롭게 대화할 수 있습니다.
      <details>
    <summary>이미지</summary>
    <div markdown="1">
        <img width="524" alt="스크린샷 2024-11-02 17 03 17" src="https://github.com/user-attachments/assets/fbaf5d81-f44e-4c6e-aba7-1ccfb053e6c2">
    </div>
    </details>
4. 대화 도중에 나갈 경우
    - 상대방이 연결을 종료하면  ‘상대방과 연결이 끊어졌습니다.’  메시지가 표시 되고, Refresh버튼이 나타납니다.
    - Send 버튼이 비활성화 됩니다.
    - **Refresh** 버튼을 클릭하면 새로 연결할 상대를 찾습니다.
      <details>
    <summary>이미지</summary>
    <div markdown="1">
        <img width="982" alt="스크린샷 2024-11-02 17 04 27" src="https://github.com/user-attachments/assets/a2347e5a-a06a-4bb8-a6db-74bb3829c2d9">
    </div>
    </details>
5. 비활성화 
    - 채팅방의 상태를 지속적으로 확인하며, 비활성화된 방은 자동으로 삭제 됩니다.

  
###


## 🤔 의사 결정

### 1.회원가입이 필요 할까 ?

<details>
<summary>의사 결정 과정</summary>
<div markdown="1">
 
누군지 모르는 상대와 대화를 하는 거라면 회원가입/로그인이 필요 없다고 판단했다.

**해결방안 1 : 임의의 사용자 값 생성**

채팅방에서 서로 통신하기 위해 임의의 사용자 값(UUID)을 부여하는 방식을 고려

*데이터 흐름* 

웹페이지 입장 → 임의의 사용자 값생성 → 접속 중인 다른 사용자 확인→ 랜덤으로 연결 → 채팅 시작 

(접속 유저가 없는 경우 대기)

*문제점* 

 유저들이 접속할 때마다 고유한 값을 관리하고, 다른 유저와의 연결을 처리해야 하는 부담이 있습니다.

**해결 방안 2 : 고유 사용자 정보 없이 간소화**

유저 정보를 따로 관리하지 않고, **같은 채널에 두 명씩 바로 입장시키는 방식**을 선택

- 별도의 사용자 ID 없이도 채팅 가능.
- 접속자가 많거나 적더라도 두 명씩 간단히 매칭.
- 불필요한 사용자 정보 관리를 생략해 구현 부담 감소.
</div>
</details>

### 2.Celery를 통한 주기적인 채팅방 관리

<details>
<summary>의사 결정 과정</summary>
<div markdown="1">
 
Redis 서버에 채팅방이 프로그램 종료 후에도 그대로 존재하는 문제 발생했습니다. 

1. 서버가 강제로 종료된 경우.
2. 비활성화된 채팅방이 삭제되지 않음.

위의 두경에 Redis 서버의 자원이 낭비된다고 판단했다. 

**해결방법 1 : Cache 값을 이용한 채팅방 관리**

1. 채팅방이 생성될 때 Cache에 생성 시간을 저장합니다.
2. 사용자가 메시지를 보낼 때마다 Cache의 시간을 갱신
3. 10분 동안 대화가 없으면 해당 채팅방을 비활성화로 간주하고 삭제

작동 원리 

일정 시간이 지나도 대화가 없다면 자동으로 채팅방에서 나가게 처리하여 비활성화된 방을 정리 했습니다.

*문제점* 

cache의 방법에서는 특정 이벤트가 발생 할 경우에만 동작한다는 문제가 있었습니다.

이러한 문제를 해결하기 위해서는 **주기적으로 코드를 실행하고 관리해주는 비동기 작업 스케줄러**가 필요했다.

**해결방법 2 Celery를 활용한 스케줄러**

 백그라운드에서 자동으로 작업을 실행해 Redis의 채팅방 상태를 지속적으로 점검할 수 있어, 사용자의 이벤트에 의존하지 않고도 불필요한 데이터 삭제가 가능하게 됐다.

[Celery 적용](https://byeongtil.tistory.com/80)

</div>
</details>
