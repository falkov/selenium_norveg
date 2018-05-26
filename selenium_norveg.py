import time
import os
import json
import logging
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SITE_URL = "http://norveg.falkov.info/"
# SITE_URL = "http://127.0.0.1:8000/"

LOG_FILE_NAME = 'selenium.log'

li_obj_questions = list()

css_class_current = 'badge badge-pill grey darken-2'
css_class_no_answer = 'badge badge-pill grey'
css_class_is_answer = 'badge badge-pill light-blue darken-1'
css_class_right_answer = 'badge badge-pill green'
css_class_wrong_answer = 'badge badge-pill red'

section_question = {
    '1':  {'from': 1,   'to': 10,  'amount_for_test': 2},
    '2':  {'from': 11,  'to': 35,  'amount_for_test': 4},
    '3':  {'from': 36,  'to': 50,  'amount_for_test': 3},
    '4':  {'from': 51,  'to': 70,  'amount_for_test': 3},
    '5':  {'from': 71,  'to': 76,  'amount_for_test': 1},
    '6':  {'from': 77,  'to': 86,  'amount_for_test': 2},
    '7':  {'from': 87,  'to': 92,  'amount_for_test': 1},
    '8':  {'from': 93,  'to': 97,  'amount_for_test': 1},
    '9':  {'from': 98,  'to': 105, 'amount_for_test': 2},
    '10': {'from': 106, 'to': 111, 'amount_for_test': 1},
    '11': {'from': 112, 'to': 127, 'amount_for_test': 2},
    '12': {'from': 128, 'to': 142, 'amount_for_test': 2},
    '13': {'from': 143, 'to': 158, 'amount_for_test': 2},
    '14': {'from': 159, 'to': 163, 'amount_for_test': 1},
    '15': {'from': 164, 'to': 173, 'amount_for_test': 2},
    '16': {'from': 174, 'to': 179, 'amount_for_test': 1},
    '17': {'from': 180, 'to': 187, 'amount_for_test': 2},
    '18': {'from': 188, 'to': 192, 'amount_for_test': 1},
    '19': {'from': 193, 'to': 195, 'amount_for_test': 1},
    '20': {'from': 196, 'to': 201, 'amount_for_test': 1},
    '21': {'from': 202, 'to': 210, 'amount_for_test': 2},
    '22': {'from': 211, 'to': 219, 'amount_for_test': 2},
    '23': {'from': 220, 'to': 228, 'amount_for_test': 2},
    '24': {'from': 229, 'to': 233, 'amount_for_test': 1},
    '25': {'from': 234, 'to': 239, 'amount_for_test': 1},
    '26': {'from': 240, 'to': 250, 'amount_for_test': 2}
}


class Question:
    def __init__(self, section, question, answers):
        self.secton_num = section['num']
        self.secton_text_eng = section['text_eng']
        self.secton_text_rus = section['text_rus']
        self.secton_text_nor = section['text_nor']
        self.question_num = question['num']
        self.question_image = question['image']
        self.question_text_eng = question['text_eng']
        self.question_text_rus = question['text_rus']
        self.question_text_nor = question['text_nor']
        self.answers = answers.copy()

    def __str__(self):
        return f'# {self.question_num} : sec.{self.secton_num} ({self.secton_text_eng}) - ' \
               f'{self.question_text_eng} - {self.question_text_rus}, answers = {self.answers} '

    def get_list_answers_eng(self):
        li_keys = self.answers.keys()
        li_answers = list()
        for letter in li_keys:
            li_answers.append(self.answers[letter]['text_eng'])
        return li_answers

    def get_list_answers_rus(self):
        li_keys = self.answers.keys()
        li_answers = list()
        for letter in li_keys:
            li_answers.append(self.answers[letter]['text_rus'])
        return li_answers

    def get_list_answers_nor(self):
        li_keys = self.answers.keys()
        li_answers = list()
        for letter in li_keys:
            li_answers.append(self.answers[letter]['text_nor'])
        return li_answers


def init_logging():
    if os.path.exists(LOG_FILE_NAME):
        os.remove(LOG_FILE_NAME)

    logging.basicConfig(format="%(asctime)s  %(filename)s:%(lineno)d  %(message)s",
        datefmt="%Y-%m-%d  %H:%M.%S", level=logging.INFO, filename=LOG_FILE_NAME)


