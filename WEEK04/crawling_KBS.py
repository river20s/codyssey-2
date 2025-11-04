'''네이버 로그인을 통한 웹 크롤링 및 메일 제목 추출

요구사항 준수:
- selenium 패키지를 사용한 로그인 크롤링
- 로그인 후에만 보이는 콘텐츠를 리스트로 수집 후 출력
- PEP 8 스타일 및 한글 기본 홑따옴표 사용

실행:
- python codyssey-2/WEEK04/crawling_KBS.py
- 네이버 아이디와 비밀번호를 입력하면 로그인 후 콘텐츠 크롤링

참고:
- 네이버는 자동화 감지 시스템이 있어 captcha가 나타날 수 있음
- 보안을 위해 실제 계정 정보는 안전하게 관리 필요
'''

import time
from typing import List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class NaverCrawler:
    '''네이버 로그인 및 크롤링을 수행하는 클래스'''

    def __init__(self) -> None:
        '''크롬 드라이버 초기화'''
        options = webdriver.ChromeOptions()
        # 자동화 감지 방지 옵션
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 20)

    def login(self, user_id: str, password: str) -> bool:
        '''네이버 로그인 수행

        Args:
            user_id: 네이버 아이디
            password: 네이버 비밀번호

        Returns:
            로그인 성공 여부
        '''
        try:
            # 네이버 로그인 페이지 접속
            self.driver.get('https://nid.naver.com/nidlogin.login')
            time.sleep(2)

            # 아이디 입력
            id_input = self.driver.find_element(By.ID, 'id')
            id_input.clear()
            id_input.send_keys(user_id)
            time.sleep(1)

            # 비밀번호 입력
            pw_input = self.driver.find_element(By.ID, 'pw')
            pw_input.clear()
            pw_input.send_keys(password)
            time.sleep(1)

            # 로그인 버튼 클릭
            login_btn = self.driver.find_element(By.ID, 'log.login')
            login_btn.click()
            time.sleep(3)

            # 로그인 성공 확인 (네이버 메인으로 이동했는지 확인)
            current_url = self.driver.current_url
            if 'naver.com' in current_url and 'nidlogin' not in current_url:
                print('로그인 성공!')
                return True
            else:
                print('로그인 실패 또는 추가 인증 필요')
                print(f'현재 URL: {current_url}')
                return False

        except (TimeoutException, NoSuchElementException) as e:
            print(f'로그인 중 오류 발생: {e}')
            return False

    def get_user_info(self) -> List[str]:
        '''로그인 후 사용자 정보 및 개인화 콘텐츠 수집

        Returns:
            로그인 후 보이는 콘텐츠 리스트
        '''
        contents = []

        try:
            # 네이버 메인 페이지로 이동
            self.driver.get('https://www.naver.com')
            time.sleep(2)

            # 로그인 후 사용자 이름 가져오기
            try:
                # 여러 선택자 시도
                selectors = [
                    (By.CSS_SELECTOR, '.MyView-module__link_login___HpHMW'),
                    (By.CSS_SELECTOR, '.link_login'),
                    (By.CSS_SELECTOR, '.user_name'),
                    (By.CSS_SELECTOR, '.area_links .link_name'),
                ]

                user_name = None
                for by, selector in selectors:
                    try:
                        element = self.driver.find_element(by, selector)
                        user_name = element.text.strip()
                        if user_name:
                            break
                    except NoSuchElementException:
                        continue

                if user_name:
                    contents.append(f'로그인 사용자: {user_name}')
                else:
                    contents.append('로그인 사용자: (이름 추출 실패)')

            except Exception as e:
                contents.append(f'사용자 정보 추출 실패: {e}')

            # 로그인 후 보이는 추가 콘텐츠 수집
            # 예: 즐겨찾기, 메일 알림 등
            try:
                # 메일 알림 확인
                mail_elements = self.driver.find_elements(By.CSS_SELECTOR, '.mail')
                if mail_elements:
                    contents.append('메일함 접근 가능')
            except Exception:
                pass

            # 페이지 소스에서 로그인 상태 확인
            page_source = self.driver.page_source
            if 'logout' in page_source.lower() or '로그아웃' in page_source:
                contents.append('로그인 상태 확인됨')

        except Exception as e:
            contents.append(f'콘텐츠 수집 중 오류: {e}')

        return contents

    def get_mail_titles(self) -> List[str]:
        '''네이버 메일함에서 메일 제목들을 추출 (보너스 과제)

        Returns:
            메일 제목 리스트
        '''
        mail_titles = []

        try:
            # 네이버 메일로 이동
            self.driver.get('https://mail.naver.com')
            time.sleep(5)

            # 메일함 로딩 대기
            try:
                # 메일 목록이 로드될 때까지 대기
                self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.list_mail'))
                )
            except TimeoutException:
                print('메일함 로딩 시간 초과')
                return mail_titles

            # 메일 제목 추출 시도 (여러 선택자 사용)
            title_selectors = [
                '.mail_title',
                '.mail_subject',
                '.title_mail',
                'strong.mail_title',
                'span.mail_title',
            ]

            for selector in title_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        title = element.text.strip()
                        if title and len(title) > 0:
                            mail_titles.append(title)

                    if mail_titles:
                        break
                except Exception:
                    continue

            # 제목을 찾지 못한 경우 대체 방법
            if not mail_titles:
                # iframe 내부를 확인
                iframes = self.driver.find_elements(By.TAG_NAME, 'iframe')
                for iframe in iframes:
                    try:
                        self.driver.switch_to.frame(iframe)
                        elements = self.driver.find_elements(By.CSS_SELECTOR, 'strong, .subject')
                        for element in elements[:10]:  # 최대 10개만
                            title = element.text.strip()
                            if title and len(title) > 3:
                                mail_titles.append(title)
                        self.driver.switch_to.default_content()
                        if mail_titles:
                            break
                    except Exception:
                        self.driver.switch_to.default_content()
                        continue

        except Exception as e:
            print(f'메일 제목 추출 중 오류: {e}')

        return mail_titles[:20]  # 최대 20개만 반환

    def close(self) -> None:
        '''브라우저 종료'''
        if self.driver:
            self.driver.quit()


