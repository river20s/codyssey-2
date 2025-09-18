import http.server
import socketserver
import datetime
import urllib.request
import json

PORT = 8080
HTML_FILE = 'index.html'

def get_location_info(ip_address):
    """
    IP 주소를 기반으로 위치 정보를 조회하는 함수 (보너스 과제)
    """
    # 로컬호스트 주소는 위치 조회를 건너뜁니다.
    if ip_address == '127.0.0.1':
        return 'Localhost'
    
    try:
        # 외부 API를 사용하여 IP 위치 정보 조회
        url = f'http://ip-api.com/json/{ip_address}'
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            if data['status'] == 'success':
                country = data.get('country', 'N/A')
                city = data.get('city', 'N/A')
                region = data.get('regionName', 'N/A')
                return f'{country}, {region}, {city}'
            else:
                return 'Location not found'
    except Exception as e:
        # API 요청 실패 시 오류 메시지 반환
        return f'Could not retrieve location: {e}'


class MyHttpRequestHandler(http.server.BaseHTTPRequestHandler):
    """
    HTTP 요청을 처리하는 커스텀 핸들러 클래스
    """
    def do_GET(self):
        # 1. 서버 콘솔에 접속 정보 출력
        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        client_ip = self.client_address[0]
        location = get_location_info(client_ip)
        
        print(f'접속 시간: {current_time}')
        print(f'클라이언트 IP: {client_ip}')
        print(f'위치 정보: {location}\n')

        try:
            # 2. index.html 파일 읽기
            with open(HTML_FILE, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            # 3. 클라이언트에 200 OK 응답 및 헤더 전송
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # 4. HTML 내용을 인코딩하여 클라이언트에 전송
            self.wfile.write(html_content.encode('utf-8'))

        except FileNotFoundError:
            # ⭐️ [수정된 부분] ⭐️
            # 한글 오류 메시지를 안전하게 전송하기 위해 직접 응답을 구성합니다.
            error_message = '<h1>404 Not Found</h1><p>index.html 파일을 찾을 수 없습니다.</p>'
            
            self.send_response(404)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(error_message.encode('utf-8'))
            print(f'오류: {HTML_FILE} 파일을 찾을 수 없습니다.')


def run_server():
    """
    웹 서버를 실행하는 함수
    """
    # TCPServer를 사용하여指定된 포트와 핸들러로 서버 생성
    with socketserver.TCPServer(('', PORT), MyHttpRequestHandler) as httpd:
        print(f'{PORT} 포트에서 웹 서버가 실행 중입니다...')
        print('브라우저에서 http://127.0.0.1:8080 또는 http://localhost:8080 으로 접속하세요.')
        try:
            # 서버를 계속 실행
            httpd.serve_forever()
        except KeyboardInterrupt:
            # Ctrl+C 입력 시 서버 정상 종료
            print("\n웹 서버를 종료합니다.")
            httpd.server_close()

if __name__ == '__main__':
    run_server()