import os
import discord
import asyncio
import time
import random
import pickle
from discord.ext import commands
from pytube import YouTube
from dataclasses import dataclass
from keep_alive import keep_alive

start_flag = True
ans_flag = False
question_flag = False
next_flag = False
grantpoint_flag = False
end_flag = False

play_volume = 1
play_time = 0
audio = None
vc = None
ans_num = None
ans_count = 0
player_count = 0
question_count = 0

answers = []
players = []
musics = []
@dataclass
class Player:
    name: str
    point: int
    ans: str
@dataclass
class Music:
    url: str
    ans: str

"""
# テストデータ
musics.append(Music("https://www.youtube.com/watch?v=vBK9YzkBTJs", "amateras system"))
musics.append(Music("https://www.youtube.com/watch?v=zqMOLz9q7Ig", "幻月環"))
musics.append(Music("https://www.youtube.com/watch?v=gJpUZ8EdxQQ", "Lux -最後の約束-"))
musics.append(Music("https://www.youtube.com/watch?v=kvXTJDpPEXA", "水晶に映る姫君"))
musics.append(Music("https://www.youtube.com/watch?v=xM9C721BaXg", "アクアテラリウム"))
musics.append(Music("https://www.youtube.com/watch?v=-EX0xJ-Wch8", "フクロウ ～フクロウが知らせる客が来たと～"))
musics.append(Music("https://www.youtube.com/watch?v=2h3PfL4TcQ0", "フレスベルグの少女"))
musics.append(Music("https://www.youtube.com/watch?v=85AXrR57WDE", "魔女の子守歌"))
musics.append(Music("https://www.youtube.com/watch?v=GNxUmwVkDPw", "お星さまのラグリマ"))
musics.append(Music("https://www.youtube.com/watch?v=NtJnix-9niI", "鳥の詩"))
"""

TOKEN = os.getenv("DISCORD_TOKEN")

# インテントの生成
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# クライアントの生成
bot = commands.Bot(
    command_prefix="/t_", # /コマンド名　でコマンドを実行できるようになる
    case_insensitive=True, # 大文字小文字を区別しない (/hello も /Hello も同じ!)
    intents=intents # 権限を設定
)

class Question_Client(discord.ui.View):
    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)

    @discord.ui.select(
        cls=discord.ui.Select,
        placeholder="回答を選択してください。",
        options=answers
    )

    async def select(self, ctx: discord.Interaction, select: discord.ui.Select):
        global ans_count
        global player_count

        await ctx.response.send_message(f"{ctx.user.display_name}様が回答を選択しました。")
        for player in players:
            # プレイヤーの回答を記録
            if (ctx.user.display_name == player.name):
                # 現在の回答者数をカウント
                if (player.ans == None):
                    ans_count += 1
                player.ans = select.values[0]
        await ctx.channel.send(f"現在の回答者数:{ans_count}/{player_count}")

    @discord.ui.button(label="play", style=discord.ButtonStyle.success)
    async def play(self, ctx: discord.Interaction, button: discord.ui.Button):
        global play_volume
        global play_time
        global audio
        global vc

        await ctx.response.defer(thinking=False)
        # 音楽を再生
        source = discord.FFmpegPCMAudio(audio.url)
        source = discord.PCMVolumeTransformer(source, volume=play_volume)
        vc.play(source)
        # 設定した秒数経過後音楽を停止
        if (play_time != 0):
            await asyncio.sleep(play_time)
            ctx.guild.voice_client.stop()

# 起動時に動作する処理
@bot.event
async def on_ready():
    global musics
    # 起動したらターミナルにログイン通知が表示される
    print('ログインしました')
    await bot.tree.sync()
    
    # musicsのセーブファイルをロード
    with open('musics_save.pickle', mode='br') as f:
        try:
            musics = pickle.load(f)
        except EOFError:
            print("データなし")
    """
    # answersの復元
    for music in musics:
        answers.append(discord.SelectOption(label=music.ans))
    """
        
