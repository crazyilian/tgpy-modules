"""
    description: get most positive and negative messages in chat & get mood of one message
    name: mood
    needs_pip:
      dostoevsky: dostoevsky
    version: 0.2.0
"""
from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
import dostoevsky.data
import os
from datetime import datetime
from operator import itemgetter
import telethon

tokenizer = RegexTokenizer()
model = FastTextSocialNetworkModel(tokenizer=tokenizer)


def install_fasttext():
    source, destination = dostoevsky.data.AVAILABLE_FILES['fasttext-social-network-model']
    destination_path = os.path.join(dostoevsky.data.DATA_BASE_PATH, destination)
    if not os.path.exists(destination_path):
        downloader = dostoevsky.data.DataDownloader()
        downloader.download(source=source, destination=destination)


async def predict_and_get_top_results(ids, texts, title, msg):
    results = model.predict(texts, k=2)
    dict_pos = {}
    dict_neg = {}
    for id, res in zip(ids, results):
        if 'positive' in res:
            dict_pos[id] = res['positive']
        if 'negative' in res:
            dict_neg[id] = res['negative']
    list_pos = reversed(sorted(dict_pos.items(), key=itemgetter(1)))[:5]
    list_neg = reversed(sorted(dict_neg.items(), key=itemgetter(1)))[:5]
    if msg.chat or isinstance(msg.chat, telethon.tl.types.User):
        txt = f'TOP positive messages ' + title + ':'
        for id, val in list_pos:
            txt = txt + f'\nlink: t.me/c/{msg.chat.id}/{id}\nval: {val}'
        await msg.reply(txt)
        txt = f'TOP negative messages ' + title + ':'
        for id, val in list_neg:
            txt = txt + f'\nlink: t.me/c/{msg.chat.id}/{id}\nval: {val}'
        await msg.reply(txt)
    else:
        for id, val in list_neg:
            await msg.respond(f'positive: {val}', reply_to=id)
        for id, val in list_pos:
            await msg.respond(f'negative: {val}', reply_to=id)


def extract_text(msg):
    try:
        text = msg.raw_text
    except:
        return None
    if not isinstance(text, str) or len(text) < 5:
        return None
    return text


async def topmood(days=1, cnt=None):
    if cnt is not None:
        days = None
    msg = ctx.msg
    ct = datetime.now().astimezone()
    texts = []
    ids = []
    cnt_messages = 0
    async for mess in client.iter_messages(msg.chat_id):
        if days:
            if (ct - mess.date).days >= days:
                break
        if cnt:
            if cnt_messages >= cnt:
                break
        text = extract_text(mess)
        if text:
            texts.append(mess.text)
            ids.append(mess.id)
            cnt_messages += 1
    title = None
    if days is None:
        title = f'among the last {cnt}'
    elif days == 1:
        title = 'of the day'
    elif days > 1:
        title = f'of the last {days} days'
    await predict_and_get_top_results(ids, texts, title, msg)
    return 'Done'


async def sentiment():
    msg = await ctx.msg.get_reply_message()
    txt = msg.text
    res = model.predict([txt])[0]
    return '\n' + '\n'.join(map(lambda el: f'{el[0]}: {round(el[1], 7)}',
                                filter(lambda el: el[1] > 0.0001, sorted(res.items(), key=lambda el: -el[1]))))


install_fasttext()

__all__ = ['sentiment', 'topmood']
