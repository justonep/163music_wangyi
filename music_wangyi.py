# -*- coding: utf-8 -*-
from Crypto.Cipher import AES
import binascii
import os
import base64
import random
import json
import requests
import pygame

# http://blog.csdn.net/qq_28702545/article/details/51719199 看到别人对x-www-form-urlencoded的解释，
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Origin': 'http://music.163.com',
    'Content-Type': 'application/x-www-form-urlencoded'}

ConfuseParametersA = '0CoJUm6Qyw8W8jud'
PublicKey = '010001'
modulus = ('00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7'
           'b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280'
           '104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932'
           '575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b'
           '3ece0462db0a22b8e7')


def create_random_key(size):
    basic = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    mix = ""
    for i in range(0, size):
        mix = mix + basic[int(random.random() * size)]
    return mix


def encrypted_request(text):
    text = json.dumps(text)
    secKey = create_random_key(16)
    encText = aesEncrypt(aesEncrypt(text, ConfuseParametersA), secKey)
    encSecKey = rsaEncrypt(secKey, PublicKey, modulus)
    data = {'params': encText, 'encSecKey': encSecKey}
    return data


def aesEncrypt(text, secKey):
    pad = 16 - len(text) % 16
    text = text + chr(pad) * pad
    encryptor = AES.new(secKey, 2, '0102030405060708')
    ciphertext = encryptor.encrypt(text)
    ciphertext = base64.b64encode(ciphertext).decode('utf-8')
    return ciphertext


def rsaEncrypt(text, pubKey, modulus):
    text = text[::-1]
    rs = pow(int(binascii.hexlify(text), 16), int(pubKey, 16), int(modulus, 16))
    return format(rs, 'x').zfill(256)


# 根据歌曲id获得歌曲的url
def get_dowload_url(id):
    give = {"ids": str([id]), "br": 128000, "csrf_token": ""}
    result = encrypted_request(give)

    response = requests.post('http://music.163.com/weapi/song/enhance/player/url?csrf_token=', headers=headers,
                             data=result)
    result_json = response.content
    result = json.loads(result_json)
    if result['data'][0]['code'] == 404:
        print '这个歌曲消失了'
    else:
        print u'这个歌曲的链接是:' + result['data'][0]['url']
        return result['data'][0]['url']


# 根据搜索词，获得歌曲id

def search_song_ids(name):
    url = 'http://music.163.com/weapi/cloudsearch/get/web?csrf_token='
    give = {"hlpretag": "<span class=\"s-fc7\">", "hlposttag": "</span>", "s": name, "type": "1", "offset": "0",
            "total": "false", "limit": "80", "csrf_token": ""}
    result = encrypted_request(give
                               )
    response = requests.post(url, headers=headers, data=result)
    result_json = response.content
    result = json.loads(result_json)
    temp_result = {}
    for i in result['result']['songs']:
        print u'歌曲名字：' + i['al']['name']
        print u'歌曲id：' + str(i['id'])
        temp_result[str(i['id'])] = i['al']['name']
    print temp_result
    k = raw_input('输入你想点的歌的id:')

    mp3_url = get_dowload_url(int(k))
    print temp_result[k]
    mp3_name = temp_result[k] + '.mp3'

    music_file = open(mp3_name, 'wb+')
    response = requests.get(mp3_url)
    music_file.write(response.content)
    music_file.flush()
    music_file.close()

    play_son(filename=mp3_name)


def play_son(filename):
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode([640, 480])
    pygame.time.delay(1000)
    pygame.mixer.music.load(filename.encode('utf-8'))
    pygame.mixer.music.play()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()


singer = raw_input('输入你想点的歌手:')
print singer
search_song_ids(name=singer)
