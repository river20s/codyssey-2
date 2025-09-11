import socket
import threading

# 데드락 방지
clients_lock = threading.RLock()
clients = {}


def broadcast_message(message):
    """현재 접속된 모든 클라이언트에게 메시지를 전송"""
    with clients_lock:
        for client_socket in list(clients.keys()):
            try:
                client_socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f'브로드캐스트 오류: {e}')


def send_private_message(message, sender_nickname, target_nickname):
    """특정 클라이언트에게 귓속말 메시지 전송"""
    with clients_lock:
        target_socket = None
        sender_socket = None

        # 닉네임을 기반으로 송신자와 수신자의 소켓을 찾음
        for sock, nick in clients.items():
            if nick == target_nickname:
                target_socket = sock
            if nick == sender_nickname:
                sender_socket = sock

        formatted_message = f'[귓속말] {sender_nickname}> {message}'

        if target_socket and sender_socket:
            try:
                target_socket.send(formatted_message.encode('utf-8'))
                sender_socket.send(formatted_message.encode('utf-8'))
            except Exception as e:
                print(f'귓속말 전송 오류: {e}')
        elif sender_socket:
            error_message = f"'{target_nickname}'님을 찾을 수 없습니다."
            try:
                sender_socket.send(error_message.encode('utf-8'))
            except Exception as e:
                print(f'오류 메시지 전송 실패: {e}')


def handle_client(client_socket, addr):
    """개별 클라이언트와의 통신 처리"""
    nickname = None
    try:
        client_socket.send('사용할 닉네임을 입력하세요: '.encode('utf-8'))
        nickname = client_socket.recv(1024).decode('utf-8').strip()

        with clients_lock:
            while not nickname or nickname in clients.values():
                client_socket.send('닉네임이 비어있거나 이미 사용 중입니다. 다른 닉네임을 입력하세요: '.encode('utf-8'))
                nickname = client_socket.recv(1024).decode('utf-8').strip()
            clients[client_socket] = nickname

        print(f"'{nickname}'님이 {addr}에서 접속했습니다.")
        broadcast_message(f"'{nickname}'님이 입장하셨습니다.")

        while True:
            message = client_socket.recv(1024).decode('utf-8').strip()
            if not message or message == '/종료':
                break

            # 귓속말 기능 처리
            if message.startswith('/w '):
                parts = message.split(' ', 2)
                if len(parts) == 3:
                    target_nickname, private_msg = parts[1], parts[2]
                    send_private_message(private_msg, nickname, target_nickname)
                else:
                    # 잘못된 형식일 경우, 보낸 사람에게만 안내 메시지 전송
                    client_socket.send(
                        "[SYSTEM] 잘못된 귓속말 형식입니다. (사용법: /w 상대닉네임 메시지)".encode('utf-8')
                    )
            else:
                # 일반 메시지 처리
                formatted_message = f'{nickname}> {message}'
                broadcast_message(formatted_message)

    except Exception as e:
        print(f"클라이언트 '{nickname}' 처리 중 오류: {e}")
    finally:
        with clients_lock:
            if client_socket in clients:
                nickname_to_remove = clients.pop(client_socket)
                exit_message = f"'{nickname_to_remove}'님이 퇴장하셨습니다."
                print(exit_message)
                broadcast_message(exit_message)
        client_socket.close()


def start_server():
    """서버를 시작하고 클라이언트의 접속을 기다림"""
    host = '127.0.0.1'
    port = 9999
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f'서버가 {port} 포트에서 시작되었습니다.')
    except Exception as e:
        print(f'서버 시작 오류: {e}')
        return

    try:
        while True:
            client_socket, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            thread.daemon = True
            thread.start()
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")
    finally:
        server_socket.close()


if __name__ == '__main__':
    start_server()