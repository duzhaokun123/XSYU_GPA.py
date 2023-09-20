import hashlib
import requests
from lxml import etree
from prettytable import PrettyTable

session = requests.Session()
LOGIN_URL = 'https://jwxt.xsyu.edu.cn/eams/login.action'
local = False
courses = []


class Course:
    学年 = 0
    学期 = 0
    课程名称 = ''
    学分 = 0.0
    成绩 = ''
    绩点 = 0.0
    checked = False

    def __str__(self):
        return '学年: ' + str(self.学年) + '-' + str(self.学年 + 1) + '\n' + \
            '学期: ' + str(self.学期) + '\n' + \
            '课程名称: ' + self.课程名称 + '\n' + \
            '学分: ' + str(self.学分) + '\n' + \
            '成绩: ' + self.成绩 + '\n' + \
            '绩点: ' + str(self.绩点) + '\n'


def main():
    print('XSYU GPA')
    print("source: https://github.com/duzhaokun123/XSYU_GPA.py\n")
    login()
    load_courses()
    print_courses()
    check_sum_loop()


def login():
    print('学号 local 本地模式')
    username = input("学号: ")
    if username == "local":
        global local
        local = True
        return
    password = input("密码: ")
    data = {
        "username": username,
        "passText": "请输入密码",
        "password": hash_password(password),
        "encodedPassword": "",
        "session_locale": "zh_CN"
    }
    r = session.post(LOGIN_URL, data=data).text
    if r.find('<div class="actionError">') != -1:
        r = r[r.find('<span class="ui-icon ui-icon-alert" style="float: left; margin-right: 0.3em;"></span>') + 81:]
        r = r[r.find('<span>') + 6:r.find('</span>')]
        print(r)
        return
    cookie = session.cookies.get_dict()['JSESSIONID']
    print("cookie: " + cookie)


def hash_password(password) -> str:
    r = session.get(LOGIN_URL).text
    salt = r[r.find("CryptoJS.SHA1('") + 15:r.find("' + form['password'].value);")]
    print("salt: " + salt)
    return hashlib.sha1((salt + password).encode('utf-8')).hexdigest()


def load_courses():
    if local:
        try:
            r = open('local.html', 'r', encoding='utf-8').read()
        except FileNotFoundError:
            print('本地文件不存在 先登录一次')
            exit()
    else:
        r = session.get(
            'https://jwxt.xsyu.edu.cn/eams/teach/grade/course/person!historyCourseGrade.action?projectType=MAJOR').text
        open('local.html', 'w', encoding='utf-8').write(r)

    html = etree.HTML(r)
    gridtable1 = html.xpath('//table[@class="gridtable"]')[1]
    courses_html = gridtable1.xpath('./tbody/tr')
    global courses
    for course_html in courses_html:
        tds = course_html.xpath('./td')
        course = Course()
        course.学年 = int(tds[0].text[0:4])
        course.学期 = int(tds[0].text[-1:])
        course.课程名称 = tds[3].text.strip()
        course.学分 = float(tds[5].text)
        course.成绩 = tds[7].text.strip()
        course.绩点 = float(tds[8].text)
        courses.append(course)


def print_courses():
    table = PrettyTable(['index', 'c?', '学年', '学期', '课程名称', '学分', '成绩', '绩点'])
    i = 0
    for course in courses:
        table.add_row(
            [i, 'x' if course.checked else ' ', f"{course.学年}-{course.学年 + 1}", course.学期, course.课程名称,
             course.学分, course.成绩, course.绩点])
        i += 1
    print(table)


def check_sum_loop():
    while True:
        c = input('c: 计算选中 q: 退出 a: 全选 1,2,3-4: 改变选中状态\n')
        match c:
            case 'q':
                exit()
            case 'a':
                for course in courses:
                    course.checked = True
                print_courses()
            case 'c':
                sum()
            case _:
                c = c.split(',')
                for i in c:
                    if i.find('-') != -1:
                        i = i.split('-')
                        for j in range(int(i[0]), int(i[1]) + 1):
                            courses[j].checked = not courses[j].checked
                    else:
                        courses[int(i)].checked = not courses[int(i)].checked
                print_courses()


def sum():
    to_sum = []
    for course in courses:
        if course.checked:
            to_sum.append(course)
    if len(to_sum) == 0:
        print('没有选中的课程')
        return
    sigma_学分 = 0.0
    sigma_绩点x学分 = 0.0
    table = PrettyTable(['学年', '学期', '课程名称', '学分', '成绩', '绩点'])
    latex_1 = ''
    latex_2 = ''
    for course in to_sum:
        sigma_学分 += course.学分
        sigma_绩点x学分 += course.绩点 * course.学分
        table.add_row(
            [f"{course.学年}-{course.学年 + 1}", course.学期, course.课程名称, course.学分, course.成绩, course.绩点])
        latex_1 += f"{course.学分} \\times {course.绩点} + "
        latex_2 += f"{course.学分} + "
    print(table)
    print('计算公式(LaTex): \\frac{' + latex_1[:-3] + '}{' + latex_2[:-3] + '}')
    print('平均绩点: ' + str(sigma_绩点x学分 / sigma_学分))


if __name__ == '__main__':
    main()