def print_contents(title: str, contents: List[str]) -> None:
    '''콘텐츠 리스트를 화면에 출력

    Args:
        title: 출력할 제목
        contents: 출력할 콘텐츠 리스트
    '''
    print(f'\n--- {title} ---')
    if contents:
        for i, content in enumerate(contents, 1):
            print(f'{i}. {content}')
    else:
        print('수집된 콘텐츠가 없습니다.')


def main() -> None:
    '''메인 함수'''
    print('네이버 로그인 크롤링 프로그램')
    print('=' * 50)

    # 사용자 입력 받기
    user_id = input('네이버 아이디를 입력하세요: ').strip()
    password = input('비밀번호를 입력하세요: ').strip()

    if not user_id or not password:
        print('아이디와 비밀번호를 모두 입력해야 합니다.')
        return

    crawler = None
    try:
        # 크롤러 초기화
        print('\n브라우저를 실행합니다...')
        crawler = NaverCrawler()

        # 로그인 시도
        print('로그인을 시도합니다...')
        if not crawler.login(user_id, password):
            print('\n로그인에 실패했습니다.')
            print('자동화 감지로 인해 추가 인증이 필요할 수 있습니다.')
            print('수동으로 인증을 완료한 후 Enter를 눌러주세요...')
            input()

        # 로그인 후 콘텐츠 수집
        print('\n로그인 후 콘텐츠를 수집합니다...')
        user_contents = crawler.get_user_info()
        print_contents('로그인 후 보이는 콘텐츠', user_contents)

        # 보너스 과제: 메일 제목 수집
        print('\n메일함의 메일 제목을 수집합니다...')
        mail_titles = crawler.get_mail_titles()
        print_contents('네이버 메일 제목', mail_titles)

    except Exception as e:
        print(f'\n프로그램 실행 중 오류 발생: {e}')
    finally:
        if crawler:
            print('\n브라우저를 종료합니다...')
            time.sleep(2)
            crawler.close()
        print('프로그램을 종료합니다.')


if __name__ == '__main__':
    main()
