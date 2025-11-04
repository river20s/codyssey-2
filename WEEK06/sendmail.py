'''Gmail SMTP 프로토콜을 이용하여 HTML 이메일 발송 및 CSV 파일에서 수신자 목록 관리

주요 기능:
    - Gmail SMTP를 통한 HTML 이메일 발송
    - CSV 파일에서 수신자 목록 읽기
    - TLS 보안 연결 (포트 587)
    - 예외 처리 및 오류 메시지
    - 두 가지 메일 발송 방법 (일괄 발송 vs 개별 발송)

SMTP 프로토콜 정보:
    - 서버: smtp.gmail.com
    - 포트: 587 (TLS)
    - 보안: STARTTLS

Gmail 설정 방법:
    1. 2단계 인증 활성화
    2. Google 계정 > 보안 > 앱 비밀번호 생성
    3. 생성된 16자리 비밀번호를 프로그램에서 사용

사용 방법:
    1. mail_target_list.csv 파일에 수신자 목록 작성
       형식: 이름,이메일
       예시: 김철수,chulsoo.kim@example.com

    2. 프로그램 실행
       python sendmail.py

    3. 순서대로 입력
       - 보내는 사람 Gmail 주소
       - Gmail 비밀번호 (또는 앱 비밀번호)
       - 메일 제목
       - 샘플 HTML 본문 사용 여부 (y/n)
       - 메일 발송 방법 선택
         1: 일괄 발송 (빠름, 모든 수신자가 서로의 이메일 주소를 볼 수 있음)
         2: 개별 발송 (느림, 각 수신자는 자신의 이메일만 보임, 개인화 가능)

두 가지 메일 발송 방법 비교:
    방법 1 (일괄 발송):
        장점: 빠르고 효율적 (SMTP 연결 1회)
        단점: 모든 수신자가 서로의 이메일 주소를 볼 수 있음
        권장 사용: 공지사항, 단체 메일

    방법 2 (개별 발송):
        장점: 각 수신자는 자신의 이메일만 보임 (개인정보 보호)
              이름을 이용한 개인화 가능 ({name} 태그 사용)
              각 수신자별 발송 성공/실패 추적 가능
        단점: 느림 (각 수신자마다 별도 발송)
        권장 사용: 개인화된 메일, 마케팅 메일

권장 방법: 방법 2 (개별 발송)
    - 개인정보 보호가 중요
    - 개인화 기능 활용 가능
    - SMTP 연결을 재사용하여 속도 최적화
'''

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import os


def read_mail_list(csv_file_path):
    '''
    CSV 파일에서 메일 수신자 목록을 읽어오는 함수

    Args:
        csv_file_path (str): CSV 파일 경로

    Returns:
        list: 수신자 정보 리스트 [{'name': '이름', 'email': '이메일'}, ...]
        None: 파일을 읽을 수 없는 경우
    '''
    try:
        recipients = []

        # CSV 파일 읽기
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            # csv.DictReader: CSV 파일을 딕셔너리 형태로 읽어옴
            # 첫 번째 행을 자동으로 헤더로 인식
            reader = csv.DictReader(file)

            for row in reader:
                # 각 행에서 이름과 이메일 추출
                name = row.get('이름', '').strip()
                email = row.get('이메일', '').strip()

                # 이메일이 유효한 경우만 추가
                if email and '@' in email:
                    recipients.append({
                        'name': name,
                        'email': email
                    })

        return recipients

    except FileNotFoundError:
        print(f'오류: CSV 파일을 찾을 수 없습니다 - {csv_file_path}')
        return None

    except Exception as e:
        print(f'오류: CSV 파일을 읽는 중 오류가 발생했습니다 - {str(e)}')
        return None


def create_html_message(subject, html_content, sender_email, receiver_emails):
    '''
    HTML 형식의 이메일 메시지를 생성하는 함수

    Args:
        subject (str): 메일 제목
        html_content (str): HTML 형식의 메일 본문
        sender_email (str): 보내는 사람의 이메일 주소
        receiver_emails (list or str): 받는 사람의 이메일 주소 (리스트 또는 단일 문자열)

    Returns:
        MIMEMultipart: 생성된 MIME 메시지 객체
    '''
    # MIME 메시지 생성
    message = MIMEMultipart('alternative')
    message['From'] = sender_email

    # 받는 사람이 리스트인 경우 콤마로 연결
    if isinstance(receiver_emails, list):
        message['To'] = ', '.join(receiver_emails)
    else:
        message['To'] = receiver_emails

    message['Subject'] = subject

    # HTML 본문 추가
    # MIMEText의 두 번째 인자를 'html'로 설정하여 HTML 형식 지정
    html_part = MIMEText(html_content, 'html')
    message.attach(html_part)

    return message


