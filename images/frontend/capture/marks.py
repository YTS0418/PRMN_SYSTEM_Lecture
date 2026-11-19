# 撮影の設定（shots.py）の読み取り。capture.py と gen_legend.py が使う（Playwright が無くても使える）。
NUMBERS = "①②③④⑤⑥⑦⑧⑨"
DEFAULT_PAD = 12                              # 切り抜きの余白（px）


def normalize_mark(m):
    """マークの指定を、辞書にそろえる。(セレクタ, 番号) の古い書き方も受け付ける。"""
    d = dict(m) if isinstance(m, dict) else {"sel": m[0], "n": m[1]}
    d.setdefault("how", "box")
    d.setdefault("n", None)
    d.setdefault("label", "")
    d.setdefault("nested_ok", False)
    return d


def normalize_clip(c):
    if c is None:
        return None
    if isinstance(c, str):
        return {"sel": c, "pad": DEFAULT_PAD, "how": "box"}
    if isinstance(c, (tuple, list)):
        return {"sel": c[0], "pad": c[1], "how": "box"}
    d = dict(c)
    d.setdefault("pad", DEFAULT_PAD)
    d.setdefault("how", "box")
    return d