# コマンド処理
@bot.tree.command(name="t_help", description="ヘルプを表示するコマンドです。")
async def help(ctx: discord.Interaction):
    await ctx.response.send_message("===============ヘルプ===============")
    await ctx.channel.send('本BotはYoutubeの動画をイントロクイズとして出題するBotとなっております。')
    await ctx.channel.send('本Botが使用可能なコマンドを下記に記載いたします。')
    await ctx.channel.send('/t_help:ヘルプを表示するコマンドです。(/t_help)の形で実行できます。')
    await ctx.channel.send('/t_rule:遊び方を表示するコマンドです。(/t_rule)の形で実行可能です。')
    await ctx.channel.send('/t_add:出題される問題を追加するコマンドです。(/t_add YoutubeURL 問題の答え)の形で実行可能です。')
    await ctx.channel.send('/t_list:出題される問題の一覧を表示するコマンドです。(/t_list)の形で実行可能です。')
    await ctx.channel.send('/t_delete:問題を削除するコマンドです。(/t_delete 問題番号)の形で実行可能です。問題番号は/t_listコマンドで表示される番号です。')
    await ctx.channel.send('/t_reset:全ての問題を削除するコマンドです。(/t_reset)コマンドの形で実行可能です。')
    await ctx.channel.send('/t_config:再生される音楽の音量と再生時間を設定するコマンドです。(/t_config 音量[0.0～1.0] 再生時間[0.0～10.0])の形で実行可能です。また、再生時間を0に設定した場合は音楽がフルで再生されます。')
    await ctx.channel.send('/t_join:ゲームに参加するコマンドです。(/t_join)の形で実行可能です。')
    await ctx.channel.send('/t_leave:ゲームから退出するコマンドです。(/t_leave)の形で実行可能です。')
    await ctx.channel.send('/t_start:ゲームを開始するコマンドです。(/t_start)の形で実行可能です。')
    await ctx.channel.send('/t_question:問題を出題するコマンドです。(/t_question)の形で実行可能です。')
    await ctx.channel.send('/t_next:出題された問題の答えを表示するコマンドです。(/t_next)の形で実行可能です。')
    await ctx.channel.send('/t_grantpoint:指定したプレイヤーにポイントを付与するコマンドです。(/t_grantpoint プレイヤー名 付与するポイント数)の形で実行可能です。')
    await ctx.channel.send('/t_end:ゲームを終了するコマンドです。(/t_end)の形で実行可能です。')
    await ctx.channel.send('以上が実行可能なコマンドとなっております。')
    await ctx.channel.send('その他不明点がございましたら気軽に夢幻までお問い合わせください。')

@bot.tree.command(name="t_rule", description="遊び方を表示するコマンドです。")
async def rule(ctx: discord.Interaction):
    await ctx.response.send_message("===============遊び方===============")
    await ctx.channel.send('1.ボイスチャンネルに接続してください。')
    await ctx.channel.send('2.(/t_join)コマンドでゲームに参加してください。')
    await ctx.channel.send('3.全員がゲームに参加したらどなたか一人が代表して(/t_start)コマンドを実行してください。')
    await ctx.channel.send('4.ゲームがスタートしたらどなたか一人が代表して(/t_question)コマンドを実行してください。')
    await ctx.channel.send('5.(/t_question)コマンドを実行すると音楽が再生され、回答群が表示されますのでご回答ください。また、"play"ボタンを押下すると音楽をもう一度再生することができます。')
    await ctx.channel.send('6.全員の回答が終わりましたらどなたか一人が代表して(/t_next)コマンドを実行してください。')
    await ctx.channel.send('7.(/t_next)コマンドを実行すると正解が表示され、正解者にポイントが付与されます。')
    await ctx.channel.send('8.あとは飽きるまで4～7を繰り返してください。')
    await ctx.channel.send('9.ゲームを終了したくなった場合は、どなたか一人が代表して(/t_end)コマンドを実行してください。')
    await ctx.channel.send('10.(/t_end)コマンドを実行するとゲームが終了し、一番ポイントが多かったプレイヤーが優勝となります。')

@bot.tree.command(name="t_add", description="問題を追加するコマンドです。")
async def add(ctx: discord.Interaction, url: str, ans: str):
    # 音楽の登録処理
    await ctx.response.send_message("問題を追加しています......")
    musics.append(Music(url, ans))
    # 現在のmusicsをセーブファイルに保存
    with open('musics_save.pickle', mode='wb') as f:
        pickle.dump(musics, f)
    await ctx.channel.send("問題を追加しました。")

@bot.tree.command(name="t_list", description="問題の一覧を表示するコマンドです。")
async def list(ctx: discord.Interaction):
    num = 1

    # 問題の一覧を表示
    await ctx.response.send_message("問題の一覧を表示します......")
    for music in musics:
        await ctx.channel.send(f"{num}:{music.ans}")
        num += 1
    await ctx.channel.send("問題の一覧を表示しました。")
    
@bot.tree.command(name="t_delete", description="問題を削除するコマンドです。")
async def delete(ctx: discord.Interaction, num: int):
    await ctx.response.send_message("問題を削除しています......")
    # 指定した問題を削除
    try:
        del musics[num-1]
        # 現在のmusicsをセーブファイルに保存
        with open('musics_save.pickle', mode='wb') as f:
            pickle.dump(musics, f)
        await ctx.channel.send("問題を削除しました。")
    except Exception as e:
        await ctx.channel.send("指定した問題が見つかりませんでした。")
        raise e

