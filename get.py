#!/usr/bin/env python3

import requests
import os
from orm import SQL
import hashlib

markets = ['auto', 'ar-XA', 'da-DK', 'de-AT', 'de-CH', 'de-DE', 'en-AU', 'en-CA', 'en-GB',
    'en-ID', 'en-IE', 'en-IN', 'en-MY', 'en-NZ', 'en-PH', 'en-SG', 'en-US', 'en-WW', 'en-XA', 'en-ZA', 'es-AR',
    'es-CL', 'es-ES', 'es-MX', 'es-US', 'es-XL', 'et-EE', 'fi-FI', 'fr-BE', 'fr-CA', 'fr-CH', 'fr-FR',
    'he-IL', 'hr-HR', 'hu-HU', 'it-IT', 'ja-JP', 'ko-KR', 'lt-LT', 'lv-LV', 'nb-NO', 'nl-BE', 'nl-NL',
    'pl-PL', 'pt-BR', 'pt-PT', 'ro-RO', 'ru-RU', 'sk-SK', 'sl-SL', 'sv-SE', 'th-TH', 'tr-TR', 'uk-UA',
    'zh-CN', 'zh-HK', 'zh-TW']


def get_page(index, market='en-WW'):
    per_page = 8
    params = {
        'format': 'js',
        'idx': index,
        'n': per_page,
        'mbl': 1,
        'mkt': market
    }
    image_base = 'https://www.bing.com/HPImageArchive.aspx'

    r = requests.get(image_base, params=params, headers={
        'accept': 'application/json'
    })

    return r.json()['images']


def main():
    directory = 'images'
    db = SQL('images_db')

    if not os.path.exists(directory):
        os.makedirs(directory)

    for market in markets:
        print('')
        print('Getting region...', market)

        for index in range(1):
            for image in get_page(index, market):
                save_image(image, db, directory)


def calc_hash(content):
    hasher = hashlib.sha256()
    hasher.update(content)

    return hasher.hexdigest()

def save_image(image, db, directory):
    bing = 'http://www.bing.com'
    resolution = 'UHD'

    base = image['urlbase']
    filename = base.replace('/th?id=OHR.', '') + '.jpg'
    url = f'{bing}{base}_{resolution}.jpg&qlt=100'
    hsh = image['hsh']

    dst = os.path.join(directory, filename)

    if db.exists(hsh):
        print('[S] Skipping...', filename)
        return

    print('[D] Downloading...', filename)
    r = requests.get(url)

    if r.status_code == 200:
        digest = calc_hash(r.content)

        if db.existsSHA(digest):
            print('[-] Found duplicate...', filename)
            db.create(hsh, digest, filename)
            return

        with open(dst, 'wb') as f:
            f.write(r.content)
        db.create(hsh, digest, filename)


if __name__ == '__main__':
    main()