def send_email_bulk(sender_email, sender_password, receiver_emails, subject, html_content):
    '''
    여러 명에게 한 번에 이메일을 발송하는 함수 (방법 1: 일괄 발송)

    장점: 빠르고 효율적 (SMTP 연결 1회)
    단점: 받는 사람이 다른 수신자들의 이메일 주소를 볼 수 있음

    Args:
        sender_email (str): 보내는 사람의 Gmail 주소
        sender_password (str): 보내는 사람의 Gmail 앱 비밀번호
        receiver_emails (list): 받는 사람들의 이메일 주소 리스트
        subject (str): 메일 제목
        html_content (str): HTML 형식의 메일 본문

    Returns:
        bool: 메일 발송 성공 여부
    '''
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    try:
        # HTML 메시지 생성
        message = create_html_message(subject, html_content, sender_email, receiver_emails)

        # SMTP 서버에 연결
        print(f'SMTP 서버에 연결 중... ({smtp_server}:{smtp_port})')
        server = smtplib.SMTP(smtp_server, smtp_port)

        # TLS 보안 연결
        server.starttls()
        print('TLS 보안 연결이 설정되었습니다.')

        # 로그인
        print('Gmail 계정으로 로그인 중...')
        server.login(sender_email, sender_password)
        print('로그인 성공!')

        # 메일 발송
        text = message.as_string()
        server.sendmail(sender_email, receiver_emails, text)
        print(f'메일이 성공적으로 발송되었습니다: {len(receiver_emails)}명')

        # 연결 종료
        server.quit()
        print('SMTP 서버 연결이 종료되었습니다.')

        return True

    except smtplib.SMTPAuthenticationError:
        print('오류: 인증 실패. 이메일 주소 또는 비밀번호를 확인해주세요.')
        print('Gmail의 경우 2단계 인증을 사용하는 경우 앱 비밀번호를 생성해야 합니다.')
        return False

    except smtplib.SMTPConnectError:
        print('오류: SMTP 서버 연결 실패. 네트워크 연결을 확인해주세요.')
        return False

    except smtplib.SMTPServerDisconnected:
        print('오류: SMTP 서버와의 연결이 끊어졌습니다.')
        return False

    except smtplib.SMTPException as e:
        print(f'오류: SMTP 오류가 발생했습니다 - {str(e)}')
        return False

    except Exception as e:
        print(f'오류: 예상치 못한 오류가 발생했습니다 - {str(e)}')
        return False


def send_email_individual(sender_email, sender_password, recipients, subject, html_content):
    '''
    여러 명에게 개별적으로 이메일을 발송하는 함수 (방법 2: 개별 발송)

    장점: 각 수신자는 자신의 이메일만 보임 (개인정보 보호)
    단점: 느림 (각 수신자마다 별도 발송)

    Args:
        sender_email (str): 보내는 사람의 Gmail 주소
        sender_password (str): 보내는 사람의 Gmail 앱 비밀번호
        recipients (list): 수신자 정보 리스트 [{'name': '이름', 'email': '이메일'}, ...]
        subject (str): 메일 제목
        html_content (str): HTML 형식의 메일 본문

    Returns:
        tuple: (성공 횟수, 실패 횟수)
    '''
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    success_count = 0
    fail_count = 0

    try:
        # SMTP 서버에 한 번만 연결
        print(f'SMTP 서버에 연결 중... ({smtp_server}:{smtp_port})')
        server = smtplib.SMTP(smtp_server, smtp_port)

        # TLS 보안 연결
        server.starttls()
        print('TLS 보안 연결이 설정되었습니다.')

        # 로그인
        print('Gmail 계정으로 로그인 중...')
        server.login(sender_email, sender_password)
        print('로그인 성공!')
        print()

        # 각 수신자에게 개별적으로 메일 발송
        for recipient in recipients:
            try:
                name = recipient['name']
                email = recipient['email']

                # 개인화된 HTML 메시지 생성
                # 수신자 이름으로 인사말 개인화 가능
                personalized_content = html_content.replace('{name}', name)

                # HTML 메시지 생성
                message = create_html_message(subject, personalized_content, sender_email, email)

                # 메일 발송
                text = message.as_string()
                server.sendmail(sender_email, email, text)
                print(f'✓ 메일 발송 성공: {name} ({email})')
                success_count += 1

            except Exception as e:
                print(f'✗ 메일 발송 실패: {name} ({email}) - {str(e)}')
                fail_count += 1

        # 연결 종료
        server.quit()
        print()
        print('SMTP 서버 연결이 종료되었습니다.')

        return (success_count, fail_count)

    except smtplib.SMTPAuthenticationError:
        print('오류: 인증 실패. 이메일 주소 또는 비밀번호를 확인해주세요.')
        print('Gmail의 경우 2단계 인증을 사용하는 경우 앱 비밀번호를 생성해야 합니다.')
        return (success_count, fail_count)

    except smtplib.SMTPConnectError:
        print('오류: SMTP 서버 연결 실패. 네트워크 연결을 확인해주세요.')
        return (success_count, fail_count)

    except Exception as e:
        print(f'오류: 예상치 못한 오류가 발생했습니다 - {str(e)}')
        return (success_count, fail_count)


