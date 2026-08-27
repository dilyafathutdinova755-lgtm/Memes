# Snapshot of the pairing/render plan used for videos 1-13 (see output/progress.md).
# For a new batch: edit PAIRS below to the next unused photo+hook numbers, then
# run this followed by render_all.sh (see output/video_style.md for the full recipe).
import sys, os
sys.path.insert(0, "/home/user/Memes/scripts")
from shadow_analyze import analyze
from PIL import ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MAXWIDTH = 920
MAXLINES = 4
PHOTO_DIR = "/home/user/Memes"
OUTDIR = os.getcwd()

PAIRS = [
    (1, "IMG_3790.jpeg", "Одиннадцатиклассники, от сердца отрываю это приложение"),
    (2, "IMG_3791.jpeg", "Моя рекомендация по подготовке к ЕГЭ: что занимает минимум времени и усилий но значительно повышает баллы"),
    (3, "IMG_3792.jpeg", "Что ты можешь сделать прямо сейчас чтобы добить тестовую часть по русскому языку"),
    (4, "IMG_3793.jpeg", "Твой шанс бесплатно забрать +30 баллов на ЕГЭ"),
    (5, "IMG_3794.jpeg", "Моя искренняя рекомендация для сдающих ЕГЭ в этом году"),
    (6, "IMG_3795.jpeg", "Как я сэкономила несколько десятков 1000 на подготовки к экзаменам (одно приложение заменило мне всех репетиторов)"),
    (7, "IMG_3796.jpeg", "Хочу сдать русский язык на 85+, но нет денег на репетиторов, что посоветуешь?"),
    (8, "IMG_3879.jpeg", "Хватит переживать из-за ЕГЭ, вот твоё спасение:"),
    (9, "IMG_3880.jpeg", "Что я буду советовать всем одиннадцатиклассникам как человек, который уже сейчас пишет пробники на 75+ баллов"),
    (10, "IMG_3881.jpeg", "Одиннадцатиклассники, вот что я хотела бы знать ещё в сентябре"),
    (11, "IMG_3882.jpeg", "Выпускники 2027, сохраните этот пост, потом спасибо скажете"),
    (12, "IMG_3883.jpeg", "Если готовишься к ЕГЭ только по учебникам — ты теряешь время, вот почему"),
    (13, "IMG_3884.jpeg", "Будущие абитуриенты, вот лайфхак, который экономит часы на подготовке"),
    (14, "IMG_3887.jpeg", "10 минут в день вместо репетитора — звучит нереально? А вот и нет"),
    (15, "IMG_3888.jpeg", "Как готовиться к ЕГЭ, если совсем нет свободного времени"),
    (16, "IMG_3889.jpeg", "Секрет тех, кто готовится к ЕГЭ без нервов и репетиторов"),
    (17, "IMG_3890.jpeg", "Что сделать прямо сейчас, чтобы подтянуть теорию по обществознанию"),
    (18, "IMG_3892.jpeg", "5 минут — и ты закрыл ещё один пробел в теории по биологии"),
    (19, "IMG_3893.jpeg", "Как за неделю повторить всю теорию по русскому, которую забыл за 11 лет"),
    (20, "IMG_3894.jpeg", "Забери бесплатно +20 баллов к ЕГЭ по русскому, пока не поздно"),
    (21, "IMG_3895.jpeg", "Бесплатный способ поднять балл по обществознанию — делюсь без воды"),
    (22, "IMG_3896.jpeg", "Если сдаёшь ЕГЭ в этом году — вот самая честная рекомендация от меня"),
    (23, "IMG_3897.jpeg", "Один репетитор в месяц стоит как год подписки на это приложение"),
]

def wrap(text, font, maxwidth):
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        bbox = font.getbbox(trial)
        width = bbox[2] - bbox[0]
        if width <= maxwidth or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def fit(text, maxwidth=MAXWIDTH, maxlines=MAXLINES, start=64, minsize=40):
    for size in range(start, minsize - 1, -2):
        font = ImageFont.truetype(FONT, size)
        lines = wrap(text, font, maxwidth)
        if len(lines) <= maxlines:
            return size, lines
    font = ImageFont.truetype(FONT, minsize)
    return minsize, wrap(text, font, maxwidth)

plan_lines = []
for idx, photofile, hook_text in PAIRS:
    photo = os.path.join(PHOTO_DIR, photofile)
    size, lines = fit(hook_text)
    textfile = os.path.join(OUTDIR, f"hook{idx}.txt")
    with open(textfile, "w") as f:
        f.write("\n".join(lines))
    r = analyze(photo)
    plan_lines.append(f"{idx}\t{photo}\t{textfile}\t{size}\t{r['shadow_alpha']}\t{r['border_alpha']}\t{r['borderw']}")
    print(f"{idx}: {photofile} fontsize={size} lines={len(lines)} shadow={r['shadow_alpha']} border={r['border_alpha']}/{r['borderw']}px  (brightness={r['mean_brightness']} busyness={r['busyness']})")

with open(os.path.join(OUTDIR, "plan.tsv"), "w") as f:
    f.write("\n".join(plan_lines) + "\n")
