import setting
import discord
from googlesearch import search
from discord.ext import commands

# チェンネルID
TOKEN = setting.TOKEN
CHANNEL_ID = setting.CHANNEL_ID

# 役職ID
POSITION_CLEE = setting.POSITION_CLEE

# 対応した絵文字
EMOJI_CLEE = 'EMOJI_CLEE'

# 絵文字配列
EMOJI_LIST = ['EMOJI_CLEE']


####################
# 接続に必要なオブジェクトを生成
####################
Intents = discord.Intents.default()
Intents.members = True
presence = discord.Game("エヴァンゲリオン") # プレイ中
client = discord.Client(intents=Intents, activity=presence)


##########
# 起動時
##########
# 任意のチャンネルで挨拶する非同期関数を定義
async def greet():
    channel = client.get_channel(CHANNEL_ID)
    await channel.send('私は大人だからね！ (login)')

# bot起動時に実行されるイベントハンドラを定義
@client.event
async def on_ready():
    print('Logged in as')
    print('name:{}'.format(client.user.name))
    print('user_id:{}'.format(client.user.id))
    print('------')
    await greet() # 挨拶する非同期関数を実行


##############
# リアクションと役職
##############
# 役職を付与する非同期関数を定義
async def grant_role(payload):
    # 絵文字が異なる場合は処理終了
    if not payload.emoji.name in EMOJI_LIST:
        return
    # チャンネルが異なる場合は処理を終了
    if payload.channel_id != CHANNEL_ID:
        return

    # 指定の絵文字の場合
    if payload.emoji.name == EMOJI_CLEE:
        # MemberとRoleを取得して役職を付与
        member = payload.member # Member情報を取得
        role = member.guild.get_role(POSITION_CLEE) # 付与するRoleをID指定で取得
        await member.add_roles(role) # 付与
    return member, role

# 役職を剥奪する非同期関数を定義
async def deprived_role(payload):
    # 絵文字が異なる場合は処理終了
    if not payload.emoji.name in EMOJI_LIST:
        return
    # チャンネルが異なる場合は処理を終了
    if payload.channel_id != CHANNEL_ID:
        return

    # 指定の絵文字の場合
    if payload.emoji.name == EMOJI_CLEE:
        guild = client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id) # メンバー名を取得
        print(member)
        role = member.guild.get_role(POSITION_CLEE) # 剥奪するRoleをID指定で取得
        await member.remove_roles(role) # 剥奪
    return member, role

# リアクション追加時に実行されるイベントハンドラを定義
@client.event
async def on_raw_reaction_add(payload):
    # 役職を付与する非同期関数を実行して Optional[Member] オブジェクトを取得
    member, role = await grant_role(payload)
    if member is not None: # 役職を付与したメンバーがいる時
        text = f'{member.mention} 役職自動付与：{role}'
        await client.get_channel(CHANNEL_ID).send(text)

'''
# リアクション解除時に実行されるイベントハンドラを定義
@client.event
async def on_raw_reaction_remove(payload):
    print(payload)
    # 役職を剥奪する非同期関数を実行して Optional[Member] オブジェクトを取得
    member, role = await deprived_role(payload)
    if member is not None: # 役職を剥奪したメンバーがいる時
        text = f'{member.mention} 役職自動剥奪：{role}'
        await client.get_channel(CHANNEL_ID).send(text)
'''


####################
# メッセージに対するアクション
####################
# コマンドに対応するリストデータを取得する関数を定義
def get_data(message):
    print("{}".format(message))
    command = message.content
    data_table = {
        '/members': message.guild.members, # メンバーのリスト
        '/roles': message.guild.roles, # 役職のリスト
        '/text_channels': message.guild.text_channels, # テキストチャンネルのリスト
        '/voice_channels': message.guild.voice_channels, # ボイスチャンネルのリスト
        '/category_channels': message.guild.categories, # カテゴリチャンネルのリスト
    }
    return data_table.get(command, '無効なコマンドです')

# 返信する非同期関数を定義
async def reply(message):
    reply = f'{message.author.mention} Thanks message!' # 返信メッセージの作成
    await message.channel.send(reply) # 返信メッセージを送信

##############
### Mode #######
### 1 : Google検索
##############
mode_flag = 0 # モードフラグ

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    global mode_flag

    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return

    # 発言時に実行されるイベントハンドラを定義
    if client.user in message.mentions: # 話しかけられたかの判定
        await reply(message) # 返信する非同期関数を実行

    # 「/Hello」と発言したら「こんにちは」が返る
    if message.content == '/Hello':
        await message.channel.send('Hello!')
    # 終了コマンド
    if message.content == '/exit':
        await client.logout()
        #await sys.exit()
    # コマンドに対応するデータを取得して表示
    print(get_data(message))


    # Google検索モード
    if mode_flag == 1:
        mode_flag = 0
        count = 0
        search_str = message.content
        # 日本語で検索した上位3券を表示
        for url in search(search_str, lang="jp", num = 3):
            await message.channel.send(url)
            count +=1
            if count == 3:
                break

    # Google検索モード切り替え
    if message.content == '/google':
        mode_flag = 1
        await message.channel.send('検索ワードを入力してね！')



# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
