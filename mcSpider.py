#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import time
import chardet

# 传入URL获取网页内容
def get_html(url):
	try:
		r = requests.get(url, timeout=30)
		r.raise_for_status()
		r.encoding = r.apparent_encoding
		return r.text
	except:
		return u'[ERROR][get_html]获取网页内容时发生错误！'


# 通过URL生成美丽汤，爬取并储存所需的数据
def get_content(url):
	data_list = []
	html = get_html(url)
	# 搜索class为s_post的div标签
	soup = BeautifulSoup(html, 'lxml')
	postTags = soup.find_all('div', attrs={'class': 's_post'})
	# 在每个帖子的div中搜索标题、用户、时间和链接
	for post in postTags:
		data = {}
		try:
			data['title'] = post.find('a', attrs={'class': 'bluelink'}).text.strip()
			info = post.find_all('font', attrs={'class': 'p_violet'})
			data['user'] = info[1].text
			data['time'] = post.find('font', attrs={'class': 'p_green p_date'}).text.strip()
			data['link'] = 'http://tieba.baidu.com' + post.find('a', attrs={'class': 'bluelink'})['href']
			data_list.append(data)
		except:
			print(u'[ERROR][get_content]爬取帖子信息时发生错误！')
	# 返回数据列表，其中的元素为字典
	return data_list


# 爬取数据写入文本文件
def Out2File(dict, tieba, keyword, url):
	# 以Append方式打开文件，写入数据时使用UTF-8编码
	with open('tieba.txt', 'a+', encoding='utf-8') as f:
		time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
		head = u'爬取时间: %s \n在%s吧搜索关键词: %s \n搜索结果URL: %s \n' % (time_str, tieba, keyword, url)
		print(head)
		f.write(head)
		# 将字典中储存的数据整理输出
		error_list = []
		for data in dict:
			item = u'标题: %s \t 用户: %s \t 时间: %s \t 链接: %s \n' % (data['title'], data['user'], data['time'], data['link'])
			try:
				f.write(item)
				print(item)
			# 标题、用户名等字段中存在特殊符号/文字时会出错，目前尚未解决
			except UnicodeEncodeError:
				print(u'[ERROR]Unicode 编码时出错！')
				print(u'[ERROR]未写入文件的错误项目: '+item)
				error = {}
				error[data['title']] = chardet.detect(data['title'].encode())
				error[data['user']] = chardet.detect(data['user'].encode())
				error_list.append(error)
		# 打印错误编码的列表
		print(u'[Out2File]当前页面爬取Over\n')
		for i in error_list:
			print(i)


# 通过尾页链接确定总页数，生成URL列表
def getUrlList(url):
	html = get_html(url)
	soup = BeautifulSoup(html, 'lxml')
	pn = 1
	url_list = []
	print(u'[getUrlList]正在获取页码数')
	# 捕获TypeError异常，用于单页的搜索结果
	try:
		last_tag = soup.find('a', attrs={'class': 'last'})['href']
	except TypeError:
		print(u'[getUrlList]未找到页码元素，可能为单页')
		url_list.append(url)
	# 如果未出现TypeError异常，执行此段
	else:
		try:
			kwd = re.search('&pn=\d+', last_tag).group()
			pn_max = int(re.search('\d+', kwd).group())
			print(u'[getUrlList]搜索结果共%d页' % pn_max)
		except:
			print(u'[ERROR][getUrlList]获取页码数时发生了错误！\n')
			print(u'soup.find:'+soup.find('a', attrs={'class': 'last'})['href'])
		else:
			print(u'[getUrlList]获取页码数成功 \n URL: %s \n last_tag: %s \n kwd: %s \n pn_max: %s \n' % (url, last_tag, kwd, pn_max))
			while (pn<=pn_max):
				url_list.append(url+'&pn='+str(pn))
				pn = pn + 1
	# 返回URL列表
	return url_list


# 主函数
def main(base_url, tieba, keyword, thread_only):
	url = base_url + '&kw=' + tieba + '&qw=' + keyword + '&only_thread=' + thread_only
	url_list = getUrlList(url)
	#url_list = ['']
	# 遍历URL列表，爬取网页内容
	for i in url_list: 
		content = get_content(i)
		Out2File(content, tieba, keyword, i)
	print(u'[main]爬取数据已保存到本地！')


# 从控制台获取查询的关键词
def get_input():
	kwd = input(u'请输入搜索关键词:')
	return kwd


# 基础变量
base_url = 'http://tieba.baidu.com/f/search/res?ie=utf-8'
tieba = 'minecraft'
keyword = 'tiankeng'
thread_only = '1'


# 当Python文件被直接执行而非import时触发
if __name__ == '__main__':
	keyword = get_input()
	print(u'关键词为:'+keyword)
	main(base_url, tieba, keyword, thread_only)