def ret_qna_from_liqna_qnum(q_num):
    for qna in li_obj_questions:
        if str(q_num) == qna.question_num:
            return qna


def ret_qna_from_liqna_eng(q_this_text_eng, li_this_answers):
    def is_this_answers_in_qna(li_qna_answers):
        for this_answer in li_this_answers:
            if this_answer not in li_qna_answers:
                return False
        else:
            return True

    for qna in li_obj_questions:
        if q_this_text_eng == qna.question_text_eng:
            liqna_answers = qna.get_list_answers_eng()

            if is_this_answers_in_qna(liqna_answers):
                return qna


def create_list_objects_from_json():
    json_file = open("./norveg.json")
    json_object = json.load(json_file)
    json_file.close()

    dict_sections = {}
    dict_questions = {}
    dict_answers_temp = {}
    dict_answers_this_question = {}

    def answers_for_this_question(question_num):
        dict_answers_this_question.clear()
        for key, value in dict_answers_temp.items():
            if value['question_num'] == str(question_num):
                dict_answers_this_question.update({
                    value['letter']: {
                        # 'question_num': value['question_num'],
                        'text_eng': value['text_eng'],
                        'text_rus': value['text_rus'],
                        'text_nor': value['text_nor'],
                        'correct': value['correct']
                    }
                })
        return dict_answers_this_question

    for num, obj in enumerate(json_object):
        if obj['model'] == 'app_quiz.section':
            dict_sections.update({
                str(obj['pk']): {
                    'text_eng': obj['fields']['text_eng'],
                    'text_rus': obj['fields']['text_rus'],
                    'text_nor': obj['fields']['text_nor']
                }
            })

        if obj['model'] == 'app_quiz.question':
            dict_questions.update({
                obj['fields']['number']: {
                    'section_num': obj['fields']['section'],
                    'text_eng': obj['fields']['text_eng'],
                    'text_rus': obj['fields']['text_rus'],
                    'text_nor': obj['fields']['text_nor'],
                    'image': obj['fields']['image']
                }
            })

        if obj['model'] == 'app_quiz.answer':
            dict_answers_temp.update({
                str(obj['pk']): {
                    'question_num': obj['fields']['question'],
                    'letter': obj['fields']['letter'],
                    'text_eng': obj['fields']['text_eng'],
                    'text_rus': obj['fields']['text_rus'],
                    'text_nor': obj['fields']['text_nor'],
                    'correct': obj['fields']['correct']
                }
            })

    li_obj_questions.clear()

    for num in range(1, 251):
        sect = dict_sections[dict_questions[str(num)]['section_num']]
        sect.update({'num': dict_questions[str(num)]['section_num']})

        quest = dict_questions[str(num)]
        quest.update({'num': str(num)})

        answers = answers_for_this_question(num)

        obj_question = Question(sect, quest, answers)
        li_obj_questions.append(obj_question)

    # for aa in li_obj_questions: print(aa, '\n')


def init_driver(window_width, window_height):
    driver = webdriver.Chrome('../webdrivers/Mac/chromedriver')
    driver.set_window_size(window_width, window_height)
    driver.implicitly_wait(10)
    return driver


