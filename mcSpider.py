import requests
from bs4 import BeautifulSoup
import re
import time


# 传入URL获取网页内容
def get_html(url):
	try:
		r = requests.get(url, timeout=30)
		r.raise_for_status()
		r.encoding = r.apparent_encoding
		return r.text
	except:
		return "[ERROR][get_html]获取网页内容时发生错误！"


# 通过URL生成美丽汤，爬取并储存所需的数据
def get_content(url):
	data_list = []
	html = get_html(url)

	soup = BeautifulSoup(html, "lxml")
	postTags = soup.find_all("div", attrs={"class": "s_post"})

	for post in postTags:
		data = {}
		try:
			data["title"] = post.find("a", attrs={"class": "bluelink"}).text.strip()
			info = post.find_all("font", attrs={"class": "p_violet"})
			data["user"] = info[1].text
			data["time"] = post.find("font", attrs={"class": "p_green p_date"}).text.strip()
			data["link"] = "http://tieba.baidu.com" + post.find("a", attrs={"class": "bluelink"})["href"]
			data_list.append(data)
		except:
			print("[ERROR][get_content]爬取帖子信息时发生错误！")

	return data_list


# 爬取数据写入文本文件
def Out2File(dict, tieba, keyword, url):
	with open("tieba.txt", "a+") as f:
		time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		head = "爬取时间: {}\n在{}吧搜索关键词: {}\n搜索结果URL: {}".format(time_str, tieba, keyword, url)
		print(head)
		f.write(head)
		# 将字典中储存的数据整理输出
		for data in dict:
			item = "标题: {} \t 用户: {} \t 时间: {} \t 链接: {}".format(data["title"], data["user"], data["time"], data["link"])
			try:
				f.write(item)
				print(item)
			# 标题、用户名等字段中存在特殊符号/文字时会出错，目前尚未解决
			except UnicodeEncodeError:
				print("[ERROR]Unicode 编码时出错！")
				print("[ERROR]未写入文件的错误项目: "+item)

		print("[Out2File]当前页面爬取Over\n")


# 通过尾页链接确定总页数，生成URL列表
def getUrlList(url):
	html = get_html(url)
	soup = BeautifulSoup(html, "lxml")
	pn = 1
	url_list = []
	print("[getUrlList]正在获取页码数")
	# 捕获TypeError异常，用于单页的搜索结果
	try:
		last_tag = soup.find("a", attrs={"class": "last"})["href"]
	except TypeError:
		print("[getUrlList]未找到页码元素，可能为单页")
		url_list.append(url)
	# 如果未出现TypeError异常，执行此段
	else:
		try:
			kwd = re.search("&pn=\d+", last_tag).group()
			pn_max = int(re.search("\d+", kwd).group())
			print("[getUrlList]搜索结果共%d页" % pn_max)
		except:
			print("[ERROR][getUrlList]获取页码数时发生了错误！\n")
			print("soup.find:"+soup.find("a", attrs={"class": "last"})["href"])
		else:
			print("[getUrlList]获取页码数成功\nURL: {}\nlast_tag: {}\nkwd: {}\npn_max: {}\n".format(url, last_tag, kwd, pn_max))
			while (pn<=pn_max):
				url_list.append(url+"&pn="+str(pn))
				pn = pn + 1
	# 返回URL列表
	return url_list


# 主函数
def main(base_url, tieba, keyword, thread_only):
	url = base_url + "&kw=" + tieba + "&qw=" + keyword + "&only_thread=" + thread_only
	url_list = getUrlList(url)
	#url_list = [""]
	# 遍历URL列表，爬取网页内容
	for i in url_list: 
		content = get_content(i)
		Out2File(content, tieba, keyword, i)
	print("[main]爬取数据已保存到本地！")


# 从控制台获取查询的关键词
def get_input():
	kwd = input("请输入搜索关键词:")
	return kwd


# 基础变量
base_url = "http://tieba.baidu.com/f/search/res?ie=utf-8"
tieba = "minecraft"
keyword = "tiankeng"
thread_only = "1"


# 当Python文件被直接执行而非import时触发
if __name__ == "__main__":
	keyword = get_input()
	print("关键词为:"+keyword)
	main(base_url, tieba, keyword, thread_only)
