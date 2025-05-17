from http.client import responses
from bs4 import BeautifulSoup
import requests
import brotli
import httpx
import multiprocessing
from multiprocessing import Pool, Manager
from functools import partial
import os
import shutil
from tqdm import tqdm

os.makedirs('./tmp', exist_ok=True)
os.makedirs('./output', exist_ok=True)
bookname = ""
bqg_url = "https://www.c24f.cc/"
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
    "accept-encoding": "br, gzip, deflate",
}
word_lis = ['www', '收藏本站', '笔趣阁']

def get_list(bookid):
    try:
        url_0 = bqg_url + f'read/{bookid}/'
        responses = requests.get(url_0, headers=headers)
        soup = BeautifulSoup(responses.text, 'html.parser')
        meta_tag = soup.find('meta', attrs={'property': 'og:title'})
        print("---------------------------")
        bookname = "book"
        if meta_tag and meta_tag.get('content'):
            print("书名解析成功！书名：", meta_tag['content'])
            bookname = meta_tag['content']
        else:
            print('书名未解析成功')
        listmain_div = soup.find('div', class_='listmain')
        url_list = []
        if listmain_div:
            links = listmain_div.find_all('a')
            for link in links:
                tmp = str(link.get('href'))
                if tmp.endswith('.html'):
                    url_list.append(bqg_url + tmp)
        print("---------------------------")
        print(f"成功读取目录，共计{len(url_list)}章")
        print("---------------------------")
        return url_list, bookname
    except:
        print("网址无法连接，请检查是否可用！")
        return []

def get_single_chapter(url_lis, idx, failed_list=[], queue=None):
    s = "/" + str(idx) + ".html"
    url = None
    for i in url_lis:
        if i.endswith(s):
            url = i
            break
    try:
        with httpx.Client(http2=True, headers=headers) as client:
            response = client.get(url)
            html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h1', class_='wap_none')
        if title:
            title = title.text.strip()
            if title.find('.')!=-1:
                title=title[title.find('.')+1:]
            if title.find(' ')!=-1:
                title=title[title.find(' ')+1:]
            if title.startswith(str(idx)):
                title = title.replace(str(idx),"")
            title = f"第{idx}章：" + title
        else:
            title = f"第{idx}章："

        content_div = soup.find('div', id='chaptercontent', class_='Readarea ReadAjax_content')
        if content_div:
            lines = []
            for elem in content_div.children:
                if elem.name == 'br':
                    lines.append('')
                elif elem.name is None:
                    text = elem.strip()
                    if text:
                        lines.append(text)
            clean_lines = [
                line for line in lines
                if line.strip() and not any(word in line for word in word_lis)
            ]
            ans = ''
            for item in clean_lines:
                ans += '        ' + item + '\n'
            file_path = f'./tmp/{idx}.txt'
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('        ' + title+ '\n' + ans)
        if queue == None:
            print(idx, "重新下载成功")
    except:
        failed_list.append(idx)
        if queue == None:
            print(idx, "重新下载失败")
    finally:
        if queue != None:
            queue.put(1)

def progress_monitor(q, total):
    from tqdm import tqdm
    with tqdm(total=total, desc="下载进度", ncols=80) as pbar:
        while True:
            item = q.get()
            if item is None:
                break
            pbar.update(1)


def delete_tmp_folder(path='./tmp'):
    if os.path.exists(path):
        shutil.rmtree(path)

def merge_txt_files(input_dir='./tmp', bookname="book"):
    output_file = f"./output/{bookname}.txt"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    files = sorted(
        [f for f in os.listdir(input_dir) if f.endswith('.txt')],
        key=lambda x: int(os.path.splitext(x)[0])
    )
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for i, fname in enumerate(files):
            fpath = os.path.join(input_dir, fname)
            with open(fpath, 'r', encoding='utf-8') as chapter_f:
                content = chapter_f.read().strip()
            out_f.write(content)
            if i != len(files) - 1:
                out_f.write('\n')  # 换页 + 空行分隔
    print(f"✅ 合并完成，共 {len(files)} 章，输出到：{output_file}")


if __name__ == '__main__':
    url_lis, bookname = get_list("45814")
    if len(url_lis)!=0:
        with Manager() as manager:
            failed_list = manager.list()
            queue = manager.Queue()
            pool = Pool(processes=20)
            monitor = multiprocessing.Process(target=progress_monitor, args=(queue, len(url_lis)+1))
            monitor.start()
            func = partial(get_single_chapter, url_lis, failed_list=failed_list, queue=queue)
            pool.map(func, range(len(url_lis)))
            pool.close()
            pool.join()
            queue.put(None)
            monitor.join()
            if failed_list:
                print(f"\n❗ 以下章节下载失败（共 {len(failed_list)} 项）：")
                print(list(failed_list))
            else:
                print("\n✅ 所有章节下载成功！")

            for item in failed_list:
                get_single_chapter(url_lis, item)

            merge_txt_files(bookname=bookname)

        # delete_tmp_folder()