def check_learn(driver):
    wait = WebDriverWait(driver, 10)

    def switch_to_en():
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "ul.nav.nav-tabs.animated li.nav-item a[href='#panel1']"))).click()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div#panel1 p.h5")))

    def switch_to_ru():
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "ul.nav.nav-tabs.animated li.nav-item a[href='#panel2']"))).click()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div#panel2 p.h5")))

    for section_num in range(1, 27):
        q_from = section_question[str(section_num)]['from']
        q_to = section_question[str(section_num)]['to']

        show_sidebar(driver)
        time.sleep(.5)

        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div#slide-out a.collapsible-header"))).click()

        section_this = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(),'{section_num}')]")))
        section_this.location_once_scrolled_into_view
        section_this.click()

        str_section_eng = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[style*='right'"))).text
        str_section_eng = str_section_eng[str_section_eng.find('. ')+2:str_section_eng.find('  (')]

        for q_num in range(q_from, q_to+1):
            switch_to_en()
            q_text_eng = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='panel1']//p[@class='h5']"))).text
            q_text_eng = q_text_eng[q_text_eng.find('. ')+2:]
            answers_eng = driver.find_elements(By.CSS_SELECTOR, "label[for*='checkbox_eng_']")

            switch_to_ru()
            q_text_rus = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div#panel2 p.h5"))).text
            q_text_rus = q_text_rus[q_text_rus.find('. ')+2:]
            answers_rus = driver.find_elements(By.CSS_SELECTOR, "label[for*='checkbox_rus_']")

            check_this_qna(q_num, q_text_eng, q_text_rus, answers_eng, answers_rus, str_section_eng)

            switch_to_en()
            random_checkbox_eng = 'checkbox_eng_' + str(random.randint(1, 4))
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"label[for*='{random_checkbox_eng}']"))).click()
            this_answer_eng = driver.find_element(By.CSS_SELECTOR, f"label[for*='{random_checkbox_eng}']").get_attribute('textContent')

            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#btn_check"))).click()

            if ret_correct(q_num, this_answer_eng):
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div#centralModalSuccess a.btn"))).click()
                wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div#centralModalSuccess")))
            else:
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div#centralModalWrong a.btn"))).click()
                wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div#centralModalWrong")))

            if q_num < q_to:
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#btn_next"))).click()


def ret_correct(q_num, this_answer_eng):
    this_qna = ret_qna_from_liqna_qnum(q_num)
    correct = ''

    for value in this_qna.answers.values():
        if this_answer_eng == value['text_eng']:
            correct = value['correct']

    return True if correct == 'true' else False


def check_this_qna(q_num, q_text_eng, q_text_rus, answers_eng, answers_rus, str_section_eng):
    this_qna = ret_qna_from_liqna_qnum(q_num)

    def is_answer_eng(str_answer):
        result = False
        for value in this_qna.answers.values():
            if str_answer == value['text_eng']:
                result = True
        return result

    def is_answer_rus(str_answer):
        result = False
        for value in this_qna.answers.values():
            if str_answer == value['text_rus']:
                result = True
        return result

    if str_section_eng != this_qna.secton_text_eng:
        logging.info(f'q_num = {q_num}: str_section_eng != this_qna.secton_text_eng: {str_section_eng} != {this_qna.secton_text_eng}')

    if q_text_eng != this_qna.question_text_eng:
        logging.info(f'q_num = {q_num}: q_text_eng != this_qna.question_text_eng: {q_text_eng} != {this_qna.question_text_eng}')

    if q_text_rus != this_qna.question_text_rus:
        logging.info(f'q_num = {q_num}: q_text_rus != this_qna.question_text_rus: {q_text_rus} != {this_qna.question_text_rus}')

    for ans in answers_eng:
        if not is_answer_eng(ans.get_attribute('textContent')):
            logging.info("q_num = {q_num}: нет такого answer_eng в БД")

    for ans in answers_rus:
        if not is_answer_rus(ans.get_attribute('textContent')):
            logging.info("q_num = {q_num}: нет такого answer_rus в БД")


def show_sidebar(driver):
    wait = WebDriverWait(driver, 10)

    # transform: translateX(-100%) - sidebar нет, ширина < 1441; transform: translateX(0%) - sidebar есть, ширина > 1440
    attr_style = driver.find_element(By.CSS_SELECTOR, 'div#slide-out').get_attribute('style')
    translate_x = attr_style[attr_style.find('(')+1:attr_style.find(')')]

    if translate_x == '-100%':      # sidebar нет,  ширина < 1441
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='#']"))).click()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div#slide-out[style*='transform: translateX']")))