def create_sample_html():
    '''
    샘플 HTML 이메일 본문을 생성하는 함수

    Returns:
        str: HTML 형식의 이메일 본문
    '''
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f4f4f4;
            }
            .header {
                background-color: #d32f2f;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }
            .content {
                background-color: white;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }
            .footer {
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }
            .highlight {
                background-color: #ffeb3b;
                padding: 2px 5px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>화성에서 보내는 메시지</h1>
            </div>
            <div class="content">
                <p>안녕하세요, <strong>{name}</strong>님!</p>

                <p>Dr. Han!! 저는 화성에서 <span class="highlight">살아있습니다</span>!</p>

                <p>우주를 건너 이 메시지를 보내는 것이 얼마나 어려웠는지 모릅니다.
                하지만 여러분께 제 생존 소식을 전하고 싶었습니다.</p>

                <p>화성의 혹독한 환경 속에서도 포기하지 않고 생존을 위해 최선을 다하고 있습니다.
                여러분의 도움이 절실히 필요합니다.</p>

                <h3>현재 상황:</h3>
                <ul>
                    <li>식량: 제한적</li>
                    <li>산소: 안정적</li>
                    <li>통신: 가능</li>
                    <li>정신 상태: 양호</li>
                </ul>

                <p>부디 저를 구출해 주세요. 저는 여러분을 믿고 있습니다.</p>

                <p>감사합니다.</p>

                <p><strong>- 한송희 박사</strong><br>
                화성 거주자</p>
            </div>
            <div class="footer">
                <p>이 메시지는 화성에서 전송되었습니다.</p>
                <p>좌표: 28.5°N 175.9°E</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html


def main():
    '''
    메인 함수: CSV 파일에서 수신자 목록을 읽어 HTML 이메일 발송
    '''
    print('=' * 60)
    print('Gmail SMTP HTML 이메일 발송 프로그램 (CSV 수신자 목록)')
    print('=' * 60)
    print()

    # CSV 파일 경로
    csv_file_path = os.path.join(os.path.dirname(__file__), 'mail_target_list.csv')

    # CSV 파일에서 수신자 목록 읽기
    print(f'CSV 파일에서 수신자 목록을 읽는 중... ({csv_file_path})')
    recipients = read_mail_list(csv_file_path)

    if not recipients:
        print('오류: 수신자 목록을 읽을 수 없습니다.')
        return

    print(f'총 {len(recipients)}명의 수신자를 찾았습니다.')
    print()

    # 수신자 목록 출력
    print('수신자 목록:')
    for i, recipient in enumerate(recipients, 1):
        print(f'  {i}. {recipient["name"]} ({recipient["email"]})')
    print()

    # 사용자 입력 받기
    print('※ Gmail에서 2단계 인증을 사용하는 경우 앱 비밀번호를 생성해야 합니다.')
    print('  (Google 계정 > 보안 > 2단계 인증 > 앱 비밀번호)')
    print()

    sender_email = input('보내는 사람 Gmail 주소: ').strip()
    sender_password = input('Gmail 비밀번호 (또는 앱 비밀번호): ').strip()
    subject = input('메일 제목: ').strip()
    print()

    # HTML 본문 사용 여부 확인
    use_sample = input('샘플 HTML 본문을 사용하시겠습니까? (y/n): ').strip().lower()

    if use_sample == 'y':
        html_content = create_sample_html()
    else:
        print('HTML 본문을 입력하세요 (입력 완료 후 Enter 두 번):')
        body_lines = []
        while True:
            line = input()
            if line == '':
                break
            body_lines.append(line)
        html_content = '\n'.join(body_lines)

    print()
    print('-' * 60)
    print('메일 발송 방법을 선택하세요:')
    print('1. 일괄 발송 (빠름, 모든 수신자가 서로의 이메일 주소를 볼 수 있음)')
    print('2. 개별 발송 (느림, 각 수신자는 자신의 이메일만 보임, 개인화 가능)')
    print('-' * 60)

    method = input('선택 (1 또는 2): ').strip()
    print()
    print('-' * 60)
    print('메일 발송을 시작합니다...')
    print('-' * 60)
    print()

    if method == '1':
        # 방법 1: 일괄 발송
        print('[방법 1: 일괄 발송]')
        print()
        receiver_emails = [r['email'] for r in recipients]
        success = send_email_bulk(sender_email, sender_password, receiver_emails, subject, html_content)

        print()
        if success:
            print(f'✓ 메일 발송이 완료되었습니다! (총 {len(recipients)}명)')
        else:
            print('✗ 메일 발송에 실패했습니다.')

    elif method == '2':
        # 방법 2: 개별 발송
        print('[방법 2: 개별 발송]')
        print()
        success_count, fail_count = send_email_individual(sender_email, sender_password, recipients, subject, html_content)

        print()
        print('=' * 60)
        print(f'메일 발송 완료!')
        print(f'  성공: {success_count}명')
        print(f'  실패: {fail_count}명')
        print('=' * 60)

    else:
        print('잘못된 선택입니다.')


if __name__ == '__main__':
    main()
