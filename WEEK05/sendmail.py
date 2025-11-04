'''Gmail SMTP 프로토콜을 이용하여 이메일 발송

주요 기능:
    - Gmail SMTP를 통한 이메일 발송
    - TLS 보안 연결 (포트 587)
    - 예외 처리 및 오류 메시지
    - 첨부파일 지원 (보너스 과제)

SMTP 프로토콜 정보:
    - 서버: smtp.gmail.com
    - 포트: 587 (TLS)
    - 보안: STARTTLS

Gmail 설정 방법:
    1. 2단계 인증 활성화
    2. Google 계정 > 보안 > 앱 비밀번호 생성
    3. 생성된 16자리 비밀번호를 프로그램에서 사용
'''

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os


def send_email(sender_email, sender_password, receiver_email, subject, body, attachment_path=None):
    '''
    Gmail SMTP를 이용하여 이메일을 발송하는 함수

    Args:
        sender_email (str): 보내는 사람의 Gmail 주소
        sender_password (str): 보내는 사람의 Gmail 앱 비밀번호
        receiver_email (str): 받는 사람의 이메일 주소
        subject (str): 메일 제목
        body (str): 메일 본문
        attachment_path (str, optional): 첨부파일 경로

    Returns:
        bool: 메일 발송 성공 여부
    '''
    # SMTP 서버 설정
    # Gmail SMTP 서버 주소 및 TLS 포트 번호 (587)
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # TLS 포트 (STARTTLS 사용)

    try:
        # MIME 메시지 생성
        # MIMEMultipart: 여러 부분(본문, 첨부파일 등)으로 구성된 메일 생성
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject

        # 메일 본문 추가
        # MIMEText: 텍스트 형식의 메일 본문 생성
        message.attach(MIMEText(body, 'plain'))

        # 첨부파일이 있는 경우 (보너스 과제)
        if attachment_path and os.path.exists(attachment_path):
            try:
                # 파일을 바이너리 모드로 열기
                with open(attachment_path, 'rb') as attachment:
                    # MIMEBase 객체 생성
                    # application/octet-stream: 일반적인 바이너리 데이터 타입
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())

                # 파일을 base64로 인코딩
                # 이메일은 텍스트 기반이므로 바이너리 데이터를 base64로 인코딩
                encoders.encode_base64(part)

                # 헤더 추가
                # Content-Disposition: 첨부파일임을 나타내는 헤더
                filename = os.path.basename(attachment_path)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )

                # 메시지에 첨부파일 추가
                message.attach(part)
                print(f'첨부파일이 추가되었습니다: {filename}')
            except Exception as e:
                print(f'첨부파일 처리 중 오류 발생: {str(e)}')
                return False

        # SMTP 서버에 연결
        # smtplib.SMTP: SMTP 프로토콜을 사용하여 메일 서버와 통신
        print(f'SMTP 서버에 연결 중... ({smtp_server}:{smtp_port})')
        server = smtplib.SMTP(smtp_server, smtp_port)

        # TLS 보안 연결 시작
        # starttls(): 평문 연결을 암호화된 TLS 연결로 업그레이드
        server.starttls()
        print('TLS 보안 연결이 설정되었습니다.')

        # 로그인
        # Gmail 계정과 앱 비밀번호(또는 계정 비밀번호)로 SMTP 서버에 인증
        print('Gmail 계정으로 로그인 중...')
        server.login(sender_email, sender_password)
        print('로그인 성공!')

        # 메일 발송
        # as_string(): MIME 메시지를 문자열로 변환
        # sendmail(): 실제로 메일을 전송
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        print(f'메일이 성공적으로 발송되었습니다: {receiver_email}')

        # 연결 종료
        # quit(): SMTP 서버와의 연결을 정상적으로 종료
        server.quit()
        print('SMTP 서버 연결이 종료되었습니다.')

        return True

    except smtplib.SMTPAuthenticationError:
        # 인증 오류: 잘못된 이메일 주소 또는 비밀번호
        print('오류: 인증 실패. 이메일 주소 또는 비밀번호를 확인해주세요.')
        print('Gmail의 경우 2단계 인증을 사용하는 경우 앱 비밀번호를 생성해야 합니다.')
        return False

    except smtplib.SMTPConnectError:
        # 연결 오류: SMTP 서버에 연결할 수 없음
        print('오류: SMTP 서버 연결 실패. 네트워크 연결을 확인해주세요.')
        return False

    except smtplib.SMTPServerDisconnected:
        # 연결 끊김 오류: 서버와의 연결이 예기치 않게 끊어짐
        print('오류: SMTP 서버와의 연결이 끊어졌습니다.')
        return False

    except smtplib.SMTPException as e:
        # 기타 SMTP 관련 오류
        print(f'오류: SMTP 오류가 발생했습니다 - {str(e)}')
        return False

    except Exception as e:
        # 예상치 못한 모든 오류 처리
        print(f'오류: 예상치 못한 오류가 발생했습니다 - {str(e)}')
        return False


def main():
    '''
    메인 함수: 사용자로부터 입력받아 이메일 발송
    '''
    print('=' * 50)
    print('Gmail SMTP 이메일 발송 프로그램')
    print('=' * 50)
    print()

    # 사용자 입력 받기
    # Gmail에서 2단계 인증 사용 시 앱 비밀번호 필요
    print('※ Gmail에서 2단계 인증을 사용하는 경우 앱 비밀번호를 생성해야 합니다.')
    print('  (Google 계정 > 보안 > 2단계 인증 > 앱 비밀번호)')
    print()

    # 보내는 사람의 Gmail 주소 입력
    sender_email = input('보내는 사람 Gmail 주소: ').strip()
    # Gmail 계정 비밀번호 또는 앱 비밀번호 입력
    sender_password = input('Gmail 비밀번호 (또는 앱 비밀번호): ').strip()
    # 받는 사람의 이메일 주소 입력
    receiver_email = input('받는 사람 이메일 주소: ').strip()
    # 메일 제목 입력
    subject = input('메일 제목: ').strip()
    print('메일 본문 (입력 완료 후 Enter 두 번):')

    # 메일 본문 입력 (여러 줄 입력 가능)
    # 빈 줄을 입력하면 입력 종료
    body_lines = []
    while True:
        line = input()
        if line == '':
            break
        body_lines.append(line)
    body = '\n'.join(body_lines)

    # 첨부파일 여부 확인
    attach_file = input('첨부파일을 추가하시겠습니까? (y/n): ').strip().lower()
    attachment_path = None

    if attach_file == 'y':
        # 첨부파일 경로 입력
        attachment_path = input('첨부파일 경로를 입력하세요: ').strip()
        # 파일 존재 여부 확인
        if not os.path.exists(attachment_path):
            print(f'경고: 파일을 찾을 수 없습니다 - {attachment_path}')
            continue_anyway = input('첨부파일 없이 계속 진행하시겠습니까? (y/n): ').strip().lower()
            if continue_anyway != 'y':
                print('메일 발송이 취소되었습니다.')
                return
            attachment_path = None

    print()
    print('-' * 50)
    print('메일 발송을 시작합니다...')
    print('-' * 50)
    print()

    # 이메일 발송
    success = send_email(
        sender_email,
        sender_password,
        receiver_email,
        subject,
        body,
        attachment_path
    )

    print()
    if success:
        print('✓ 메일 발송이 완료되었습니다!')
    else:
        print('✗ 메일 발송에 실패했습니다.')


if __name__ == '__main__':
    main()