@bot.tree.command(name="t_reset", description="全ての問題を削除するコマンドです。")
async def reset(ctx: discord.Interaction):
    if (ctx.user.display_name == "夢幻"):
        # 全ての問題を削除
        await ctx.response.send_message("全ての問題を削除しています......")
        musics.clear()
        # 現在のmusicsをセーブファイルに保存
        with open('musics_save.pickle', mode='wb') as f:
            pickle.dump(musics, f)
        await ctx.channel.send("全ての問題を削除しました。")
    else:
        await ctx.response.send_message("あなたにはこのコマンドを実行する権限がありません。")

@bot.tree.command(name="t_config", description="音量と再生時間を設定するコマンドです。")
async def config(ctx: discord.Interaction, volume: float, time: float):
    global play_volume
    global play_time

    if (volume >= 0.0 and volume <= 1.0):
        if (time >= 0.0 and time <= 10.0):
            # 音量と再生時間を設定
            play_volume = volume
            play_time = time
            await ctx.response.send_message(f"音量を{play_volume}, 再生時間を{play_time}に設定しました。")
        else:
            await ctx.response.send_message("再生時間は[0.0～10.0]で指定してください。")
    else:
        await ctx.response.send_message("音量は[0.0～1.0]で指定してください。")


@bot.command()
async def join(ctx: commands.Context):
    global player_count

    # 参加プレイヤーの重複チェック
    for player in players:
        if (ctx.author.display_name == player.name):
            await ctx.author.send("あなたは既にゲームに参加しています。")
            return
    # 参加プレイヤーを追加する
    await ctx.channel.send(f"{ctx.author.display_name}様がゲームに参加しました。")
    players.append(Player(ctx.author.display_name, 0, None))
    player_count += 1
    await ctx.channel.send(f"現在のプレイヤー数:{player_count}人")

@bot.command()
async def leave(ctx: commands.Context):
    global player_count

    # 参加プレイヤーを削除する
    for player in players:
        if (ctx.author.display_name == player.name):
            await ctx.channel.send(f"{ctx.author.display_name}様がゲームから退出しました。")
            players.remove(player)
            player_count -= 1
            await ctx.channel.send(f"現在のプレイヤー数:{player_count}人")
            return
    await ctx.author.send("あなたはゲームに参加していません。")
    
@bot.command()
async def start(ctx: commands.Context):
    global start_flag
    global question_flag
    global grantpoint_flag
    global end_flag
    global vc

    if (start_flag == True):
        # botをボイスチャンネルに接続
        try:
            await ctx.message.author.voice.channel.connect()
            vc = ctx.guild.voice_client
        except Exception as e:
            await ctx.author.send("ボイスチャンネルに参加してから実行してください。")
            raise e
        # ゲームスタート
        await ctx.channel.send("ゲームスタート！！")
        await ctx.channel.send("==========現在のポイント数==========")
        for player in players:
            await ctx.channel.send(f"{player.name}様:{str(player.point)}pt")
        # flag処理
        start_flag = False # /startを無効化
        question_flag = True # /questionを有効化
        grantpoint_flag = True # /grantpointを有効化
        end_flag = True # /endを有効化
        await ctx.channel.send("====================================")
    else:
        await ctx.author.send("(/t_start)はゲーム中に使用できません。")

