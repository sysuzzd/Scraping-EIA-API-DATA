# 这是一个目的为在“https://www.cjrl.cn/jiedu/meiguo-325.html”该网址爬取EIA数据和API数据的程序
# EIA[美国能源信息署(Energy Information Administration)]原油库存数据：
# API[美国石油协会(American Petroleum Institute)]库存数据：
#-*- coding:utf-8 -*-

# ***************************************************************************
# 导入模块
import re
import os
import chardet
import codecs
import traceback
import time
import csv
from urllib.request import urlopen as uo
from urllib.request import urlretrieve as ur
from selenium import webdriver
# 导入所需模块结束
# ***************************************************************************

# ***************************************************************************
# 基础数据
eia_page_link = 'https://www.cjrl.cn/jiedu/meiguo-325.html'
api_page_link = 'https://www.cjrl.cn/jiedu/meiguo-324.html'
# 基础数据赋值完毕
# ***************************************************************************

# ***************************************************************************
# 定义功能函数
# ***************************************
# 函数一:mkdir() 创建目录
def mkdir(cur_dir, data_type, date_span):
    if data_type != 'eia' and data_type != 'api':
        print('数据源名出错！！！')
    # 去除首位空格
    path = cur_dir
    path = path.strip()
    # 去除尾部符号 ‘\\’
    path = path.rstrip('\\')
    # 分eia或api不同数据分文件夹存储
    path = path + '\\' + data_type
    # 判断路径是否存在
    isExists = os.path.exists(path)
    # 去掉目录路径，返回文件夹名
    fp_new = os.path.basename(path)
    if not isExists:
        # 如果不存在，则创建目录 os.makedirs(path)
        os.makedirs(path)
        print('新文件夹:  ' + fp_new + ' 创建成功')
    else:
        # 如果目录存在则不创建
        print('文件夹:  ' + fp_new + ' 已存在')
    mkfile_dir = path + '\\' + data_type + '_' +date_span
    return mkfile_dir
# 函数一定义完毕
# ***************************************

# ***************************************
# 函数二:mkfile() 创建文件
def mkfile(mkfile_dir):
    f_name = os.path.basename(mkfile_dir)  # 分割出文件名
    isexist = os.path.exists(mkfile_dir+'.csv')  # 判断路径下的文件是否存在
    if not isexist:
        with codecs.open(mkfile_dir + '.csv', 'w') as f:
            print('新csv文件: ' + f_name + '.csv  已创建完成')
    else:
        print('csv文件:  ' + f_name + '.csv  已存在\n  请及时关闭相关数据文件，否则将出错！')
# 函数二定义完毕
# ***************************************
# 定义功能函数完毕
# ***************************************************************************


# ***************************************************************************
# 主程序开始
cur_dir = os.getcwd()
data_type, date_span = \
    map(str, input('''请输入要获取eia或api，同时以'200701-200701'格式输入获取时间段：(空格隔开)''').split())
# 按不同数据生成数据文件夹，并返回csv数据文件名绝对路径
mkfile_dir = mkdir(cur_dir, data_type, date_span)
# 按返回的csv数据文件绝对路径生成文件
mkfile(mkfile_dir)

if data_type == 'eia':
    url_source = eia_page_link
if data_type == 'api':
    url_source = api_page_link

# webdriver中的PhantomJS方法可以打开一个我们下载的静默浏览器（headless version）。
# 输入executable_path为当前文件夹下的phantomjs.exe以启动浏览器，生成浏览器句柄
driver = webdriver.PhantomJS(executable_path="phantomjs.exe")
# 使用浏览器请求数据页面
print('正在加载网页中的 %s数据' % data_type.upper())
driver.get(url_source)

# 根据所需时间区间起始月份进入多次点击循环
click_flag = True
click_count = 1
inquiry_from_date = date_span[0:6]
str_inquiry_from_date_year = inquiry_from_date[0:4]
inquiry_from_date_year = int(str_inquiry_from_date_year)
str_inquiry_from_date_month = inquiry_from_date[4:6]
inquiry_from_date_month = int(str_inquiry_from_date_month)
inquiry_to_date = date_span[7:13]
str_inquiry_to_date_year = inquiry_to_date[0:4]
inquiry_to_date_year = int(str_inquiry_to_date_year)
str_inquiry_to_date_month = inquiry_to_date[4:6]
inquiry_to_date_month = int(str_inquiry_to_date_month)

while click_flag:
    # 利用find_element_by_xpath该定位方法定位到加载更多数据的标签上
    contents = driver.find_element_by_xpath("//div[@id='loadmore']/a")

    # 利用find_element_by_id 和.text方法找到'datadetail'为id的标签模块中的数据
    data = driver.find_element_by_id('datadetail').text
    # 把日期后边的逗号去掉
    data = data.replace(r',', '')
    # 按行分割data字符串
    temp = data.split('\n')
    # 判断当前数据起始时间是否满足查询时段起始要求
    data_from_date = temp[len(temp) - 1][0:10]  # 2018-03-28
    data_to_date = temp[1][0:10]
    data_from_date_year = int(data_from_date[0:4])
    data_from_date_month = int(data_from_date[5:7])
    data_from_date_day = int(data_from_date[8:10])

    if data_from_date_year < inquiry_from_date_year:
        break
    elif data_from_date_year == inquiry_from_date_year:
        if data_from_date_month < inquiry_from_date_month:
            break
        elif data_from_date_month == inquiry_from_date_month:
            if data_from_date_day - 7 <= 0:
                break

    # 浏览器模拟点击
    contents.click()
    # 提示第几次点击
    print('''已第%d次点击'加载更多'按钮''' % click_count)
    click_count += 1
    # 等待1s使数据刷新
    time.sleep(1)

# 关闭浏览器
driver.close()

# 对所需时间段计算temp对应的起止索引值
str_inquiry_from_year_month = str_inquiry_from_date_year + '-' + str_inquiry_from_date_month
str_inquiry_to_year_month = str_inquiry_to_date_year + '-' + str_inquiry_to_date_month
index = 0
flag1 = 0
flag2 = 0
for tempi in temp:
    if flag1 ==0 and str_inquiry_to_year_month in tempi:
        index_start = index
        flag1 = 1
    if str_inquiry_from_year_month in tempi:
        index_to = index
        flag2 = 1
    if flag2 == 1:
        if not str_inquiry_from_year_month in tempi:
            break
    index += 1

temp[0] = '公布日期 公布时间 前值 预测值 公布值 影响美元 影响金银石油'
with open(mkfile_dir+'.csv', 'w') as f:
    print('正在往  %s 中写入数据' % (mkfile_dir + '.csv'))
    tempk = temp[0].replace(r' ', r',')
    f.writelines(tempk + '\n')
    for tempi in temp[index_start:index_to + 1]: #记得终止索引值应该+1
        tempk = tempi.replace(r' ', r',')    #将数据中的' '(空格) 改为 ','，方便作为csv分割符
        tempj = tempk.replace(r'---', '0')   #将数据中的'---' 改为 '0'
        f.writelines(tempj+'\n')
    print('写入数据完成！')



# ***************************************************************************