def check_test(driver):
    my_answers = list();    my_answers.append('s')    # чтобы начинать индекс с единицы
    test_answers = list();  test_answers.append('s')
    test_qnas = list();     test_qnas.append('s')
    li_this_answers = list()

    wait = WebDriverWait(driver, 10)

    show_sidebar(driver)
    time.sleep(.5)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='/testing/yes']"))).click()

    for qtest_num in range(1, 46):
        qtest_text_eng = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.card p.h5"))).text

        li_this_answers.clear()
        answers_amount = len(driver.find_elements(By.CSS_SELECTOR, "label[for*='checkbox']"))

        for checkbox_count in range(1, answers_amount+1):
            temp_answer = driver.find_element(By.CSS_SELECTOR, f"label[for*='checkbox_{checkbox_count}']").get_attribute('textContent')
            li_this_answers.append(temp_answer)

        # по вопросу и ответам найти qna
        this_qna = ret_qna_from_liqna_eng(qtest_text_eng, li_this_answers)

        test_qnas.append(this_qna)

        random_checkbox = 'checkbox_' + str(random.randint(1, 4))
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"label[for*='{random_checkbox}']"))).click()
        this_answer_eng = driver.find_element(By.CSS_SELECTOR, f"label[for*='{random_checkbox}']").get_attribute('textContent')

        my_answers.append('right') if ret_correct(this_qna.question_num, this_answer_eng) else my_answers.append('false')

        if qtest_num < 45:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#btn_next"))).click()

    time.sleep(.5)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick*='btn_endtest_click']"))).click()

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "ul.nav.nav-tabs span[style*='font-size: larger']")))

    # появился результат
    test_result = driver.find_element(By.CSS_SELECTOR, "ul.nav.nav-tabs span:nth-child(1)").text

    temp_text = driver.find_element(By.CSS_SELECTOR, "ul.nav.nav-tabs span:nth-child(2)").text
    test_rightanswers_amount = int(temp_text[temp_text.find('-')+2:temp_text.find(',')])

    temp_text = driver.find_element(By.CSS_SELECTOR, "ul.nav.nav-tabs span:nth-child(3)").text
    test_faulseanswers_amount = int(temp_text[temp_text.find('-')+2:temp_text.find(',')])

    temp_text = driver.find_element(By.CSS_SELECTOR, "ul.nav.nav-tabs span:nth-child(4)").text
    test_noanswers_amount = int(temp_text[temp_text.find('-')+2:temp_text.find(')')])

    if my_answers.count('right') != test_rightanswers_amount:
        logging.info(f'my_answers.count(right) != test_rightanswers_amount : {my_answers.count("right")} != {test_rightanswers_amount}')

    if my_answers.count('false') != test_faulseanswers_amount:
        logging.info(f'my_answers.count(false) != test_faulseanswers_amount : {my_answers.count("false")} != {test_faulseanswers_amount}')

    if my_answers.count('no_answer') != test_noanswers_amount:
        logging.info(f'my_answers.count(no_answer) != test_noanswers_amount : {my_answers.count("no_answer")} != {test_noanswers_amount}')

    for ans_num in range(1, 46):
        temp_css_class = driver.find_element(By.CSS_SELECTOR, f'span#qmap_{ans_num}').get_attribute('class')
        test_answers.append('right') if temp_css_class == css_class_right_answer else test_answers.append('false')

    for answer_num in range(1, 46):
        if my_answers[answer_num] != test_answers[answer_num]:
            logging.info(f'my_answers[{answer_num}] != test_answers[{answer_num}] : {my_answers[answer_num]} != {test_answers[answer_num]}')
            logging.info(f'+ {test_qnas[answer_num]}')


if __name__ == "__main__":
    init_logging()
    create_list_objects_from_json()

    driver = init_driver(window_width=1442, window_height=1000)
    driver.get(SITE_URL)

    check_learn(driver)
    check_test(driver)

    if os.stat(LOG_FILE_NAME).st_size == 0:
        pass
        # driver.close()
        # driver.quit()
    else:
        print('Ошибка! Смотри selenium.log')


    # init_logging()
    # create_list_objects_from_json()
    #
    # for loop in range(100):
    #     print('Test ', loop)
    #
    #     driver = init_driver(window_width=1440, window_height=1000)
    #     driver.get(SITE_URL)
    #
    #     check_test(driver)
    #
    #     if os.stat(LOG_FILE_NAME).st_size == 0:
    #         driver.close()
    #         driver.quit()
    #     else:
    #         print('Ошибка! Смотри selenium.log')
    #         break