@bot.command()
async def question(ctx: commands.Context):
    global question_flag
    global next_flag
    global question_count
    global ans_num
    global audio
    used = []
    dammy_num = 0
    count = 0

    if (question_flag == True): 
        question_flag = False # /t_questionコマンドを無効化
        try:
            question_count += 1
            await ctx.channel.send(f"第{question_count}問")
            ans_num = random.randint(0, (len(musics)-1))
        except Exception as e:
            await ctx.channel.send("出題する問題がありません。")
            await ctx.channel.send("問題を追加してからお楽しみください。")
            raise e
        # 音楽を再生
        try:
            yt = YouTube(musics[ans_num].url)
            streams = yt.streams
            audio = streams.filter(only_audio=True).order_by('abr').last()
            source = discord.FFmpegPCMAudio(audio.url)
            source = discord.PCMVolumeTransformer(source, volume=play_volume)
            vc.play(source)
        except Exception as e:
            await ctx.channel.send("問題設定中にエラーが発生しました。")
            await ctx.channel.send(f"対象楽曲:{musics[ans_num].ans}")
            next_flag = True # /t_nextコマンドを有効化
            raise e
        # 設定した秒数経過後音楽を停止
        if (play_time != 0):
            await asyncio.sleep(play_time)
            ctx.guild.voice_client.stop()
        # ダミー回答生成処理
        while count < 9:
            dammy_num = random.randint(0, (len(musics)-1))
            # -ここの処理はそのうち最適化したい-
            # dammy_ans用の音楽が4曲以下だったとき
            if (len(answers) >= (len(musics)-1)):
                break
            # 乱数値が正解の音楽だったときもしくはもう既に使われているダミー音楽だったとき
            if (dammy_num == ans_num or dammy_num in used):
                continue
            answers.append(discord.SelectOption(label=musics[dammy_num].ans))
            used.append(dammy_num)
            count += 1
        # 正解を挿入
        answers.insert(random.randint(0, (len(answers)-1)), discord.SelectOption(label=musics[ans_num].ans))
        # 答案生成処理
        view = Question_Client(timeout=None)
        await ctx.channel.send(view=view)
        next_flag = True # /t_nextを有効化
    else:
        await ctx.author.send("(/t_question)コマンドはゲーム開始直後もしくは(/t_next)コマンド実行直後のみ使用可能です。")

@bot.command()
async def next(ctx: commands.Context):
    global question_flag
    global next_flag
    global ans_num
    global ans_count

    if (next_flag == True):
        next_flag = False # /t_nextを無効化
        # 音楽を停止
        await asyncio.sleep(play_time)
        ctx.guild.voice_client.stop()
        await ctx.channel.send(f"正解は[{musics[ans_num].ans}]でした！！")
        await ctx.channel.send("==========正解者==========")
        # 正解したプレイヤーにポイントを付与する
        for player in players:
            if (musics[ans_num].ans == player.ans):
                await ctx.channel.send(f"{player.name}様")
                player.point += 1
        await ctx.channel.send("正解者にはポイントを付与いたします。")
        await ctx.channel.send("==========現在のポイント数==========")
        # プレイヤーのポイント数を出力し、回答を初期化
        for player in players:
            await ctx.channel.send(f"{player.name}様:{str(player.point)}pt")
            player.ans = None

        answers.clear() # 答案を初期化
        ans_count = 0 # 回答者数を初期化
        question_flag = True # /t_questionコマンドを有効化
        await ctx.channel.send("====================================")
    else:
        await ctx.author.send("(/t_next)コマンドは(/t_question)コマンド実行直後のみ使用可能です。")

@bot.command()
async def grantpoint(ctx: commands.Context, name: str, point: int):
    if (grantpoint_flag == True):
        for player in players:
            # 指定したプレイヤーを検索
            if (name == player.name):
                # 指定したプレイヤーに指定したポイント数を付与
                await ctx.channel.send(f"{name}様に{point}pt付与しました。")
                player.point = player.point + point
                return
        await ctx.author.send("指定したプレイヤーはゲームに参加していません。")

@bot.command()
async def end(ctx: commands.Context):
    global start_flag
    global question_flag
    global grantpoint_flag
    global end_flag
    global player_count
    global question_count

    victory_name = None
    max_point = 0
    gifts = [
        "ペア10日間の血管旅行券",
        "汚部屋清掃員加入券(強制)",
        "路地裏招待券",
        ]

    if (end_flag == True):
        await ctx.channel.send("ゲーム終了！！")
        await ctx.channel.send("優勝は.........")
        time.sleep(5)
        # 優勝プレイヤーを選定する
        for player in players:
            if (max_point <= player.point):
                victory_name = player.name
                max_point = player.point
        await ctx.channel.send(f"{victory_name}様！！！！！！！！！！")
        time.sleep(3)
        await ctx.channel.send(f"優勝した{victory_name}様には、{gifts[random.randint(0, 2)]}をお持ち帰りいただきます。")
        time.sleep(3)
        await ctx.channel.send("おめでとうございました！！！！！！！！！！")
        # botをボイスチャンネルから切断
        await ctx.guild.voice_client.disconnect()
        # 初期化処理
        start_flag = True # /startを有効化
        question_flag = False # /questionを無効化
        grantpoint_flag = False # /grantpointを無効化
        end_flag = False # /endを無効化
        players.clear() # 全参加プレイヤーを削除
        player_count = 0 # プレイヤーカウントを初期化
        question_count = 0 # 問題カウントを初期化
    else:
        await ctx.author.send("(/t_end)はゲーム中のみ使用可能です。")

# Webサーバの立ち上げ
keep_alive()
# Botの起動とDiscordサーバーへの接続
bot.run(TOKEN)