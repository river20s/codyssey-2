import socket
import threading

def receive_messages(sock):
    """서버로부터 메시지를 수신하여 출력"""
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            if not message:
                print('서버로부터 연결이 종료되었습니다.')
                break
            print(message)
        except:
            break
    sock.close()


def start_client():
    """클라이언트를 시작하고 서버에 연결"""
    host = '127.0.0.1'
    port = 9999

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
    except Exception as e:
        print(f'서버 연결 오류: {e}')
        return

    thread = threading.Thread(target=receive_messages, args=(client_socket,))
    thread.daemon = True
    thread.start()
    
    print('서버에 연결되었습니다. 메시지를 입력하세요.')

    try:
        while True:
            message = input()
            try:
                # 인코딩 오류가 발생해도 프로그램이 충돌하지 않도록 예외 처리
                client_socket.send(message.encode('utf-8'))
            except UnicodeEncodeError:
                print("[SYSTEM] 전송할 수 없는 문자가 포함되어 있습니다.")

    except (KeyboardInterrupt, EOFError):
        print("\n프로그램을 종료합니다.")
    finally:
        client_socket.close()

if __name__ == '__main__':
    start_client()