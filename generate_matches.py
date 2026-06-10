#!/usr/bin/env python3
"""
生成球员近10场比赛数据 —— 基于2026世界杯前真实足球赛历
时间范围：2026年3月初 ~ 2026年6月5日（世界杯开幕前一周）
覆盖赛事：各国联赛收官轮、欧冠淘汰赛、国内杯赛、国家队热身赛
"""
import re, json, random, hashlib
from datetime import date, timedelta

# ============================================================
# 第一部分：定义 2026 赛季真实赛程模板（按周排列）
# 基准日：2026-06-05（世界杯前约1周，作为"最近一场比赛"的参考点）
# ============================================================

BASE_DATE = date(2026, 6, 5)

# ---- 欧冠 2025/26 赛季（基于真实赛程）----
# 1/8决赛次回合：3月上旬
UCL_RO16_2ND = [date(2026,3,4), date(2026,3,5), date(2026,3,11), date(2026,3,12)]
# 1/4决赛：4月8-16日
UCL_QF        = [date(2026,4,8), date(2026,4,9), date(2026,4,15), date(2026,4,16)]
# 半决赛：4月29日-5月7日
UCL_SF        = [date(2026,4,29),date(2026,4,30),date(2026,5,6), date(2026,5,7)]
# 决赛：5月23日（巴黎圣日耳曼 vs 阿森纳，巴黎 4-2 夺冠）
UCL_FINAL     = date(2026, 5, 23)
UCL_FINAL_HOME = "巴黎圣日耳曼(法国)"
UCL_FINAL_AWAY = "阿森纳(英格兰)"
UCL_FINAL_SCORE = "4-2"  # 巴黎圣日耳曼夺冠

# ============================================================
# 欧冠 2025/26 赛季晋级路线（硬编码，确保决赛=巴黎vs阿森纳）
# ============================================================

# 各俱乐部欧冠最深晋级阶段 ("ro16" | "qf" | "sf" | "final")
# 注意：key 必须与 CLUB_INFO 和 teamSquads.js 中的俱乐部名一致
UCL_PROGRESS = {
    # 冠军 + 亚军（有决赛）
    "巴黎圣日耳曼(法国)":         "final",
    "阿森纳(England)":            "final",
    "阿森纳(英格兰)":             "final",
    # 四强（有半决赛）
    "马德里竞技(西班牙)":         "sf",      # 马竞进四强，半决赛负于阿森纳
    "马德里竞技":                   "sf",
    "拜仁慕尼黑(Germany)":        "sf",     # 拜仁进四强，半决赛负于巴黎
    "拜仁慕尼黑(德国)":           "sf",
    # 十六强（止步1/8决赛）
    "皇家马德里(西班牙)":         "ro16",    # 皇马止步16强
    "皇家马德里":                 "ro16",
    "国际米兰(Italy)":            "qf",      # 国米止步八强（被拜仁淘汰）
    "国际米兰(意大利)":           "qf",
    "曼城(English)":               "qf",      # 曼城止步八强（被阿森纳淘汰）
    "曼城(England)":              "qf",
    "曼城(英格兰)":               "qf",
    "巴塞罗那(Spain)":            "qf",      # 巴萨止步八强（被马竞淘汰）
    "巴塞罗那(西班牙)":           "qf",
    "多特蒙德(Germany)":          "qf",      # 多特止步八强（被巴黎淘汰）
    "多特蒙德(德国)":             "qf",
}

# 半决赛对阵（4月29日-5月7日）
# 格式：俱乐部 → (对手, 该俱乐部是否获胜)
# 正确对阵（2026）：阿森纳 vs 皇马，巴黎 vs 拜仁
# 晋级逻辑：阿森纳 & 巴黎 进决赛 → 他们必须赢下半决赛
UCL_SF_FIXTURES = {
    # 半决赛1：阿森纳 胜 马德里竞技 → 阿森纳进决赛
    "阿森纳(England)":            ("马德里竞技(西班牙)",        True),    # 阿森纳胜
    "阿森纳(英格兰)":             ("马德里竞技(西班牙)",         True),
    "马德里竞技(西班牙)":         ("阿森纳(England)",            False),  # 马竞技负
    "马德里竞技":                   ("阿森纳(England)",             False),
    # 半决赛2：巴黎 胜 拜仁 → 巴黎进决赛
    "巴黎圣日耳曼(法国)":         ("拜仁慕尼黑(德国)",           True),   # 巴黎胜
    "拜仁慕尼黑(Germany)":        ("巴黎圣日耳曼(法国)",          False),  # 拜仁负
    "拜仁慕尼黑(德国)":           ("巴黎圣日耳曼(法国)",           False),
}

# 1/4决赛对阵（4月8-16日）
# 格式：俱乐部 → (对手, 是否主场获胜)
UCL_QF_FIXTURES = {
    # QF1：阿森纳 淘汰 曼城 -> 阿森纳进四强
    "阿森纳(England)":            ("曼城(English)",               True),
    "阿森纳(英格兰)":             ("曼城(English)",               True),
    "曼城(English)":               ("阿森纳(England)",            False),
    "曼城(England)":              ("阿森纳(England)",             False),
    "曼城(英格兰)":               ("阿森纳(英格兰)",              False),
    # QF2：马德里竞技 淘汰 巴塞罗那 -> 马竞进四强
    "马德里竞技(西班牙)":         ("巴塞罗那(西班牙)",           True),
    "马德里竞技":                   ("巴塞罗那(西班牙)",          True),
    "巴塞罗那(Spain)":            ("马德里竞技(西班牙)",          False),
    "巴塞罗那(西班牙)":          ("马德里竞技(西班牙)",           False),
    # QF3：巴黎 淘汰 多特 -> 巴黎进四强
    "巴黎圣日耳曼(法国)":         ("多特蒙德(德国)",             True),
    "多特蒙德(Germany)":          ("巴黎圣日耳曼(法国)",          False),
    "多特蒙德(德国)":             ("巴黎圣日耳曼(法国)",           False),
    # QF4：拜仁 淘汰 国米 -> 拜仁进四强
    "拜仁慕尼黑(Germany)":        ("国际米兰(意大利)",           True),
    "拜仁慕尼黑(德国)":           ("国际米兰(Italy)",              True),
    "国际米兰(Italy)":            ("拜仁慕尼黑(Germany)",          False),
    "国际米兰(意大利)":           ("拜仁慕尼黑(Germany)",           False),
}

# 1/8决赛对手（3月4-12日）
UCL_RO16_OPPONENTS = {
    "阿森纳(England)":            "葡萄牙体育(葡萄牙)",
    "阿森纳(英格兰)":             "葡萄牙体育(葡萄牙)",
    "葡萄牙体育(葡萄牙)":        "阿森纳(英格兰)",
    "巴黎圣日耳曼(法国)":         "亚特兰大(意大利)",
    "亚特兰大(Italy)":            "巴黎圣日耳曼(法国)",
    "亚特兰大(意大利)":          "巴黎圣日耳曼(法国)",
    "皇家马德里(西班牙)":         "勒沃库森",
    "曼城(England)":              "尤文图斯(意大利)",
    "曼城(英格兰)":               "尤文图斯(意大利)",
    "拜仁慕尼黑(Germany)":        "凯尔特人(苏格兰)",
    "拜仁慕尼黑(德国)":           "凯尔特人(苏格兰)",
    "巴塞罗那(Spain)":            "那不勒斯(意大利)",
    "巴塞罗那(西班牙)":          "那不勒斯(意大利)",
    "那不勒斯(Italy)":            "巴塞罗那(Spain)",
    "那不勒斯(意大利)":          "巴塞罗那(Spain)",
    "国际米兰(Italy)":            "费耶诺德(荷兰)",
    "国际米兰(意大利)":           "费耶诺德(荷兰)",
    "多特蒙德(Germany)":          "阿斯顿维拉(英格兰)",
    "多特蒙德(德国)":             "阿斯顿维拉(英格兰)",
    "阿斯顿维拉(England)":       "多特蒙德(Germany)",
    "阿斯顿维拉(英格兰)":        "多特蒙德(Germany)",
    "勒沃库森":                   "皇家马德里(西班牙)",
    "AC米兰(Italy)":              "切尔西(英格兰)",
    "AC米兰(意大利)":            "切尔西(英格兰)",
    "切尔西(England)":            "AC米兰(Italy)",
    "切尔西(英格兰)":            "AC米兰(Italy)",
    "纽卡斯尔联":                "国际米兰(Italy)",
    "马德里竞技(西班牙)":         "勒沃库森",
    "莱比锡红牛":                 "马德里竞技(西班牙)",
}
# 英超：5月17日收官
EPL_FINAL_ROUNDS = [
    ("EPL", date(2026,3,14)), ("EPL", date(2026,3,21)), ("EPL", date(2026,4,4)),
    ("EPL", date(2026,4,11)), ("EPL", date(2026,4,18)), ("EPL", date(2026,4,25)),
    ("EPL", date(2026,5,2)),  ("EPL", date(2026,5,9)),  ("EPL", date(2026,5,17)),
]
# 西甲：5月24日收官
LALIGA_FINAL_ROUNDS = [
    ("LAL", date(2026,3,15)), ("LAL", date(2026,3,22)), ("LAL", date(2026,4,5)),
    ("LAL", date(2026,4,12)), ("LAL", date(2026,4,19)), ("LAL", date(2026,4,26)),
    ("LAL", date(2026,5,3)),  ("LAL", date(2026,5,10)), ("LAL", date(2026,5,17)),
    ("LAL", date(2026,5,24)),
]
# 德甲：5月16日收官
BUNDESLIGA_FINAL_ROUNDS = [
    ("BL1", date(2026,3,13)), ("BL1", date(2026,3,20)), ("BL1", date(2026,4,4)),
    ("BL1", date(2026,4,11)), ("BL1", date(2026,4,18)), ("BL1", date(2026,4,25)),
    ("BL1", date(2026,5,2)),  ("BL1", date(2026,5,9)),  ("BL1", date(2026,5,16)),
]
# 意甲：5月24日收官
SERIEA_FINAL_ROUNDS = [
    ("SEA", date(2026,3,15)), ("SEA", date(2026,3,22)), ("SEA", date(2026,4,5)),
    ("SEA", date(2026,4,12)), ("SEA", date(2026,4,19)), ("SEA", date(2026,4,26)),
    ("SEA", date(2026,5,3)),  ("SEA", date(2026,5,10)), ("SEA", date(2026,5,17)),
    ("SEA", date(2026,5,24)),
]
# 法甲：5月16日收官
LIGUE1_FINAL_ROUNDS = [
    ("FR1", date(2026,3,14)), ("FR1", date(2026,3,21)), ("FR1", date(2026,4,4)),
    ("FR1", date(2026,4,11)), ("FR1", date(2026,4,18)), ("FR1", date(2026,4,25)),
    ("FR1", date(2026,5,2)),  ("FR1", date(2026,5,9)),  ("FR1", date(2026,5,16)),
]

# ---- 国内杯赛决赛 ----
FA_CUP_FINAL       = date(2026, 5, 16)   # 足总杯决赛
COPA_DEL_REY_FINAL = date(2026, 4, 25)   # 国王杯决赛
DFB_POKAL_FINAL    = date(2026, 5, 23)   # 德国杯决赛
COPPA_ITALIA_FINAL = date(2026, 5, 20)   # 意大利杯决赛
COUPE_DE_FRANCE_F  = date(2026, 5, 9)    # 法国杯决赛

# ---- 国家队热身赛 / 世界杯前友谊赛（5月底-6月初）----
NT_FRIENDLIES = [
    (date(2026,5,23), "FRI"),  # 第1场友谊赛
    (date(2026,5,27), "FRI"),  # 第2场友谊赛
    (date(2026,5,31), "FRI"),  # 第3场（部分球队）
    (date(2026,6,4),  "FRI"),  # 最后一场赛前热身
]

# ---- 其他联赛（沙特、巴西、墨西哥、阿根廷等）----
SAUDI_MATCHES = [
    ("SAD", date(2026,3,7)), ("SAD", date(2026,3,14)), ("SAD", date(2026,3,21)),
    ("SAD", date(2026,3,28)), ("SAD", date(2026,4,4)),  ("SAD", date(2026,4,11)),
    ("SAD", date(2026,4,18)), ("SAD", date(2026,4,25)), ("SAD", date(2026,5,2)),
    ("SAD", date(2026,5,9)),
]
BRAZIL_MATCHES = [
    ("BRA", date(2026,4,5)), ("BRA", date(2026,4,12)), ("BRA", date(2026,4,19)),
    ("BRA", date(2026,4,26)), ("BRA", date(2026,5,3)),  ("BRA", date(2026,5,10)),
    ("BRA", date(2026,5,17)), ("BRA", date(2026,5,24)),
]
MEXICO_MATCHES = [
    ("MEX", date(2026,3,7)), ("MEX", date(2026,3,15)), ("MEX", date(2026,3,22)),
    ("MEX", date(2026,3,29)), ("MEX", date(2026,4,5)),  ("MEX", date(2026,4,12)),
    ("MEX", date(2026,4,19)),  # 季后赛开始
    ("MEX", date(2026,4,26)), ("MEX", date(2026,5,3)),
]
ARGENTINA_MATCHES = [
    ("ARG", date(2026,3,7)), ("ARG", date(2026,3,16)), ("ARG", date(2026,3,23)),
    ("ARG", date(2026,3,30)), ("ARG", date(2026,4,6)),  ("ARG", date(2026,4,13)),
    ("ARG", date(2026,4,20)), ("ARG", date(2026,4,27)), ("ARG", date(2026,5,4)),
    ("ARG", date(2026,5,11)),
]
PORTUGAL_MATCHES = [
    ("POR", date(2026,3,8)), ("POR", date(2026,3,15)), ("POR", date(2026,3,22)),
    ("POR", date(2026,3,29)), ("POR", date(2026,4,5)),  ("POR", date(2026,4,12)),
    ("POR", date(2026,4,19)), ("POR", date(2026,4,26)), ("POR", date(2026,5,3)),
    ("POR", date(2026,5,10)),
]
NETHERLANDS_MATCHES = [
    ("NED", date(2026,3,8)), ("NED", date(2026,3,15)), ("NED", date(2026,3,22)),
    ("NED", date(2026,3,29)), ("NED", date(2026,4,5)),  ("NED", date(2026,4,12)),
    ("NED", date(2026,4,19)), ("NED", date(2026,4,26)), ("NED", date(2026,5,3)),
    ("NED", date(2026,5,10)),
]
BELGIUM_MATCHES = [
    ("BEL", date(2026,3,7)), ("BEL", date(2026,3,14)), ("BEL", date(2026,3,21)),
    ("BEL", date(2026,3,28)), ("BEL", date(2026,4,4)),  ("BEL", date(2026,4,11)),
    ("BEL", date(2026,4,18)), ("BEL", date(2026,4,25)), ("BEL", date(2026,5,2)),
    ("BEL", date(2026,5,9)),
]
SCOTLAND_MATCHES = [
    ("SCO", date(2026,3,7)), ("SCO", date(2026,3,14)), ("SCO", date(2026,3,21)),
    ("SCO", date(2026,3,28)), ("SCO", date(2026,4,4)),  ("SCO", date(2026,4,11)),
    ("SCO", date(2026,4,18)), ("SCO", date(2026,4,25)), ("SCO", date(2026,5,2)),
    ("SCO", date(2026,5,9)),
]


# ============================================================
# 第二部分：俱乐部完整信息（含联赛归属+欧冠资格+杯赛对手）
# ============================================================

CLUB_INFO = {
    # ===== 英超 (EPL) =====
    "阿森纳(英格兰)": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": True,  # 欧冠球队
        "fa_cup": True,  # 足总杯深阶段
        "opponents_epl": ["曼城","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿","富勒姆","西汉姆联"],
        "ucl_opponents": ["拜仁慕尼黑","皇家马德里","国际米兰","巴黎圣日耳曼","多特蒙德","巴塞罗那"],
    },
    "曼城(英格兰)": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": True, "fa_cup": True,
        "opponents_epl": ["阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿","富勒姆","西汉姆联"],
        "ucl_opponents": ["巴塞罗那","拜仁慕尼黑","皇家马德里","国际米兰","巴黎圣日耳曼"],
    },
    "利物浦(英格兰)": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False,  # 本赛季可能欧联/无欧战
        "europa": True,
        "fa_cup": True,
        "opponents_epl": ["曼城","阿森纳","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿","富勒姆","西汉姆联"],
    },
    "曼联": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "fa_cup": True,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿","富勒姆","西汉姆联"],
    },
    "切尔西(英格兰)": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": True, "fa_cup": True,
        "opponents_epl": ["曼城","阿森纳","利物浦","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿","富勒姆","西汉姆联"],
        "ucl_opponents": ["巴黎圣日耳曼","多特蒙德","国际米兰","皇家马德里"],
    },
    "托特纳姆热刺": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","纽卡斯尔联","阿斯顿维拉","布赖顿"],
    },
    "热刺(英格兰)": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","纽卡斯尔联","阿斯顿维拉","布赖顿"],
    },
    "纽卡斯尔联": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": True, "fa_cup": False,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","阿斯顿维拉","布赖顿","富勒姆"],
        "ucl_opponents": ["国际米兰","多特蒙德","皇家马德里","巴黎圣日耳曼"],
    },
    "阿斯顿维拉(英格兰)": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": True, "fa_cup": True,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","布赖顿","富勒姆"],
        "ucl_opponents": ["巴黎圣日耳曼","多特蒙德","国际米兰","拜仁慕尼黑"],
    },
    "阿斯顿维拉": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": True, "fa_cup": True,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","布赖顿","富勒姆"],
        "ucl_opponents": ["巴黎圣日耳曼","多特蒙德","国际米兰","拜仁慕尼黑"],
    },
    "布莱顿(英格兰)": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","富勒姆","西汉姆联"],
    },
    "布莱顿": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","富勒姆","西汉姆联"],
    },
    "富勒姆(英格兰)": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿","西汉姆联"],
    },
    "西汉姆联": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿","富勒姆"],
    },
    "布伦特福德": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿","富勒姆"],
    },
    "伯恩茅斯": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿","富勒姆"],
    },
    "水晶宫(英格兰)": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿","富勒姆"],
    },
    "水晶宫": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿","富勒姆"],
    },
    "埃弗顿(英格兰)": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿","富勒姆"],
    },
    "伯恩利(英格兰)": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿"],
    },
    "诺丁汉森林": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿"],
    },
    "狼队(英格兰)": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿"],
    },
    "桑德兰(英格兰)": {
        "league": "英超", "tag": "league-tag",
        "code": "EPL", "schedule": EPL_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_epl": ["曼城","阿森纳","利物浦","切尔西","曼联","托特纳姆","纽卡斯尔联","阿斯顿维拉","布赖顿"],
    },

    # ===== 西甲 (La Liga) =====
    "皇家马德里": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": True, "cup_final": COPA_DEL_REY_FINAL, "cup_name": "国王杯",
        "opponents_lal": ["巴塞罗那","马德里竞技","塞维利亚","皇家社会","比利亚雷亚尔","皇家贝蒂斯","毕尔巴鄂竞技","瓦伦西亚","塞尔塔","奥萨苏纳"],
        "ucl_opponents": ["利物浦","曼城","拜仁慕尼黑","巴黎圣日耳曼","国际米兰"],
    },
    "巴塞罗那(西班牙)": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": True, "cup_final": None,
        "opponents_lal": ["皇家马德里","马德里竞技","塞维利亚","皇家社会","比利亚雷亚尔","皇家贝蒂斯","毕尔巴鄂竞技","瓦伦西亚","塞尔塔","奥萨苏纳"],
        "ucl_opponents": ["曼城","利物浦","国际米兰","拜仁慕尼黑","多特蒙德"],
    },
    "马德里竞技(西班牙)": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": True, "cup_final": None,
        "opponents_lal": ["皇家马德里","巴塞罗那","塞维利亚","皇家社会","比利亚雷亚尔","皇家贝蒂斯","毕尔巴鄂竞技","瓦伦西亚","塞尔塔","奥萨苏纳"],
        "ucl_opponents": ["巴黎圣日耳曼","多特蒙德","拜仁慕尼黑","国际米兰","利物浦"],
    },
    "马德里竞技": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": True, "cup_final": None,
        "opponents_lal": ["皇家马德里","巴塞罗那","塞维利亚","皇家社会","比利亚雷亚尔","皇家贝蒂斯","毕尔巴鄂竞技","瓦伦西亚","塞尔塔","奥萨苏纳"],
        "ucl_opponents": ["巴黎圣日耳曼","多特蒙德","拜仁慕尼黑","国际米兰","利物浦"],
    },
    "毕尔巴鄂竞技(西班牙)": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "cup_final": COPA_DEL_REY_FINAL, "cup_name": "国王杯",
        "opponents_lal": ["皇家马德里","巴塞罗那","马德里竞技","塞维利亚","皇家社会","比利亚雷亚尔","皇家贝蒂斯","瓦伦西亚","塞尔塔","奥萨苏纳"],
    },
    "毕尔巴鄂竞技": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "cup_final": COPA_DEL_REY_FINAL, "cup_name": "国王杯",
        "opponents_lal": ["皇家马德里","巴塞罗那","马德里竞技","塞维利亚","皇家社会","比利亚雷亚尔","皇家贝蒂斯","瓦伦西亚","塞尔塔","奥萨苏纳"],
    },
    "皇家贝蒂斯(西班牙)": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "opponents_lal": ["皇家马德里","巴塞罗那","马德里竞技","塞维利亚","皇家社会","比利亚雷亚尔","毕尔巴鄂竞技","瓦伦西亚","塞尔塔","奥萨苏纳"],
    },
    "皇家贝蒂斯": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "opponents_lal": ["皇家马德里","巴塞罗那","马德里竞技","塞维利亚","皇家社会","比利亚雷亚尔","毕尔巴鄂竞技","瓦伦西亚","塞尔塔","奥萨苏纳"],
    },
    "皇家社会(西班牙)": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "opponents_lal": ["皇家马德里","巴塞罗那","马德里竞技","塞维利亚","比利亚雷亚尔","皇家贝蒂斯","毕尔巴鄂竞技","瓦伦西亚","塞尔塔","奥萨苏纳"],
    },
    "塞维利亚(西班牙)": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_lal": ["皇家马德里","巴塞罗那","马德里竞技","皇家社会","比利亚雷亚尔","皇家贝蒂斯","毕尔巴鄂竞技","瓦伦西亚","塞尔塔","奥萨苏纳"],
    },
    "塞维利亚": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_lal": ["皇家马德里","巴塞罗那","马德里竞技","皇家社会","比利亚雷亚尔","皇家贝蒂斯","毕尔巴鄂竞技","瓦伦西亚","塞尔塔","奥萨苏纳"],
    },
    "瓦伦西亚": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_lal": ["皇家马德里","巴塞罗那","马德里竞技","塞维利亚","皇家社会","比利亚雷亚尔","皇家贝蒂斯","毕尔巴鄂竞技","塞尔塔","奥萨苏纳"],
    },
    "比利亚雷亚尔(西班牙)": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "opponents_lal": ["皇家马德里","巴塞罗那","马德里竞技","塞维利亚","皇家社会","皇家贝蒂斯","毕尔巴鄂竞技","瓦伦西亚","塞尔塔","奥萨苏纳"],
    },
    "比利亚雷亚尔": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "opponents_lal": ["皇家马德里","巴塞罗那","马德里竞技","塞维利亚","皇家社会","皇家贝蒂斯","毕尔巴鄂竞技","瓦伦西亚","塞尔塔","奥萨苏纳"],
    },
    "塞尔塔(西班牙)": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_lal": ["皇家马德里","巴塞罗那","马德里竞技","塞维利亚","皇家社会","比利亚雷亚尔","皇家贝蒂斯","毕尔巴鄂竞技","瓦伦西亚","奥萨苏纳"],
    },
    "塞尔塔": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_lal": ["皇家马德里","巴塞罗那","马德里竞技","塞维利亚","皇家社会","比利亚雷亚尔","皇家贝蒂斯","毕尔巴鄂竞技","瓦伦西亚","奥萨苏纳"],
    },
    "奥萨苏纳(西班牙)": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_lal": ["皇家马德里","巴塞罗那","马德里竞技","塞维利亚","皇家社会","比利亚雷亚尔","皇家贝蒂斯","毕尔巴鄂竞技","瓦伦西亚","塞尔塔"],
    },
    "奥萨苏纳": {
        "league": "西甲", "tag": "league-tag",
        "code": "LAL", "schedule": LALIGA_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_lal": ["皇家马德里","巴塞罗那","马德里竞技","塞维利亚","皇家社会","比利亚雷亚尔","皇家贝蒂斯","毕尔巴鄂竞技","瓦伦西亚","塞尔塔"],
    },

    # ===== 德甲 (Bundesliga) =====
    "拜仁慕尼黑(德国)": {
        "league": "德甲", "tag": "league-tag",
        "code": "BL1", "schedule": BUNDESLIGA_FINAL_ROUNDS,
        "ucl": True, "cup_final": DFB_POKAL_FINAL, "cup_name": "德国杯",
        "opponents_bl1": ["多特蒙德","莱比锡红牛","勒沃库森","法兰克福","斯图加特","门兴格拉德巴赫","沃尔夫斯堡","云达不莱梅","霍芬海姆","美因茨"],
        "ucl_opponents": ["阿森纳","巴塞罗那","皇家马德里","曼城","巴黎圣日耳曼"],
    },
    "多特蒙德(德国)": {
        "league": "德甲", "tag": "league-tag",
        "code": "BL1", "schedule": BUNDESLIGA_FINAL_ROUNDS,
        "ucl": True, "cup_final": None,
        "opponents_bl1": ["拜仁慕尼黑","莱比锡红牛","勒沃库森","法兰克福","斯图加特","门兴格拉德巴赫","沃尔夫斯堡","云达不莱梅","霍芬海姆","美因茨"],
        "ucl_opponents": ["国际米兰","纽卡斯尔联","皇马","巴萨","巴黎"],
    },
    "勒沃库森": {
        "league": "德甲", "tag": "league-tag",
        "code": "BL1", "schedule": BUNDESLIGA_FINAL_ROUNDS,
        "ucl": True, "cup_final": None,
        "opponents_bl1": ["拜仁慕尼黑","多特蒙德","莱比锡红牛","法兰克福","斯图加特","门兴格拉德巴赫","沃尔夫斯堡","云达不莱梅","霍芬海姆","美因茨"],
        "ucl_opponents": ["曼城","利物浦","皇马","国米","大巴黎"],
    },
    "莱比锡红牛": {
        "league": "德甲", "tag": "league-tag",
        "code": "BL1", "schedule": BUNDESLIGA_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "opponents_bl1": ["拜仁慕尼黑","多特蒙德","勒沃库森","法兰克福","斯图加特","门兴格拉德巴赫","沃尔夫斯堡","云达不莱梅","霍芬海姆","美因茨"],
    },
    "斯图加特(德国)": {
        "league": "德甲", "tag": "league-tag",
        "code": "BL1", "schedule": BUNDESLIGA_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "opponents_bl1": ["拜仁慕尼黑","多特蒙德","勒沃库森","莱比锡红牛","法兰克福","门兴格拉德巴赫","沃尔夫斯堡","云达不莱梅","霍芬海姆","美因茨"],
    },
    "斯图加特": {
        "league": "德甲", "tag": "league-tag",
        "code": "BL1", "schedule": BUNDESLIGA_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "opponents_bl1": ["拜仁慕尼黑","多特蒙德","勒沃库森","莱比锡红牛","法兰克福","门兴格拉德巴赫","沃尔夫斯堡","云达不莱梅","霍芬海姆","美因茨"],
    },
    "法兰克福(德国)": {
        "league": "德甲", "tag": "league-tag",
        "code": "BL1", "schedule": BUNDESLIGA_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "opponents_bl1": ["拜仁慕尼黑","多特蒙德","勒沃库森","莱比锡红牛","斯图加特","门兴格拉德巴赫","沃尔夫斯堡","云达不莱梅","霍芬海姆","美因茨"],
    },
    "法兰克福": {
        "league": "德甲", "tag": "league-tag",
        "code": "BL1", "schedule": BUNDESLIGA_FINAL_ROUNDS,
        "ucl": False, "europa": True,
        "opponents_bl1": ["拜仁慕尼黑","多特蒙德","勒沃库森","莱比锡红牛","斯图加特","门兴格拉德巴赫","沃尔夫斯堡","云达不莱梅","霍芬海姆","美因茨"],
    },
    "霍芬海姆(德国)": {
        "league": "德甲", "tag": "league-tag",
        "code": "BL1", "schedule": BUNDESLIGA_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_bl1": ["拜仁慕尼黑","多特蒙德","勒沃库森","莱比锡红牛","斯图加特","法兰克福","门兴格拉德巴赫","沃尔夫斯堡","云达不莱梅","美因茨"],
    },
    "霍芬海姆": {
        "league": "德甲", "tag": "league-tag",
        "code": "BL1", "schedule": BUNDESLIGA_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_bl1": ["拜仁慕尼黑","多特蒙德","勒沃库森","莱比锡红牛","斯图加特","法兰克福","门兴格拉德巴赫","沃尔夫斯堡","云达不莱梅","美因茨"],
    },
    "美因茨(德国)": {
        "league": "德甲", "tag": "league-tag",
        "code": "BL1", "schedule": BUNDESLIGA_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_bl1": ["拜仁慕尼黑","多特蒙德","勒沃库森","莱比锡红牛","斯图加特","法兰克福","门兴格拉德巴赫","沃尔夫斯堡","云达不莱梅","霍芬海姆"],
    },
    "美因茨": {
        "league": "德甲", "tag": "league-tag",
        "code": "BL1", "schedule": BUNDESLIGA_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_bl1": ["拜仁慕尼黑","多特蒙德","勒沃库森","莱比锡红牛","斯图加特","法兰克福","门兴格拉德巴赫","沃尔夫斯堡","云达不莱梅","霍芬海姆"],
    },

    # ===== 意甲 (Serie A) =====
    "国际米兰(意大利)": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": True, "cup_final": COPPA_ITALIA_FINAL, "cup_name": "意大利杯",
        "opponents_sea": ["尤文图斯","AC米兰","那不勒斯","罗马","拉齐奥","佛罗伦萨","亚特兰大","博洛尼亚","科莫","维罗纳"],
        "ucl_opponents": ["多特蒙德","纽卡斯尔联","拜仁","巴萨","曼城"],
    },
    "尤文图斯(意大利)": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": False, "europa": True, "cup_final": None,
        "opponents_sea": ["国际米兰","AC米兰","那不勒斯","罗马","拉齐奥","佛罗伦萨","亚特兰大","博洛尼亚","科莫","维罗纳"],
    },
    "尤文图斯": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": False, "europa": True, "cup_final": None,
        "opponents_sea": ["国际米兰","AC米兰","那不勒斯","罗马","拉齐奥","佛罗伦萨","亚特兰大","博洛尼亚","科莫","维罗纳"],
    },
    "AC米兰(意大利)": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": True, "cup_final": None,
        "opponents_sea": ["国际米兰","尤文图斯","那不勒斯","罗马","拉齐奥","佛罗伦萨","亚特兰大","博洛尼亚","科莫","维罗纳"],
        "ucl_opponents": ["巴黎圣日耳曼","皇马","拜仁","巴萨","利物浦"],
    },
    "AC米兰": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": True, "cup_final": None,
        "opponents_sea": ["国际米兰","尤文图斯","那不勒斯","罗马","拉齐奥","佛罗伦萨","亚特兰大","博洛尼亚","科莫","维罗纳"],
        "ucl_opponents": ["巴黎圣日耳曼","皇马","拜仁","巴萨","利物浦"],
    },
    "那不勒斯(意大利)": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": True, "cup_final": None,
        "opponents_sea": ["国际米兰","尤文图斯","AC米兰","罗马","拉齐奥","佛罗伦萨","亚特兰大","博洛尼亚","科莫","维罗纳"],
        "ucl_opponents": ["切尔西","利物浦","多特","莱比锡","勒沃库森"],
    },
    "那不勒斯": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": True, "cup_final": None,
        "opponents_sea": ["国际米兰","尤文图斯","AC米兰","罗马","拉齐奥","佛罗伦萨","亚特兰大","博洛尼亚","科莫","维罗纳"],
        "ucl_opponents": ["切尔西","利物浦","多特","莱比锡","勒沃库森"],
    },
    "罗马(意大利)": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": False, "europa": True, "cup_final": None,
        "opponents_sea": ["国际米兰","尤文图斯","AC米兰","那不勒斯","拉齐奥","佛罗伦萨","亚特兰大","博洛尼亚","科莫","维罗纳"],
    },
    "罗马": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": False, "europa": True, "cup_final": None,
        "opponents_sea": ["国际米兰","尤文图斯","AC米兰","那不勒斯","拉齐奥","佛罗伦萨","亚特兰大","博洛尼亚","科莫","维罗纳"],
    },
    "亚特兰大(意大利)": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": True, "cup_final": None,
        "opponents_sea": ["国际米兰","尤文图斯","AC米兰","那不勒斯","罗马","拉齐奥","佛罗伦萨","博洛尼亚","科莫","维罗纳"],
        "ucl_opponents": ["皇马","曼城","拜仁","巴萨","多特"],
    },
    "亚特兰大": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": True, "cup_final": None,
        "opponents_sea": ["国际米兰","尤文图斯","AC米兰","那不勒斯","罗马","拉齐奥","佛罗伦萨","博洛尼亚","科莫","维罗纳"],
        "ucl_opponents": ["皇马","曼城","拜仁","巴萨","多特"],
    },
    "佛罗伦萨(意大利)": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": False, "europa": True, "cup_final": None,
        "opponents_sea": ["国际米兰","尤文图斯","AC米兰","那不勒斯","罗马","拉齐奥","亚特兰大","博洛尼亚","科莫","维罗纳"],
    },
    "佛罗伦萨": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": False, "europa": True, "cup_final": None,
        "opponents_sea": ["国际米兰","尤文图斯","AC米兰","那不勒斯","罗马","拉齐奥","亚特兰大","博洛尼亚","科莫","维罗纳"],
    },
    "科莫(意大利)": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": False, "europa": False, "cup_final": None,
        "opponents_sea": ["国际米兰","尤文图斯","AC米兰","那不勒斯","罗马","拉齐奥","亚特兰大","佛罗伦萨","博洛尼亚","维罗纳"],
    },
    "亚历山德里亚(意大利)": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": False, "europa": False, "cup_final": None,
        "opponents_sea": ["国际米兰","尤文图斯","AC米兰","那不勒斯","罗马","拉齐奥","亚特兰大","佛罗伦萨","博洛尼亚","科莫"],
    },
    "维罗纳(意大利)": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": False, "europa": False, "cup_final": None,
        "opponents_sea": ["国际米兰","尤文图斯","AC米兰","那不勒斯","罗马","拉齐奥","亚特兰大","佛罗伦萨","博洛尼亚","科莫"],
    },
    "维罗纳": {
        "league": "意甲", "tag": "league-tag",
        "code": "SEA", "schedule": SERIEA_FINAL_ROUNDS,
        "ucl": False, "europa": False, "cup_final": None,
        "opponents_sea": ["国际米兰","尤文图斯","AC米兰","那不勒斯","罗马","拉齐奥","亚特兰大","佛罗伦萨","博洛尼亚","科莫"],
    },

    # ===== 法甲 (Ligue 1) =====
    "巴黎圣日耳曼": {
        "league": "法甲", "tag": "league-tag",
        "code": "FR1", "schedule": LIGUE1_FINAL_ROUNDS,
        "ucl": True, "cup_final": COUPE_DE_FRANCE_F, "cup_name": "法国杯",
        "opponents_fr1": ["马赛","里昂","摩纳哥","尼斯","朗斯","兰斯","雷恩","图卢兹","斯特拉斯堡","雷恩"],
        "ucl_opponents": ["AC米兰","那不勒斯","多特蒙德","利物浦","曼城"],
    },
    "马赛(法国)": {
        "league": "法甲", "tag": "league-tag",
        "code": "FR1", "schedule": LIGUE1_FINAL_ROUNDS,
        "ucl": False, "europa": True, "cup_final": COUPE_DE_FRANCE_F, "cup_name": "法国杯",
        "opponents_fr1": ["巴黎圣日耳曼","里昂","摩纳哥","尼斯","朗斯","兰斯","雷恩","图卢兹","斯特拉斯堡"],
    },
    "马赛": {
        "league": "法甲", "tag": "league-tag",
        "code": "FR1", "schedule": LIGUE1_FINAL_ROUNDS,
        "ucl": False, "europa": True, "cup_final": COUPE_DE_FRANCE_F, "cup_name": "法国杯",
        "opponents_fr1": ["巴黎圣日耳曼","里昂","摩纳哥","尼斯","朗斯","兰斯","雷恩","图卢兹","斯特拉斯堡"],
    },
    "里昂(法国)": {
        "league": "法甲", "tag": "league-tag",
        "code": "FR1", "schedule": LIGUE1_FINAL_ROUNDS,
        "ucl": False, "europa": True, "cup_final": None,
        "opponents_fr1": ["巴黎圣日耳曼","马赛","摩纳哥","尼斯","朗斯","兰斯","雷恩","图卢兹","斯特拉斯堡"],
    },
    "里昂": {
        "league": "法甲", "tag": "league-tag",
        "code": "FR1", "schedule": LIGUE1_FINAL_ROUNDS,
        "ucl": False, "europa": True, "cup_final": None,
        "opponents_fr1": ["巴黎圣日耳曼","马赛","摩纳哥","尼斯","朗斯","兰斯","雷恩","图卢兹","斯特拉斯堡"],
    },
    "摩纳哥(法国)": {
        "league": "法甲", "tag": "league-tag",
        "code": "FR1", "schedule": LIGUE1_FINAL_ROUNDS,
        "ucl": False, "europa": True, "cup_final": None,
        "opponents_fr1": ["巴黎圣日耳曼","马赛","里昂","尼斯","朗斯","兰斯","雷恩","图卢兹","斯特拉斯堡"],
    },
    "朗斯(法国)": {
        "league": "法甲", "tag": "league-tag",
        "code": "FR1", "schedule": LIGUE1_FINAL_ROUNDS,
        "ucl": False, "europa": False, "cup_final": None,
        "opponents_fr1": ["巴黎圣日耳曼","马赛","里昂","摩纳哥","尼斯","兰斯","雷恩","图卢兹","斯特拉斯堡"],
    },
    "朗斯": {
        "league": "法甲", "tag": "league-tag",
        "code": "FR1", "schedule": LIGUE1_FINAL_ROUNDS,
        "ucl": False, "europa": False, "cup_final": None,
        "opponents_fr1": ["巴黎圣日耳曼","马赛","里昂","摩纳哥","尼斯","兰斯","雷恩","图卢兹","斯特拉斯堡"],
    },
    "雷恩(法国)": {
        "league": "法甲", "tag": "league-tag",
        "code": "FR1", "schedule": LIGUE1_FINAL_ROUNDS,
        "ucl": False, "europa": False, "cup_final": None,
        "opponents_fr1": ["巴黎圣日耳曼","马赛","里昂","摩纳哥","尼斯","朗斯","兰斯","图卢兹","斯特拉斯堡"],
    },
    "斯特拉斯堡(法国)": {
        "league": "法甲", "tag": "league-tag",
        "code": "FR1", "schedule": LIGUE1_FINAL_ROUNDS,
        "ucl": False, "europa": False, "cup_final": None,
        "opponents_fr1": ["巴黎圣日耳曼","马赛","里昂","摩纳哥","尼斯","朗斯","兰斯","雷恩","图卢兹"],
    },
    "斯特拉斯堡": {
        "league": "法甲", "tag": "league-tag",
        "code": "FR1", "schedule": LIGUE1_FINAL_ROUNDS,
        "ucl": False, "europa": False, "cup_final": None,
        "opponents_fr1": ["巴黎圣日耳曼","马赛","里昂","摩纳哥","尼斯","朗斯","兰斯","雷恩","图卢兹"],
    },

    # ===== 葡超 =====
    "波尔图(葡萄牙)": {
        "league": "葡超", "tag": "club-tag",
        "code": "POR", "schedule": PORTUGAL_MATCHES,
        "ucl": False, "europa": True,
        "opponents_por": ["本菲卡","葡萄牙体育","布拉加","吉马良斯","阿维斯镇","埃斯托里尔","卡萨皮亚","法马利康"],
    },
    "葡萄牙体育(葡萄牙)": {
        "league": "葡超", "tag": "club-tag",
        "code": "POR", "schedule": PORTUGAL_MATCHES,
        "ucl": True, "europa": False,
        "opponents_por": ["波尔图","本菲卡","布拉加","吉马良斯","阿维斯镇","埃斯托里尔","卡萨皮亚","法马利康"],
        "ucl_opponents": ["阿森纳","切尔西","多特蒙德","国米","拜仁"],
    },
    "本菲卡(葡萄牙)": {
        "league": "葡超", "tag": "club-tag",
        "code": "POR", "schedule": PORTUGAL_MATCHES,
        "ucl": False, "europa": True,
        "opponents_por": ["波尔图","葡萄牙体育","布拉加","吉马良斯","阿维斯镇","埃斯托里尔","卡萨皮亚","法马利康"],
    },

    # ===== 荷甲 =====
    "阿贾克斯(荷兰)": {
        "league": "荷甲", "tag": "club-tag",
        "code": "NED", "schedule": NETHERLANDS_MATCHES,
        "ucl": False, "europa": True,
        "opponents_ned": ["费耶诺德","埃因霍温","阿尔克马尔","特温特","格罗宁根","乌德勒支","维迪斯","前进之鹰"],
    },
    "费耶诺德(荷兰)": {
        "league": "荷甲", "tag": "club-tag",
        "code": "NED", "schedule": NETHERLANDS_MATCHES,
        "ucl": True, "europa": False,
        "opponents_ned": ["阿贾克斯","埃因霍温","阿尔克马尔","特温特","格罗宁根","乌德勒支","维迪斯","前进之鹰"],
        "ucl_opponents": ["皇马","巴萨","曼城","利物浦","巴黎"],
    },
    "埃因霍温(荷兰)": {
        "league": "荷甲", "tag": "club-tag",
        "code": "NED", "schedule": NETHERLANDS_MATCHES,
        "ucl": False, "europa": True,
        "opponents_ned": ["阿贾克斯","费耶诺德","阿尔克马尔","特温特","格罗宁根","乌德勒支","维迪斯","前进之鹰"],
    },

    # ===== 比利时甲级 =====
    "布鲁日(比利时)": {
        "league": "比甲", "tag": "club-tag",
        "code": "BEL", "schedule": BELGIUM_MATCHES,
        "ucl": False, "europa": True,
        "opponents_bel": ["安德莱赫特","根特","标准列日","亨克","布鲁日","安特卫普","梅赫伦","奥斯坦德"],
    },

    # ===== 苏超 =====
    "流浪者(苏格兰)": {
        "league": "苏超", "tag": "club-tag",
        "code": "SCO", "schedule": SCOTLAND_MATCHES,
        "ucl": False, "europa": True,
        "opponents_sco": ["凯尔特人","阿伯丁","哈茨","希伯尼安","马瑟韦尔","圣约翰斯顿","罗斯郡","邓迪联"],
    },

    # ===== 土超 =====
    "费内巴切": {
        "league": "土超", "tag": "ucl-tag",
        "code": "TUR", "schedule": SAUDI_MATCHES,  # 复用日期结构
        "ucl": False, "europa": True,
        "opponents_tur": ["加拉塔萨雷","贝西克塔斯","特拉布宗体育","巴萨克谢希尔","开塞利体育","锡瓦斯体育"],
    },

    # ===== 沙特职业联赛 =====
    "吉达联合(沙特)": {
        "league": "沙特联", "tag": "club-tag",
        "code": "SAD", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_sad": ["利雅得新月","利雅得胜利","吉达国民","吉达阿赫利","达曼协作","布赖代合作","费哈","哈萨征服"],
    },
    "吉达联合": {
        "league": "沙特联", "tag": "club-tag",
        "code": "SAD", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_sad": ["利雅得新月","利雅得胜利","吉达国民","吉达阿赫利","达曼协作","布赖代合作","费哈","哈萨征服"],
    },
    "利雅得新月(沙特)": {
        "league": "沙特联", "tag": "club-tag",
        "code": "SAD", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_sad": ["吉达联合","利雅得胜利","吉达国民","吉达阿赫利","达曼协作","布赖代合作","费哈","哈萨征服"],
    },
    "利雅得胜利": {
        "league": "沙特联", "tag": "club-tag",
        "code": "SAD", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_sad": ["吉达联合","吉达国民","利雅得新月","吉达阿赫利","达曼协作","布赖代合作","费哈","哈萨征服"],
    },
    "吉达国民(沙特)": {
        "league": "沙特联", "tag": "club-tag",
        "code": "SAD", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_sad": ["吉达联合","利雅得新月","利雅得胜利","吉达阿赫利","达曼协作","布赖代合作","费哈","哈萨征服"],
    },

    # ===== 巴西甲级联赛 =====
    "弗拉门戈": {
        "league": "巴甲", "tag": "club-tag",
        "code": "BRA", "schedule": BRAZIL_MATCHES,
        "ucl": False, "europa": False,
        "opponents_bra": ["帕尔梅拉斯","格雷米奥","科林蒂安","圣保罗","米内罗竞技","巴西国际","博塔弗戈","弗鲁米嫩塞"],
    },
    "格雷米奥": {
        "league": "巴甲", "tag": "club-tag",
        "code": "BRA", "schedule": BRAZIL_MATCHES,
        "ucl": False, "europa": False,
        "opponents_bra": ["弗拉门戈","帕尔梅拉斯","科林蒂安","圣保罗","米内罗竞技","巴西国际","博塔弗戈","弗鲁米嫩塞"],
    },
    "帕尔梅拉斯": {
        "league": "巴甲", "tag": "club-tag",
        "code": "BRA", "schedule": BRAZIL_MATCHES,
        "ucl": False, "europa": False,
        "opponents_bra": ["弗拉门戈","格雷米奥","科林蒂安","圣保罗","米内罗竞技","巴西国际","博塔弗戈","弗鲁米嫩塞"],
    },
    "博塔弗戈": {
        "league": "巴甲", "tag": "club-tag",
        "code": "BRA", "schedule": BRAZIL_MATCHES,
        "ucl": False, "europa": False,
        "opponents_bra": ["弗拉门戈","格雷米奥","帕尔梅拉斯","科林蒂安","圣保罗","米内罗竞技","巴西国际","弗鲁米嫩塞"],
    },
    "桑托斯(巴西)": {
        "league": "巴甲", "tag": "club-tag",
        "code": "BRA", "schedule": BRAZIL_MATCHES,
        "ucl": False, "europa": False,
        "opponents_bra": ["弗拉门戈","格雷米奥","帕尔梅拉斯","科林蒂安","圣保罗","米内罗竞技","巴西国际","博塔弗戈"],
    },

    # ===== 墨西哥超级联赛 =====
    "墨西哥美洲": {
        "league": "墨超", "tag": "club-tag",
        "code": "MEX", "schedule": MEXICO_MATCHES,
        "ucl": False, "europa": False,
        "opponents_mex": ["蒙特雷","瓜达拉哈拉","蓝十字","墨西哥芝华士","老虎队","美洲狮","普埃布拉","莱昂","内卡萨"],
    },
    "墨西哥芝华士": {
        "league": "墨超", "tag": "club-tag",
        "code": "MEX", "schedule": MEXICO_MATCHES,
        "ucl": False, "europa": False,
        "opponents_mex": ["墨西哥美洲","蒙特雷","瓜达拉哈拉","蓝十字","老虎队","美洲狮","普埃布拉","莱昂","内卡萨"],
    },
    "蒙特雷": {
        "league": "墨超", "tag": "club-tag",
        "code": "MEX", "schedule": MEXICO_MATCHES,
        "ucl": False, "europa": False,
        "opponents_mex": ["墨西哥美洲","瓜达拉哈拉","蓝十字","墨西哥芝华士","老虎队","美洲狮","普埃布拉","莱昂","内卡萨"],
    },
    "蓝十字": {
        "league": "墨超", "tag": "club-tag",
        "code": "MEX", "schedule": MEXICO_MATCHES,
        "ucl": False, "europa": False,
        "opponents_mex": ["墨西哥美洲","蒙特雷","瓜达拉哈拉","墨西哥芝华士","老虎队","美洲狮","普埃布拉","莱昂","内卡萨"],
    },
    "美洲狮": {
        "league": "墨超", "tag": "club-tag",
        "code": "MEX", "schedule": MEXICO_MATCHES,
        "ucl": False, "europa": False,
        "opponents_mex": ["墨西哥美洲","蒙特雷","瓜达拉哈拉","蓝十字","墨西哥芝华士","老虎队","普埃布拉","莱昂","内卡萨"],
    },
    "莱昂": {
        "league": "墨超", "tag": "club-tag",
        "code": "MEX", "schedule": MEXICO_MATCHES,
        "ucl": False, "europa": False,
        "opponents_mex": ["墨西哥美洲","蒙特雷","瓜达拉哈拉","蓝十字","墨西哥芝华士","老虎队","美洲狮","普埃布拉","内卡萨"],
    },
    "普埃布拉": {
        "league": "墨超", "tag": "club-tag",
        "code": "MEX", "schedule": MEXICO_MATCHES,
        "ucl": False, "europa": False,
        "opponents_mex": ["墨西哥美洲","蒙特雷","瓜达拉哈拉","蓝十字","墨西哥芝华士","老虎队","美洲狮","莱昂","内卡萨"],
    },
    "瓜达拉哈拉": {
        "league": "墨超", "tag": "club-tag",
        "code": "MEX", "schedule": MEXICO_MATCHES,
        "ucl": False, "europa": False,
        "opponents_mex": ["墨西哥美洲","蒙特雷","蓝十字","墨西哥芝华士","老虎队","美洲狮","普埃布拉","莱昂","内卡萨"],
    },
    "内卡萨": {
        "league": "墨超", "tag": "club-tag",
        "code": "MEX", "schedule": MEXICO_MATCHES,
        "ucl": False, "europa": False,
        "opponents_mex": ["墨西哥美洲","蒙特雷","瓜达拉哈拉","蓝十字","墨西哥芝华士","老虎队","美洲狮","莱昂","普埃布拉"],
    },
    "老虎队": {
        "league": "墨超", "tag": "club-tag",
        "code": "MEX", "schedule": MEXICO_MATCHES,
        "ucl": False, "europa": False,
        "opponents_mex": ["墨西哥美洲","蒙特雷","瓜达拉哈拉","蓝十字","墨西哥芝华士","美洲狮","普埃布拉","莱昂","内卡萨"],
    },

    # ===== 阿根廷甲级联赛 =====
    "河床(阿根廷)": {
        "league": "阿甲", "tag": "club-tag",
        "code": "ARG", "schedule": ARGENTINA_MATCHES,
        "ucl": False, "europa": False,
        "opponents_arg": ["博卡青年","独立队","竞技俱乐部","圣洛伦索","萨斯菲尔德","图库曼竞技","罗萨里奥中央","拉努斯","普拉腾斯"],
    },
    "博卡青年(阿根廷)": {
        "league": "阿甲", "tag": "club-tag",
        "code": "ARG", "schedule": ARGENTINA_MATCHES,
        "ucl": False, "europa": False,
        "opponents_arg": ["河床","独立队","竞技俱乐部","圣洛伦索","萨斯菲尔德","图库曼竞技","罗萨里奥中央","拉努斯","普拉腾斯"],
    },

    # ===== 俄罗斯超级联赛 =====
    "泽尼特": {
        "league": "俄超", "tag": "club-tag",
        "code": "RUS", "schedule": ARGENTINA_MATCHES,  # 复用日期
        "ucl": False, "europa": False,
        "opponents_rus": ["莫斯科中央陆军","莫斯科斯巴达克","克拉斯诺达尔","格罗兹尼","索契","罗斯托夫","奥伦堡","乌拉尔"],
    },

    # ===== 美职联 MLS =====
    "迈阿密国际(美国)": {
        "league": "美职联", "tag": "club-tag",
        "code": "MLS", "schedule": BRAZIL_MATCHES,  # 复用日期
        "ucl": False, "europa": False,
        "opponents_mls": ["纽约城FC","洛杉矶FC","哥伦布机员","亚特兰大联","新英格兰革命","多伦多FC","华盛顿联","辛辛那提FC"],
    },

    # ===== 乌兹别克斯坦超级联赛 =====
    "本尤德科(乌兹别克斯坦)": {
        "league": "乌超", "tag": "club-tag",
        "code": "UZB", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_uzb": ["纳萨夫","棉农","洛科莫蒂夫塔什干","帕赫塔科尔","奥尔马利克","本菲卡塔什干","科帕尔","纳夫巴霍尔"],
    },
    "纳萨夫(乌兹别克斯坦)": {
        "league": "乌超", "tag": "club-tag",
        "code": "UZB", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_uzb": ["本尤德科","棉农","洛科莫蒂夫塔什干","帕赫塔科尔","奥尔马利克","本菲卡塔什干","科帕尔","纳夫巴霍尔"],
    },
    "棉农(乌兹别克斯坦)": {
        "league": "乌超", "tag": "club-tag",
        "code": "UZB", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_uzb": ["本尤德科","纳萨夫","洛科莫蒂夫塔什干","帕赫塔科尔","奥尔马利克","本菲卡塔什干","科帕尔","纳夫巴霍尔"],
    },

    # ===== 约旦职业联赛 =====
    "阿赫利安曼(约旦)": {
        "league": "约旦联", "tag": "club-tag",
        "code": "JOR", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_jor": ["阿尔费萨里","阿尔达汉","维赫达特","拉马萨尔","巴格达达·阿尔穆弗拉克","希尔顿","哈赛马","贾泽拉"],
    },
    "阿尔费萨里(约旦)": {
        "league": "约旦联", "tag": "club-tag",
        "code": "JOR", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_jor": ["阿赫利安曼","阿尔达汉","维赫达特","拉马萨尔","巴格达达·阿尔穆弗拉克","希尔顿","哈赛马","贾泽拉"],
    },
    "阿尔达汉(约旦)": {
        "league": "约旦联", "tag": "club-tag",
        "code": "JOR", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_jor": ["阿赫利安曼","阿尔费萨里","维赫达特","拉马萨尔","巴格达达·阿尔穆弗拉克","希尔顿","哈赛马","贾泽拉"],
    },

    # ===== 土耳其超级联赛（补充） =====
    "布尔古尔迪内斯(土耳其)": {
        "league": "土超", "tag": "club-tag",
        "code": "TUR", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_tur": ["加拉塔萨雷","费内巴切","贝西克塔斯","特拉布宗体育","巴萨克谢希尔","开塞利体育","锡瓦斯体育","比斯克塔斯"],
    },
    "阿兰亚体育(土耳其)": {
        "league": "土超", "tag": "club-tag",
        "code": "TUR", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_tur": ["加拉塔萨雷","费内巴切","贝西克塔斯","特拉布宗体育","巴萨克谢希尔","开塞利体育","锡瓦斯体育","布尔古尔迪内斯"],
    },

    # ===== 希腊超级联赛 =====
    "PAOK(希腊)": {
        "league": "希超", "tag": "club-tag",
        "code": "GRE", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": True,
        "opponents_gre": ["奥林匹亚科斯","帕纳辛纳科斯","AEK雅典","帕尼基皮斯","拉里萨","沃洛斯","潘瑟拉科斯","阿特罗米托斯"],
    },

    # ===== 伊朗职业联赛 =====
    "塞帕什科姆(伊朗)": {
        "league": "伊朗联", "tag": "club-tag",
        "code": "IRN", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_irn": ["佩斯波利斯","伊斯法罕塞帕","塔拉克托尔","埃斯蒂格拉尔","祖布·阿汉","帕丁","纳夫特麦斯杰德苏莱曼","塞帕汉"],
    },

    # ===== 南非超级运动联赛 =====
    "马摩洛火焰(南非)": {
        "league": "南非联", "tag": "club-tag",
        "code": "SAF", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_saf": ["奥兰多海盗","阿马祖鲁","卡泽尔","班加洛","超级体育","斯旺斯","科林蒂安斯","普利托利亚阿尔卡萨尔"],
    },
    "阿马祖鲁(南非)": {
        "league": "南非联", "tag": "club-tag",
        "code": "SAF", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_saf": ["马摩洛火焰","奥兰多海盗","卡泽尔","班加洛","超级体育","斯旺斯","科林蒂安斯","普利托利亚阿尔卡萨尔"],
    },
    "奥兰多海盗(南非)": {
        "league": "南非联", "tag": "club-tag",
        "code": "SAF", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": False,
        "opponents_saf": ["马摩洛火焰","阿马祖鲁","卡泽尔","班加洛","超级体育","斯旺斯","科林蒂安斯","普利托利亚阿尔卡萨尔"],
    },

    # ===== 苏格兰超级联赛（补充） =====
    "凯尔特人(苏格兰)": {
        "league": "苏超", "tag": "club-tag",
        "code": "SCO", "schedule": SCOTLAND_MATCHES,
        "ucl": True, "europa": False,
        "opponents_sco": ["流浪者","阿伯丁","哈茨","希伯尼安","马瑟韦尔","圣约翰斯顿","罗斯郡","邓迪联"],
        "ucl_opponents": ["多特蒙德","拜仁慕尼黑","皇家马德里","国际米兰","巴黎圣日耳曼"],
    },
    "圣图尔登(比利时)": {
        "league": "比甲", "tag": "club-tag",
        "code": "BEL", "schedule": BELGIUM_MATCHES,
        "ucl": False, "europa": False,
        "opponents_bel": ["安德莱赫特","根特","标准列日","亨克","布鲁日","安特卫普","梅赫伦","奥斯坦德"],
    },
    "马尔默(瑞典)": {
        "league": "瑞甲", "tag": "club-tag",
        "code": "SWE", "schedule": SAUDI_MATCHES,
        "ucl": False, "europa": True,
        "opponents_swe": ["哥德堡","诺尔雪平","赫尔辛堡","IFK哥德堡","哈马比","迪尔加尔登","厄斯泰松德","卡尔马"],
    },
    "科英布拉(葡萄牙)": {
        "league": "葡超", "tag": "club-tag",
        "code": "POR", "schedule": PORTUGAL_MATCHES,
        "ucl": False, "europa": False,
        "opponents_por": ["波尔图","本菲卡","葡萄牙体育","布拉加","吉马良斯","阿维斯镇","埃斯托里尔","卡萨皮亚"],
    },
    "特鲁瓦(法国)": {
        "league": "法甲", "tag": "club-tag",
        "code": "FR1", "schedule": LIGUE1_FINAL_ROUNDS,
        "ucl": False, "europa": False,
        "opponents_fr1": ["巴黎圣日耳曼","马赛","里昂","摩纳哥","尼斯","朗斯","兰斯","雷恩","图卢兹","斯特拉斯堡"],
    },
}

DEFAULT_CLUB = {"league": "联赛", "tag": "club-tag", "code": "DEF", "schedule": [], "ucl": False}


# ============================================================
# 第三部分：国家 → 国家队信息映射（用于热身赛）
# ============================================================
# 根据球员名字推断国籍（基于实际阵容中的球员）
PLAYER_NATIONALITY = {
    # 阿根廷
    "梅西⭐(C)": "Argentina", "阿尔瓦雷斯": "Argentina", "劳塔罗": "Argentina",
    "德保罗": "Argentina", "蒙铁尔": "Argentina", "埃米利亚诺·马丁内斯": "Argentina",
    "麦卡利斯特": "Argentina", "利桑德罗·马丁内斯": "Argentina", "奥塔门迪": "Argentina",
    "恩佐": "Argentina", "罗梅罗": "Argentina",
    # 葡萄牙
    "C罗": "Portugal", "布鲁诺·费尔南德斯": "Portugal", "贝尔纳多·席尔瓦": "Portugal",
    "鲁本·迪亚斯": "Portugal", "若昂·内维斯": "Portugal", "坎塞洛": "Portugal",
    "鲁本·内维斯": "Portugal", "莱奥": "Portugal", "拉斐尔·莱奥": "Portugal",
    "达尼洛·桑托斯": "Portugal", "布鲁诺·吉马良斯": "Portugal", "马特塔": "Portugal",
    "安东尼奥·席尔瓦": "Portugal", "迪奥戈·科斯塔": "Portugal",
    "费尔南德斯·帕尔多": "Portugal", "孔塞桑": "Portugal",
    "贡萨洛·伊纳西奥": "Portugal", "特林康": "Portugal", "鲁伊·席尔瓦": "Portugal",
    "德巴斯特": "Portugal", "奥塔门迪": "Portugal",
    # 法国
    "姆巴佩 ⭐": "France", "登贝莱": "France", "楚阿梅尼": "France",
    "萨利巴": "France", "孔德": "France", "巴尔科拉": "France",
    "奥利塞": "France", "杜埃": "France", "努诺·门德斯": "France",
    "科内": "France", "恩昆库": "France", "贡萨洛·拉莫斯": "France",
    "阿克利乌什": "France",
    # 英格兰
    "凯·哈弗茨": "Germany", "贝林厄姆": "England", "萨卡": "England",
    "福登": "England", "赖斯": "England", "沃特金斯": "England",
    "戈登": "England", "廷伯": "Netherlands", "詹姆斯": "England",
    "皮克福德": "England", "亨德森": "England", "格伊": "England",
    "特拉福德": "England", "安德森": "England", "鲍曼": "Germany",
    "马杜埃凯": "England", "埃泽": "England", "特罗萨德": "England",
    "拉亚": "Spain", "苏维门迪": "Spain", "梅里诺": "Spain",
    # 西班牙
    "罗德里": "Spain", "佩德里": "Spain", "加维": "Spain",
    "尼科·威廉姆斯": "Spain", "亚马尔": "Spain", "奥尔莫": "Spain",
    "格里马尔多": "Spain", "库巴西": "Spain", "德容": "Spain",
    "拉菲尼亚": "Brazil", "费兰·托雷斯": "Spain", "略伦特": "Spain",
    "埃里克·加西亚": "Spain", "莫利纳": "Argentina", "巴尔科": "Argentina",
    "西蒙": "Spain", "埃雷拉": "Spain", "巴斯克斯": "Spain",
    "奥亚萨瓦尔": "Spain", "伊格莱西亚斯": "Spain", "穆尼奥斯": "Spain",
    # 德国
    "基米希": "Germany", "穆西亚拉": "Germany", "维尔茨": "Germany",
    "维尔茨": "Germany", "诺伊尔": "Germany", "塔": "Germany",
    "于帕梅卡诺": "Germany", "帕夫洛维奇": "Germany", "格雷茨卡": "Germany",
    "努贝尔": "Germany", "萨内": "Germany", "卡尔": "Germany",
    "施蒂勒": "Germany", "翁达夫": "Germany", "莱韦林": "Germany",
    "沃尔特马德": "Germany", "泰阿特": "Italy", "劳姆": "Germany",
    "宽萨": "England", "弗莱肯": "Germany", "阿米里": "Germany",
    "布朗": "England",
    # 巴西
    "维尼修斯": "Brazil", "维蒂尼亚": "Brazil", "罗德里戈": "Brazil",
    "拉菲尼亚": "Brazil", "内马尔": "Brazil", "恩德里克": "Brazil",
    # 意大利
    "巴雷拉": "Italy", "托纳利": "Italy", "多纳鲁马": "Italy",
    "L·马丁内斯": "Argentina", "巴斯托尼": "Italy", "迪马尔科": "Italy",
    "德温特": "Netherlands", "冈萨雷斯": "Argentina", "维加": "Argentina",
    "库普梅纳斯": "Netherlands", "菲利克斯": "Portugal",
    "德布劳内": "Belgium", "卢卡库": "Belgium", "默尼耶": "Belgium",
    "德凯特拉雷": "Belgium", "德罗恩": "Belgium", "帕雷德斯": "Argentina",
    "萨勒马克尔斯": "Belgium", "韦斯利": "Brazil", "伊巴涅斯": "Mexico",
    # 克罗地亚
    "莫德里奇": "Croatia",
    # 波兰
    "莱万多夫斯基": "Poland",
    # 乌拉圭
    "努涅斯": "Uruguay", "阿劳霍": "Uruguay", "乌加特": "Uruguay",
    "阿尔瓦雷斯(Uru)": "Uruguay",
    # 塞尔维亚
    "弗拉霍维奇": "Serbia", "约维奇": "Serbia",
    # 日本
    "三笘薰": "Japan", "远藤航": "Japan", "久保建英": "Japan",
    # 韩国
    "孙兴慜": "South Korea",
    # 挪威
    "哈兰德": "Norway", "厄德高": "Norway",
    # 喀麦隆
    "巴索戈": "Cameroon",
    # 加拿大
    "戴维斯": "Canada",
    # 墨西哥
    "奥乔亚": "Mexico", "阿特亚加": "Mexico", "马丁(Mex)": "Mexico",
    "皮内达": "Mexico", "安图尼亚": "Mexico", "贝加": "Mexico",
    "科塔": "Mexico", "马拉贡": "Mexico", "卡洛斯·罗德里格斯": "Mexico",
    "洛萨诺": "Mexico", "马赛多": "Mexico",
    # 沙特
    "法比尼奥": "Brazil", "坎特": "France",
    # 哥伦比亚
    "路易斯·迪亚斯": "Colombia",
    # 埃及
    "萨拉赫": "Egypt",
    # 塞内加尔
    "马内": "Senegal",
    # 摩洛哥
    "阿什拉夫": "Morocco", "齐耶赫": "Morocco",
    # 尼日利亚
    "奥西梅恩": "Nigeria",
    # 美国
    "普利希奇": "USA", "麦肯尼": "USA",
    # 伊朗
    "阿兹蒙": "Iran",
    # 澳大利亚
    "古德温": "Australia",
    # 厄瓜多尔
    "凯塞多": "Ecuador",
    # 秘鲁
    "格伊": "Peru",
    # 牙买加
    "安东尼奥": "Jamaica",
    # 厄瓜多尔
    "恩纳·瓦伦西亚": "Ecuador",
    # 加纳
    "托马斯(加纳)": "Ghana", "库杜斯": "Ghana", "乔丹·阿尤": "Ghana",
    # 阿尔及利亚
    "本纳塞尔": "Algeria", "本拉赫马": "Algeria",
    # 突尼斯
    "汉尼拔": "Tunisia",
    # 哥斯达黎加"
    "纳瓦斯": "CostaRica",
    # 喀麦隆
    "奥纳纳": "Cameroon", "巴索戈": "Cameroon",
    # 中国
    "武磊": "China", "张琳芃": "China", "蒋光太": "China",
    # ===== 以下为全名球员补充映射 =====
    # 墨西哥
    "马丁(Mex)": "Mexico", "马丁": "Mexico",
    # 巴西
    "阿利松": "Brazil", "加布里埃尔": "Brazil", "达尼洛": "Brazil",
    "卢卡斯·帕奎塔": "Brazil", "马丁内利": "Brazil", "马特乌斯·库尼亚": "Brazil",
    "伊戈尔·蒂亚戈": "Brazil", "拉扬": "Morocco",
    "莱昂·佩雷拉": "Brazil", "阿莱士·桑德罗": "Brazil", "达尼洛(Bra)": "Brazil",
    # 阿根廷
    "胡安·穆索": "Argentina", "格罗尼莫·鲁利": "Argentina", "西蒙尼": "Argentina",
    "尼科·帕斯": "Argentina", "本哈明·洛佩斯": "Argentina",
    # 法国
    "科纳特": "France", "卢卡斯·埃尔南德斯": "France", "特奥·埃尔南德斯": "France",
    "扎伊尔·埃梅里": "France", "图拉姆": "France",
    # 德国
    "曼努埃尔·诺伊尔": "Germany", "奥利弗·鲍曼": "Germany", "亚历山大·努贝尔": "Germany",
    "安东尼奥·吕迪格": "Germany", "尼科·施洛特贝克": "Germany", "若纳坦·塔": "Germany",
    "达维德·劳姆": "Germany", "约书亚·基米希": "Germany", "瓦尔德马·安东": "Germany",
    "马利克·佳夫": "Germany", "纳撒尼尔·布朗": "Germany", "帕斯卡尔·格罗斯": "Germany",
    "费利克斯·恩梅查": "Germany", "亚历山大·帕夫洛维奇": "Germany",
    "安杰洛·施蒂勒": "Germany", "莱昂·格雷茨卡": "Germany", "贾马尔·穆西亚拉": "Germany",
    "弗洛里安·维尔茨": "Germany", "勒鲁瓦·萨内": "Germany", "马克西米利安·拜尔": "Germany",
    "德尼兹·翁达夫": "Germany", "伦纳特·卡尔": "Germany", "纳迪姆·阿米里": "Germany",
    "杰米·莱韦林": "Germany", "尼克·沃尔特马德": "Germany",
    # 英格兰
    "迪恩·亨德森": "England", "詹姆斯·特拉福德": "England",
    "里斯·詹姆斯": "England", "蒂诺·利夫拉门托": "England", "约翰·斯通斯": "England",
    "马克·格伊": "England", "埃兹里·宽萨": "England", "埃兹里·孔萨": "England",
    "丹·伯恩": "England", "杰德·斯彭斯": "England", "裘德·贝林厄姆": "England",
    "德克兰·赖斯": "England", "科比·梅努": "England", "埃贝雷奇·埃泽": "England",
    "摩根·罗杰斯": "England", "乔丹·亨德森": "England", "埃利奥特·安德森": "England",
    "哈里·凯恩": "England", "布卡约·萨卡": "England", "安东尼·戈登": "England",
    "奥利·沃特金斯": "England", "诺尼·马杜埃凯": "England", "伊万·托尼": "England",
    "马库斯·拉什福德": "England",
    # 西班牙
    "乌奈·西蒙": "Spain", "大卫·拉亚": "Spain", "霍安·加西亚": "Spain",
    "普比尔": "Spain", "马科斯·略伦特": "Spain", "法比安·鲁伊斯": "Spain",
    "马丁·苏维门迪": "Spain", "巴埃纳": "Spain", "达尼·奥尔莫": "Spain",
    "耶雷米·皮诺": "Spain", "博尔哈·伊格莱西亚斯": "Spain", "维克托·穆尼奥斯": "Spain",
    # 葡萄牙
    "若泽·萨": "Portugal", "迪奥戈·达洛特": "Portugal", "马修斯·努内斯": "Portugal",
    "尼尔森·塞梅多": "Portugal", "若昂·坎塞洛": "Portugal", "雷纳托·维加": "Portugal",
    "托马斯·阿劳霍": "Portugal", "伯纳多·席尔瓦": "Portugal", "萨穆·科斯塔": "Portugal",
    "若昂·菲利克斯": "Portugal", "弗朗西斯科·特林康": "Portugal",
    "弗朗西斯科·孔塞桑": "Portugal", "佩德罗·内托": "Portugal", "贡萨洛·格德斯": "Portugal",
    "若昂·坎塞洛": "Portugal", "马蒂亚斯·费尔南德斯·帕尔多": "Portugal",
    # 荷兰
    "鲁夫斯": "Netherlands", "范戴克": "Netherlands", "邓弗里斯": "Netherlands",
    "朱利安·廷伯": "Netherlands", "马茨·维费尔": "Netherlands",
    "赫拉芬贝赫": "Netherlands", "昆滕·廷伯": "Netherlands", "加克波": "Netherlands",
    "贾斯汀·克鲁伊维特": "Netherlands",
    # 比利时
    "诺阿·朗": "Belgium", "蒂博·库尔图瓦": "Belgium", "森内·拉门斯": "Belgium",
    "迈克·彭德斯": "Belgium", "蒂莫西·卡斯塔涅": "Belgium", "泽诺·德巴斯特": "Belgium",
    "马克西姆·德凯特拉雷": "Belgium", "科尼·德温特": "Belgium",
    "布兰登·梅赫勒": "Belgium", "托马斯·默尼耶": "Belgium", "内森·恩戈伊": "Belgium",
    "华金·塞斯": "Belgium", "阿尔图尔·泰阿特": "Belgium",
    "凯文·德布劳内": "Belgium", "阿马杜·奥纳纳": "Belgium",
    "尼古拉斯·拉斯金": "Belgium", "尤里·蒂勒曼斯": "Belgium",
    "汉斯·瓦纳肯": "Belgium", "阿克塞尔·维特塞尔": "Belgium",
    "夏尔·德凯特拉雷": "Belgium", "热雷米·多库": "Belgium",
    "罗梅卢·卢卡库": "Belgium", "多迪·卢克巴基奥": "Belgium",
    "迭戈·莫雷拉": "Belgium", "亚历克西斯·萨勒马克尔斯": "Belgium",
    "莱安德罗·特罗萨德": "Belgium",
    # 其他
    "托尼": "England",
    "拉波尔特": "Spain",
    "德佩": "Netherlands",
    "帕斯": "Argentina",
    "桑巴": "Brazil",
    "塔利亚菲科": "Argentina",
    "阿尔马达": "Argentina",
    "洛佩斯(Bra)": "Brazil",
    "梅迪纳": "Argentina",
    "希梅内斯": "Uruguay",
    "卡斯塔涅": "Belgium",
    "帕奎塔": "Brazil",
    "萨默维尔": "England",
    "伊戈尔": "Brazil",
    "克鲁伊维特": "Netherlands",
    "恩戈伊": "France",
    "拉斯金": "Scotland",
    "莫雷拉": "Uruguay",
    "里塞": "France",
    "蒂尔": "Netherlands",
    "洛塞尔索": "Argentina",
    "韦霍斯特": "Netherlands",
    "布罗贝": "Netherlands",
    "哈托": "Netherlands",
    "恩圭亚": "Cameroon",
    "瓦纳肯": "Belgium",
    "梅赫勒": "Belgium",
    "塞斯": "Belgium",
    "朗": "Belgium",
    "鲁利": "Argentina",
    "巴列尔迪": "Argentina",
    "拉比奥特": "France",
    "科斯塔(Fr)": "France",
    "格德斯": "Brazil",
    "阿劳霍(Por)": "Uruguay",
    "费尔南德斯": "Portugal",
    "孔德(Sp)": "France",
    "加利亚多": "Mexico",
    "蒙特斯": "Mexico",
    "罗莫": "Mexico",
    "科尔多瓦": "Mexico",
    "莱奥·佩雷拉": "Brazil",
    "阿莱士·桑德罗": "Brazil",
    "达尼洛(Bra)": "Brazil",
    "韦弗顿": "Brazil",
    "本哈明": "Argentina",
    "瓜尔达多": "Mexico",
    "阿克": "Netherlands",
    "赖因德斯": "Netherlands",
    "多库": "Belgium",
    "埃德森": "Brazil",
    "斯通斯": "England",
    "谢尔基": "France",
    "奥赖利": "Ireland",
    "努内斯": "Uruguay",
    "埃梅里": "France",
    "埃尔南德斯(Luc)": "France",
    "鲁伊斯": "Spain",
    "马尔基尼奥斯": "Brazil",
    "詹": "Scotland",
    "彭德斯": "Netherlands",
    "内托(Pedro)": "Portugal",
    "古斯托": "France",
    "詹姆斯(Reese)": "England",
    "库库雷利亚": "Spain",
    "布雷默": "Brazil",
    "维加(Juan)": "Argentina",
    "德温特(Stef)": "Netherlands",
    "孔萨(Ezri)": "England",
    "迪涅": "France",
    "罗杰斯": "England",
    "德凯特拉雷(Max)": "Belgium",
    "奥纳娜(Ama)": "Cameroon",
    "蒂勒曼斯": "Belgium",
    "达洛特": "Portugal",
    "梅努": "England",
    "库尼亚": "Brazil",
    "拉门斯": "Netherlands",
    "卡塞米罗": "Brazil",
    "佳夫": "IvoryCoast",
    "利夫拉门托": "England",
    "伯恩(Dan)": "England",
    "施洛特贝克": "Germany",
    "安东(Waldemar)": "Germany",
    "恩梅查": "Germany",
    "拜尔": "Germany",
    "马伦": "Netherlands",
    "拉扬(Rayan)": "Morocco",
    "格罗斯": "Germany",
    "范赫克": "Netherlands",
    "维费尔": "Netherlands",
    "斯彭斯(Jed)": "England",
    "波罗": "Spain",
    "范德芬": "England",
    "帕拉西奥斯": "Argentina",
    "宽萨(Ezri)": "England",
    "迈尼昂": "France",
    "特奥": "France",
    "费利克斯": "Portugal",
    "拉克鲁瓦": "France",
    "马特塔(Nicolas)": "France",
    "亨德森(Dean)": "England",
    "费布吕亨": "Netherlands",
    "廷伯(Quenty)": "Netherlands",
    "道格拉斯·桑托斯": "Brazil",
    "路易斯·恩里克": "Spain",
    "卢克巴基奥": "DR Congo",
    "多迪": "France",
    "加文": "Wales",
    "纳撒尼尔": "England",
    "尼古拉斯": "Scotland",
    "迭戈": "Uruguay",
    "若昂(Goncalo)": "Portugal",
    # ===== HTML大名单中32支球队球员国籍补充 =====
    # 阿尔及利亚
    "曼迪": "Algeria",
    "奥基贾": "Algeria",
    "塞尤德": "Algeria",
    "塔赫": "Algeria",
    "哈吉": "Algeria",
    "本塞拜尼": "Algeria",
    "阿塔勒": "Algeria",
    "库拉米": "Algeria",
    "费尔哈特": "Algeria",
    "本纳塞尔": "Algeria",
    "格迪奥拉": "Algeria",
    "贝勒哈吉": "Algeria",
    "阿德莱": "Algeria",
    "马赫雷斯": "Algeria",
    "斯利马里": "Algeria",
    "布代布": "Algeria",
    # 澳大利亚
    "瑞恩": "Australia",
    "雷德梅尼": "Australia",
    "保罗": "Australia",
    "卡拉季奇": "Australia",
    "苏塔": "Australia",
    "比伊奇": "Australia",
    "罗尔斯": "Australia",
    "德格内克": "Australia",
    "阿特金森": "Australia",
    "穆伊": "Australia",
    "赫鲁斯蒂奇": "Australia",
    "杰克逊·欧文": "Australia",
    "古德温": "Australia",
    "博斯": "Australia",
    "塔加特": "Australia",
    "杜克": "Australia",
    "马比尔": "Australia",
    "库奥尔": "Australia",
    # 奥地利
    "施拉格尔": "Austria",
    "林德纳": "Austria",
    "彭特克": "Austria",
    "阿拉巴": "Austria",
    "波施": "Austria",
    "林哈特": "Austria",
    "丹索": "Austria",
    "乌尔默": "Austria",
    "弗里德尔": "Austria",
    "萨比策": "Austria",
    "鲍姆加特纳": "Austria",
    "格里格里": "Austria",
    "塞瓦尔德": "Austria",
    "伊尔桑克": "Austria",
    "阿瑙托维奇": "Austria",
    "格雷戈里奇": "Austria",
    "奥尼西沃": "Austria",
    "凯恩茨": "Austria",
    # 波黑
    "谢希奇": "Bosnia",
    "布尔克诺维奇": "Bosnia",
    "科瓦切维奇": "Bosnia",
    "科德罗": "Bosnia",
    "阿伊特": "Bosnia",
    "奥斯特里奇": "Bosnia",
    "哈济亚赫梅托维奇": "Bosnia",
    "布尔佐尔": "Bosnia",
    "皮里奇": "Bosnia",
    "梅迪奇": "Bosnia",
    "塔拉普萨诺维奇": "Bosnia",
    "哈杜里": "Bosnia",
    "贾科维奇": "Bosnia",
    "克鲁尼奇": "Bosnia",
    "哲科": "Bosnia",
    "德米罗维奇": "Bosnia",
    "阿佐拉季奇": "Bosnia",
    "哈利霍季奇": "Bosnia",
    # 加拿大
    "博扬": "Canada",
    "迪恩": "Canada",
    "圣克莱尔": "Canada",
    "维多利亚": "Canada",
    "约翰斯顿": "Canada",
    "米勒": "Canada",
    "阿德库格贝": "Canada",
    "科纳特": "Canada",
    "拉耶": "Canada",
    "布坎南": "Canada",
    "埃克波罗": "Canada",
    "尤斯塔基奥": "Canada",
    "奥斯瓦尔多": "Canada",
    "皮内达": "Canada",
    "拉林": "Canada",
    "戴维": "Canada",
    "凯尔": "Canada",
    "乌切·奥比": "Canada",
    "洛伊": "Canada",
    # 佛得角
    "比绍": "CapeVerde",
    "丰塞卡": "CapeVerde",
    "罗萨": "CapeVerde",
    "塞梅多": "CapeVerde",
    "贡萨尔维斯": "CapeVerde",
    "达格拉萨": "CapeVerde",
    "塔瓦雷斯": "CapeVerde",
    "阿尔梅达": "CapeVerde",
    "桑托斯": "CapeVerde",
    "帕苏": "CapeVerde",
    "洛伦索": "CapeVerde",
    "莫赖斯": "CapeVerde",
    "加尔迪尼亚": "CapeVerde",
    "科雷亚": "CapeVerde",
    # 哥伦比亚
    "奥斯皮纳": "Colombia",
    "夸德拉多": "Colombia",
    "达文森·桑切斯": "Colombia",
    "库拉亚": "Colombia",
    "莫希卡": "Colombia",
    "梅迪纳": "Colombia",
    "卡拉斯卡尔": "Colombia",
    "卢库米": "Colombia",
    "J罗": "Colombia",
    "乌里韦": "Colombia",
    "金特罗": "Colombia",
    "卡斯塔诺": "Colombia",
    "阿里亚斯": "Colombia",
    "博雷": "Colombia",
    "科尔多瓦": "Colombia",
    "法尔考": "Colombia",
    "杜万·萨帕塔": "Colombia",
    # 库拉索
    "罗梅罗": "Curacao",
    "海鲁": "Curacao",
    "帕特": "Curacao",
    "维克托": "Curacao",
    "巴克": "Curacao",
    "马蒂纳": "Curacao",
    "特罗斯特": "Curacao",
    "贝克尔": "Curacao",
    "库恩": "Curacao",
    "范德沃斯特": "Curacao",
    "施密德": "Curacao",
    "卡斯特拉恩": "Curacao",
    "贝多芬": "Curacao",
    "哈赛因·阿科斯塔": "Curacao",
    "范金克尔": "Curacao",
    "德伊弗": "Curacao",
    "格隆": "Curacao",
    # 捷克
    "帕夫伦卡": "Czech",
    "曼道尔": "Czech",
    "亚罗斯": "Czech",
    "曹法尔": "Czech",
    "库德拉": "Czech",
    "马夫帕": "Czech",
    "霍莱克": "Czech",
    "津马切克": "Czech",
    "克雷伊奇": "Czech",
    "绍切克": "Czech",
    "达里达": "Czech",
    "卡拉尔": "Czech",
    "尤雷奇卡": "Czech",
    "林格尔": "Czech",
    "萨迪莱克": "Czech",
    "库赫塔": "Czech",
    "希克": "Czech",
    "乔里": "Czech",
    "克伊卡": "Czech",
    # 刚果民主共和国
    "姆博洛": "DR Congo",
    "基卡": "DR Congo",
    "帕德博": "DR Congo",
    "姆本巴": "DR Congo",
    "卢因达马": "DR Congo",
    "图萨": "DR Congo",
    "埃克西米": "DR Congo",
    "卡班吉": "DR Congo",
    "恩甘杜": "DR Congo",
    "恩巴洛": "DR Congo",
    "姆韦普": "DR Congo",
    "奥卡·昂巴尔": "DR Congo",
    "阿塞科": "DR Congo",
    "卡耶塞卡": "DR Congo",
    "巴坎布": "DR Congo",
    "姆武梅卡": "DR Congo",
    "埃克特": "DR Congo",
    "伊塞卡": "DR Congo",
    # 厄瓜多尔
    "多明戈斯": "Ecuador",
    "加林德斯": "Ecuador",
    "拉斯特": "Ecuador",
    "因蒂亚格拉": "Ecuador",
    "波罗索": "Ecuador",
    "帕乔": "Ecuador",
    "安赫洛": "Ecuador",
    "科罗佐": "Ecuador",
    "门德斯": "Ecuador",
    "派斯": "Ecuador",
    "弗朗哥": "Ecuador",
    "雷内斯": "Ecuador",
    "瓦伦西亚": "Ecuador",
    "凯塞多": "Ecuador",
    "雷莫": "Ecuador",
    # 埃及
    "阿布加巴拉": "Egypt",
    "谢纳维": "Egypt",
    "舍哈塔": "Egypt",
    "哈桑": "Egypt",
    "阿卜杜勒莫内姆": "Egypt",
    "埃尔沙赫比": "Egypt",
    "阿布·阿尔巴西尔": "Egypt",
    "卡德尔": "Egypt",
    "哈姆迪": "Egypt",
    "萨拉赫": "Egypt",
    "埃尔内尼": "Egypt",
    "索里": "Egypt",
    "陶菲克": "Egypt",
    "穆斯塔法·穆罕默德": "Egypt",
    "阿卜杜勒法塔赫": "Egypt",
    "齐佐": "Egypt",
    # 加纳
    "门萨": "Ghana",
    "瓦巴西": "Ghana",
    "夸拉塔": "Ghana",
    "阿马泰": "Ghana",
    "塞尤": "Ghana",
    "易卜拉希马·迪亚洛": "Ghana",
    "奥杜阿": "Ghana",
    "阿卜杜勒-哈米德": "Ghana",
    "托马斯·帕蒂": "Ghana",
    "库杜斯": "Ghana",
    "安德烈·阿尤": "Ghana",
    "乔丹·阿尤": "Ghana",
    "伊尼亚图·威廉斯": "Ghana",
    "布卡里": "Ghana",
    "塞门霍": "Ghana",
    "科菲·库杜斯": "Ghana",
    # 海地
    "普雷沃斯特": "Haiti",
    "奥古斯丁": "Haiti",
    "斯蒂芬": "Haiti",
    "日尔曼": "Haiti",
    "阿皮森": "Haiti",
    "阿尔库贝": "Haiti",
    "查托": "Haiti",
    "皮埃尔": "Haiti",
    "纳松": "Haiti",
    "阿尔塞诺": "Haiti",
    "艾蒂安": "Haiti",
    "洛昂": "Haiti",
    "蒙泰斯": "Haiti",
    "巴巴斯": "Haiti",
    # 伊朗
    "贝兰万德": "Iran",
    "阿比德扎德": "Iran",
    "侯赛因·侯赛尼": "Iran",
    "卡纳尼": "Iran",
    "哈伊萨菲": "Iran",
    "穆罕默迪": "Iran",
    "霍达埃": "Iran",
    "阿米里": "Iran",
    "穆赫比": "Iran",
    "埃扎托拉希": "Iran",
    "努拉伊": "Iran",
    "阿格贾万德": "Iran",
    "贾汉巴赫什": "Iran",
    "塔雷米": "Iran",
    "阿兹蒙": "Iran",
    "迈赫迪·托拉比": "Iran",
    "礼萨伊": "Iran",
    # 伊拉克
    "贾拉尔·哈桑": "Iraq",
    "阿米尔·阿尔-阿米里": "Iraq",
    "穆罕默德·加齐": "Iraq",
    "艾哈迈德·伊卜拉欣": "Iraq",
    "阿里·法伊兹": "Iraq",
    "沙基尔·法伊兹": "Iraq",
    "侯赛因·阿里": "Iraq",
    "雷宾·苏迈里": "Iraq",
    "穆塔巴尔·阿卜杜勒拉扎克": "Iraq",
    "阿姆贾德·阿塔尔": "Iraq",
    "阿里·贾西姆": "Iraq",
    "齐丹·雅各布": "Iraq",
    "易卜拉欣·盖斯": "Iraq",
    "侯赛因·赛义德": "Iraq",
    "阿里·胡塞因": "Iraq",
    "穆罕默德·阿里·阿里": "Iraq",
    "艾哈迈德·亚辛": "Iraq",
    "阿比尔·苏迈里": "Iraq",
    # 科特迪瓦
    "桑加雷": "IvoryCoast",
    "伊拉": "IvoryCoast",
    "巴巴卡尔·科内": "IvoryCoast",
    "拜利": "IvoryCoast",
    "卡诺特": "IvoryCoast",
    "迪奥芒德": "IvoryCoast",
    "卡德": "IvoryCoast",
    "巴巴": "IvoryCoast",
    "塞里": "IvoryCoast",
    "康特": "IvoryCoast",
    "阿莱": "IvoryCoast",
    "迪耶": "IvoryCoast",
    "佩佩": "IvoryCoast",
    "尼昂": "IvoryCoast",
    "科尼": "IvoryCoast",
    "博埃": "IvoryCoast",
    # 约旦
    "亚辛·布沙": "Jordan",
    "拉比·阿布·萨杜赫": "Jordan",
    "穆罕默德·谢尔马特": "Jordan",
    "穆罕默德·穆巴赫": "Jordan",
    "亚辛·萨勒姆": "Jordan",
    "阿纳斯·阿尔苏莱曼": "Jordan",
    "哈利勒·马阿纳": "Jordan",
    "阿卜杜勒拉赫曼·萨利姆": "Jordan",
    "塔拉勒·阿卜杜拉": "Jordan",
    "萨拉赫·阿尔苏莱曼": "Jordan",
    "奥马尔·阿尔马伊": "Jordan",
    "阿布杜拉赫曼·阿布·扎赫拉": "Jordan",
    "穆萨·阿尔苏莱曼": "Jordan",
    "尼扎尔·拉什丹": "Jordan",
    "穆尼尔·阿尔哈马登": "Jordan",
    "叶海亚·阿尔苏莱曼": "Jordan",
    "哈立德·阿尔苏莱曼": "Jordan",
    "艾哈迈德·阿尔苏莱曼": "Jordan",
    # 新西兰
    "塞莱": "NewZealand",
    "马里诺维奇": "NewZealand",
    "古斯曼": "NewZealand",
    "温斯顿·里德": "NewZealand",
    "伯克萨尔": "NewZealand",
    "佩恩": "NewZealand",
    "斯蒂芬斯": "NewZealand",
    "卡卡切": "NewZealand",
    "科尔": "NewZealand",
    "罗杰斯": "NewZealand",
    "英斯": "NewZealand",
    "刘易斯": "NewZealand",
    "拉姆": "NewZealand",
    "巴巴鲁塞": "NewZealand",
    "克里斯·伍德": "NewZealand",
    "巴巴塞克": "NewZealand",
    "贾斯汀·史密斯": "NewZealand",
    "萨顿": "NewZealand",
    # 挪威
    "尼兰德": "Norway",
    "塞尔特": "Norway",
    "阿热": "Norway",
    "斯特朗博格": "Norway",
    "埃拉贝格": "Norway",
    "诺曼": "Norway",
    "拉尔松": "Norway",
    "梅林": "Norway",
    "厄德高": "Norway",
    "托斯比": "Norway",
    "奥克纳斯": "Norway",
    "贝尔格": "Norway",
    "瑟尔洛德": "Norway",
    "哈兰德": "Norway",
    "索尔洛特": "Norway",
    "厄斯蒂加德": "Norway",
    "尤尔根·拉尔森": "Norway",
    # 巴拿马
    "卡尔德龙": "Panama",
    "梅吉亚": "Panama",
    "冈萨雷斯": "Panama",
    "穆查多": "Panama",
    "埃斯科瓦尔": "Panama",
    "阿梅洛": "Panama",
    "格雷罗": "Panama",
    "阿吉拉尔": "Panama",
    "费尔南德斯": "Panama",
    "库珀": "Panama",
    "戈多伊": "Panama",
    "巴尔塞纳斯": "Panama",
    "迪亚斯": "Panama",
    "法哈多": "Panama",
    "阿罗约": "Panama",
    "布拉斯奎斯": "Panama",
    # 巴拉圭
    "加蒂托": "Paraguay",
    "洛佩斯": "Paraguay",
    "梅扎拉玛": "Paraguay",
    "戈麦斯": "Paraguay",
    "巴尔武埃纳": "Paraguay",
    "阿隆索": "Paraguay",
    "罗德里格斯": "Paraguay",
    "萨拉维阿": "Paraguay",
    "阿尔德雷特": "Paraguay",
    "库瓦斯": "Paraguay",
    "桑切斯": "Paraguay",
    "卡巴纳斯": "Paraguay",
    "佩雷斯": "Paraguay",
    "贝尼特斯": "Paraguay",
    "罗哈斯": "Paraguay",
    "莫雷蒂": "Paraguay",
    # 卡塔尔
    "阿尔希卜": "Qatar",
    "Barsham": "Qatar",
    "阿里": "Qatar",
    "Miguel": "Qatar",
    "Khoukhi": "Qatar",
    "Al-Rawi": "Qatar",
    "Hassan": "Qatar",
    "Tamba": "Qatar",
    "Asim Madibo": "Qatar",
    "Al-Haydos": "Qatar",
    "Muneer": "Qatar",
    "Alaeldin": "Qatar",
    "Afif": "Qatar",
    "Ali": "Qatar",
    "Rashid": "Qatar",
    # 沙特阿拉伯
    "布诺坎": "Saudi",
    "阿尔-奥维斯": "Saudi",
    "阿尔-亚米": "Saudi",
    "阿尔-阿赫萨里": "Saudi",
    "阿尔-布迪": "Saudi",
    "阿尔-沙赫拉尼": "Saudi",
    "阿尔-瓦沙里": "Saudi",
    "阿尔-卡塔尼": "Saudi",
    "坦巴蒂": "Saudi",
    "阿尔-法拉伊": "Saudi",
    "阿尔-马勒基": "Saudi",
    "阿尔-阿姆里": "Saudi",
    "卡诺": "Saudi",
    "多萨里": "Saudi",
    "阿尔-希门尼斯": "Saudi",
    "阿尔-布莱坎": "Saudi",
    "阿尔-哈姆丹": "Saudi",
    "阿尔-纳赫利": "Saudi",
    # 苏格兰
    "冈恩": "Scotland",
    "克拉克": "Scotland",
    "凯利": "Scotland",
    "罗伯逊": "Scotland",
    "蒂尔尼": "Scotland",
    "汉利": "Scotland",
    "波蒂厄斯": "Scotland",
    "拉什": "Scotland",
    "亨得利": "Scotland",
    "麦克托米奈": "Scotland",
    "麦金": "Scotland",
    "克里斯蒂": "Scotland",
    "麦格雷戈": "Scotland",
    "弗雷泽": "Scotland",
    "摩根": "Scotland",
    "亚当斯": "Scotland",
    "戴克斯": "Scotland",
    "切·亚当斯": "Scotland",
    # 塞内加尔
    "门迪": "Senegal",
    "戈米": "Senegal",
    "阿尔弗雷德·戈米": "Senegal",
    "库利巴利": "Senegal",
    "迪亚洛": "Senegal",
    "巴洛-图雷": "Senegal",
    "雅各布斯": "Senegal",
    "萨巴利": "Senegal",
    "塞克": "Senegal",
    "盖耶": "Senegal",
    "纳帕·门迪": "Senegal",
    "西斯": "Senegal",
    "萨尔": "Senegal",
    "马内": "Senegal",
    "伊斯梅拉·萨尔": "Senegal",
    "尼古拉斯·杰克逊": "Senegal",
    "迪昂": "Senegal",
    # 南非
    "威廉斯": "SouthAfrica",
    "楚库巴": "SouthAfrica",
    "克雷格": "SouthAfrica",
    "莫伊塞·科阿迪": "SouthAfrica",
    "范维永": "SouthAfrica",
    "洛克": "SouthAfrica",
    "穆哈迪": "SouthAfrica",
    "库里巴利": "SouthAfrica",
    "克劳斯": "SouthAfrica",
    "莫科埃纳": "SouthAfrica",
    "桑杜": "SouthAfrica",
    "林德维克": "SouthAfrica",
    "佐埃": "SouthAfrica",
    "费舍尔": "SouthAfrica",
    "奥斯尼": "SouthAfrica",
    "恩特什": "SouthAfrica",
    "佩克瑟卡尼": "SouthAfrica",
    "莫科卡": "SouthAfrica",
    # 瑞典
    "罗达克": "Sweden",
    "林德": "Sweden",
    "诺德菲尔特": "Sweden",
    "林德洛夫": "Sweden",
    "丹尼尔森": "Sweden",
    "奥古斯丁松": "Sweden",
    "赫兰德": "Sweden",
    "斯塔费尔特": "Sweden",
    "约谈": "Sweden",
    "福斯贝里": "Sweden",
    "埃克雷格": "Sweden",
    "卡朱斯特": "Sweden",
    "库霍尔德": "Sweden",
    "本特松": "Sweden",
    "伊萨克": "Sweden",
    "杜尔马斯松": "Sweden",
    "克朗松": "Sweden",
    # 瑞士
    "索默": "Switzerland",
    "科贝尔": "Switzerland",
    "姆沃戈": "Switzerland",
    "阿坎吉": "Switzerland",
    "埃尔维迪": "Switzerland",
    "沙尔里奇": "Switzerland",
    "里卡多·罗德里格斯": "Switzerland",
    "乌多凯": "Switzerland",
    "科默雷拉": "Switzerland",
    "扎卡": "Switzerland",
    "扎卡里亚": "Switzerland",
    "弗罗伊勒": "Switzerland",
    "索乌": "Switzerland",
    "阿比彻": "Switzerland",
    "恩多耶": "Switzerland",
    "恩博洛": "Switzerland",
    "阿姆杜尼": "Switzerland",
    "巴尔加斯": "Switzerland",
    "奥卡福": "Switzerland",
    "沙奇里": "Switzerland",
    # 突尼斯
    "本·阿耶斯": "Tunisia",
    "马斯洛斯": "Tunisia",
    "哈姆扎·马特洛特": "Tunisia",
    "伊法": "Tunisia",
    "梅尔贝": "Tunisia",
    "德雷塞尔": "Tunisia",
    "阿布迪": "Tunisia",
    "卡德里": "Tunisia",
    "贾齐里": "Tunisia",
    "哈兹里": "Tunisia",
    "斯希里": "Tunisia",
    "阿萨雷": "Tunisia",
    "阿布·法尔汉": "Tunisia",
    "拉伊迪": "Tunisia",
    "贾兹里": "Tunisia",
    "姆萨克尼": "Tunisia",
    "卡伊比": "Tunisia",
    # 土耳其
    "恰基尔": "Turkey",
    "巴因德尔": "Turkey",
    "德尼兹利": "Turkey",
    "切利克": "Turkey",
    "卡普兰": "Turkey",
    "巴尔达克": "Turkey",
    "穆尔杜尔": "Turkey",
    "艾哈迈德": "Turkey",
    "德米拉尔": "Turkey",
    "厄兹坎": "Turkey",
    "托帕尔": "Turkey",
    "科贾迪尔": "Turkey",
    "阿尔达·居勒": "Turkey",
    "亚尔辛": "Turkey",
    "伊尔迪兹": "Turkey",
    "阿克金": "Turkey",
    "云代尔": "Turkey",
    "塞里克": "Turkey",
    # 乌兹别克斯坦
    "叶尔加舍夫": "Uzbekistan",
    "尤苏波夫": "Uzbekistan",
    "伊斯拉姆库里耶夫": "Uzbekistan",
    "阿赫梅多夫": "Uzbekistan",
    "胡萨诺夫": "Uzbekistan",
    "马沙里波夫": "Uzbekistan",
    "卡里莫夫": "Uzbekistan",
    "阿利耶夫": "Uzbekistan",
    "赛义多夫": "Uzbekistan",
    "舒库罗夫": "Uzbekistan",
    "阿卜杜拉赫马托夫": "Uzbekistan",
    "贾苏尔·马尔肖耶夫": "Uzbekistan",
    "法伊祖拉耶夫": "Uzbekistan",
    "穆赫托罗夫": "Uzbekistan",
    "谢尔佐德·拉希莫夫": "Uzbekistan",
    "贾利洛夫": "Uzbekistan",
    "阿卜杜拉耶夫": "Uzbekistan",
    "图尔贡博耶夫": "Uzbekistan",
}

# 国家队热身赛对手
NT_OPPONENTS = {
    "Argentina": [("巴西", "FRI"), ("意大利", "FRI"), ("尼日利亚", "FRI")],
    "Portugal": [("克罗地亚", "FRI"), ("芬兰", "FRI")],
    "France": [("德国", "FRI"), ("智利", "FRI"), ("澳大利亚", "FRI")],
    "England": [("冰岛", "FRI"), ("波黑", "FRI")],
    "Spain": [("哥伦比亚", "FRI"), ("北爱尔兰", "FRI"), ("韩国", "FRI")],
    "Germany": [("法国", "FRI"), ("荷兰", "FRI"), ("乌克兰", "FRI")],
    "Brazil": [("阿根廷", "FRI"), ("美国", "FRI"), ("日本", "FRI")],
    "Italy": [("阿根廷", "FRI"), ("土耳其", "FRI"), ("波黑", "FRI")],
    "Netherlands": [("冰岛", "FRI"), ("苏格兰", "FRI")],
    "Belgium": [("黑山", "FRI"), ("卢森堡", "FRI")],
    "Mexico": [("瑞典", "FRI"), ("日本", "FRI")],
    "Uruguay": [("科特迪瓦", "FRI"), ("加纳", "FRI")],
    "Croatia": [("葡萄牙", "FRI"), ("波兰", "FRI")],
    "Poland": [("克罗地亚", "FRI"), ("土耳其", "FRI")],
    "Morocco": [("巴西", "FRI"), ("比利时", "FRI")],
    "Senegal": [("埃及", "FRI"), ("加纳", "FRI")],
    "USA": [("巴西", "FRI"), ("牙买加", "FRI")],
    "Colombia": [("西班牙", "FRI"), ("秘鲁", "FRI")],
    "Japan": [("韩国", "FRI"), ("巴西", "FRI"), ("土耳其", "FRI")],
    "South Korea": [("日本", "FRI"), ("中国", "FRI")],
    "Canada": [("埃及", "FRI"), ("新西兰", "FRI")],
    "Australia": [("英格兰", "FRI"), ("伊朗", "FRI")],
    "Scotland": [("荷兰", "FRI"), ("芬兰", "FRI")],
    "IvoryCoast": [("加纳", "FRI"), ("塞内加尔", "FRI")],
    "DR Congo": [("阿尔及利亚", "FRI"), ("突尼斯", "FRI")],
    "Wales": [{"name": "美国", "tag": "friendlies"}],
    "Ireland": [{"name": "瑞士", "tag": "friendlies"}],
    "Cameroon": [{"name": "牙买加", "tag": "friendlies"}, {"name": "洪都拉斯", "tag": "friendlies"}],
    "China": [("韩国", "FRI"), ("泰国", "FRI")],
    "CostaRica": [{"name": "美国", "tag": "friendlies"}],
    "Ecuador": [{"name": "秘鲁", "tag": "friendlies"}],
    "Jamaica": [{"name": "喀麦隆", "tag": "friendlies"}],
    "Ghana": [{"name": "乌拉圭", "tag": "friendlies"}],
    "Algeria": [{"name": "刚果民主共和国", "tag": "friendlies"}],
    "Tunisia": [{"name": "刚果民主共和国", "tag": "friendlies"}],
    "Egypt": [{"name": "塞内加尔", "tag": "friendlies"}],
    "Nigeria": [{"name": "阿根廷", "tag": "friendlies"}, {"name": "沙特阿拉伯", "tag": "friendlies"}],
    "Iran": [{"name": "阿联酋", "tag": "friendlies"}],
    "Serbia": [{"name": "瑞典", "tag": "friendlies"}],
    "Norway": [{"name": "捷克", "tag": "friendlies"}],
    "Sweden": [{"name": "塞尔维亚", "tag": "friendlies"}],
    "Turkey": [{"name": "波兰", "tag": "friendlies"}, {"name": "日本", "tag": "friendlies"}],
    "Switzerland": [{"name": "爱尔兰", "tag": "friendlies"}],
    "Austria": [{"name": "塞尔维亚", "tag": "friendlies"}],
    "Denmark": [{"name": "挪威", "tag": "friendlies"}],
    "Finland": [{"name": "葡萄牙", "tag": "friendlies"}],
    "Chile": [{"name": "法国", "tag": "friendlies"}],
    "Peru": [{"name": "厄瓜多尔", "tag": "friendlies"}],
    "Paraguay": [{"name": "以色列", "tag": "friendlies"}],
    "Panama": [{"name": "哥斯达黎加", "tag": "friendlies"}],
    # ===== 补充32支球队的热身赛对手 =====
    "SouthAfrica": [("津巴布韦", "FRI"), ("莫桑比克", "FRI")],
    "Czech": [("斯洛伐克", "FRI"), ("波兰", "FRI")],
    "Bosnia": [("意大利", "FRI"), ("英格兰", "FRI")],
    "Qatar": [("伊朗", "FRI"), ("阿联酋", "FRI")],
    "Haiti": [("巴拿马", "FRI"), ("危地马拉", "FRI")],
    "NewZealand": [("澳大利亚", "FRI"), ("泰国", "FRI")],
    "Saudi": [("伊拉克", "FRI"), ("约旦", "FRI")],
    "Iraq": [("沙特阿拉伯", "FRI"), ("科威特", "FRI")],
    "Uzbekistan": [("塔吉克斯坦", "FRI"), ("伊朗", "FRI")],
    "Jordan": [("伊拉克", "FRI"), ("阿联酋", "FRI")],
    "CapeVerde": [("刚果民主共和国", "FRI"), ("科特迪瓦", "FRI")],
    "Bosnia": [("意大利", "FRI"), ("英格兰", "FRI")],
    "Curacao": [("荷兰", "FRI"), ("特立尼达", "FRI")],
}

# 国家队名称显示名
NT_DISPLAY_NAMES = {
    "Argentina": "阿根廷", "Portugal": "葡萄牙", "France": "法国",
    "England": "英格兰", "Spain": "西班牙", "Germany": "德国",
    "Brazil": "巴西", "Italy": "意大利", "Netherlands": "荷兰",
    "Belgium": "比利时", "Mexico": "墨西哥", "Uruguay": "乌拉圭",
    "Croatia": "克罗地亚", "Poland": "波兰", "Morocco": "摩洛哥",
    "Senegal": "塞内加尔", "USA": "美国", "Colombia": "哥伦比亚",
    "Japan": "日本", "South Korea": "韩国", "Canada": "加拿大",
    "Australia": "澳大利亚", "Scotland": "苏格兰", "IvoryCoast": "科特迪瓦",
    "DR Congo": "民主刚果", "Wales": "威尔士", "Ireland": "爱尔兰",
    "Cameroon": "喀麦隆", "China": "中国", "CostaRica": "哥斯达黎加",
    "Ecuador": "厄瓜多尔", "Jamaica": "牙买加", "Ghana": "加纳",
    "Algeria": "阿尔及利亚", "Tunisia": "突尼斯", "Egypt": "埃及",
    "Nigeria": "尼日利亚", "Iran": "伊朗", "Serbia": "塞尔维亚",
    "Norway": "挪威", "Sweden": "瑞典", "Turkey": "土耳其",
    "Switzerland": "瑞士", "Austria": "奥地利", "Denmark": "丹麦",
    "Finland": "芬兰", "Chile": "智利", "Peru": "秘鲁",
    "Paraguay": "巴拉圭", "Panama": "巴拿马",
    # ===== 32支球队显示名补充 =====
    "SouthAfrica": "南非", "Czech": "捷克", "Bosnia": "波黑",
    "Qatar": "卡塔尔", "Haiti": "海地",
    "NewZealand": "新西兰", "Saudi": "沙特阿拉伯",
    "Iraq": "伊拉克", "Uzbekistan": "乌兹别克斯坦", "Jordan": "约旦",
    "CapeVerde": "佛得角", "Curacao": "库拉索",
}


def get_club_info(club_name):
    """匹配俱乐部信息"""
    if not club_name or not club_name.strip():
        return DEFAULT_CLUB
    if club_name in CLUB_INFO:
        return CLUB_INFO[club_name]
    base = re.sub(r'\(.*?\)', '', club_name).strip()
    if base in CLUB_INFO:
        return CLUB_INFO[base]
    for key, val in CLUB_INFO.items():
        if base in key or key in base:
            return val
    return DEFAULT_CLUB


def get_nationality(player_name):
    """获取球员国籍"""
    if player_name in PLAYER_NATIONALITY:
        return PLAYER_NATIONALITY[player_name]
    # 尝试去掉星号等特殊符号再查
    clean = re.sub(r'[⭐★(C)\(\)]', '', player_name).strip()
    if clean in PLAYER_NATIONALITY:
        return PLAYER_NATIONALITY[clean]
    return None


def fmt_date(d):
    """格式化日期为 MM/DD/YY"""
    return f"{d.month:02d}/{d.day:02d}/{str(d.year)[2:]}"


def gen_score(is_home_fav=True, comp_type="league"):
    """生成合理比分"""
    if comp_type == "ucl":
        # 比分更接近
        if is_home_fav:
            sh = random.choice([2,1,2,3,1])
            sa = random.choice([0,1,1,0,2])
        else:
            sh = random.choice([0,1,1,0,2])
            sa = random.choice([2,1,2,3,1])
    elif comp_type == "nt":
        # 友谊赛比分较开放
        if is_home_fav:
            sh = random.choice([2,1,3,2,1])
            sa = random.choice([0,1,0,2,1])
        else:
            sh = random.choice([0,1,0,2,1])
            sa = random.choice([2,1,3,2,1])
    elif comp_type == "cup":
        # 杯赛可能加时/更胶着
        if is_home_fav:
            sh = random.choice([1,2,1,3,2])
            sa = random.choice([0,0,1,1,2])
        else:
            sh = random.choice([0,0,1,1,2])
            sa = random.choice([1,2,1,3,2])
    else:
        # 联赛正常分布
        if is_home_fav:
            sh = random.choice([1,2,2,3,1,2])
            sa = random.choice([0,0,1,1,2,1])
        else:
            sh = random.choice([0,1,1,2,0,1])
            sa = random.choice([1,2,2,3,1,2])

    # 小概率平局
    if random.random() < 0.22 and sh != sa:
        tie_score = random.choice([0,1,1,2])
        sh = sa = tie_score
    # 小概率爆冷
    if random.random() < 0.08 and not is_home_fav:
        sh, sa = sa, sh

    return sh, sa


def gen_player_stats(comp_type):
    """生成单场球员个人数据"""
    goal_prob = 0.30 if comp_type == "league" else (0.35 if comp_type == "ucl" else 0.25)
    assist_prob = 0.18 if comp_type == "league" else (0.20 if comp_type == "ucl" else 0.20)

    goals = 1 if random.random() < goal_prob else (random.randint(1, 3) if random.random() < 0.06 else 0)
    assists = 1 if random.random() < assist_prob else (random.randint(1, 2) if random.random() < 0.04 else 0)
    rating = round(random.uniform(6.0, 8.8), 1)

    # 如果进球或助攻，评分偏高
    if goals > 0 or assists > 0:
        rating = min(rating + random.uniform(0.3, 1.5), 9.5)
        rating = round(rating, 1)

    minutes = 90 if random.random() < 0.78 else (
        random.randint(60, 89) if random.random() < 0.15 else (
            random.randint(45, 59) if random.random() < 0.05 else 0
        )
    )

    return goals, assists, str(rating), minutes


def gen_matches_for_player(player_name, club, position=None):
    """为单个球员生成近10场比赛"""
    seed_val = hashlib.md5(f"{player_name}{club}2026WC".encode()).hexdigest()
    rng = random.Random(seed_val)

    ci = get_club_info(club)
    club_base = re.sub(r'\s*\(.*?\)', '', club).strip()
    matches = []

    def add_match(match_date, home_team, away_team, score_str, league_name, tag, comp_type):
        """添加一场比赛"""
        nonlocal matches
        is_home_club = (home_team == club or ci["league"] in home_team)
        g, a, r, m = gen_player_stats(comp_type)
        temp = rng.randint(14, 33)
        weather_cond = rng.choice(["晴", "多云", "阴", "晴间多云"])
        # 清理球队名称（去掉括号内容）用于直播搜索
        home_clean = re.sub(r'\s*\(.*?\)\s*', '', home_team).strip()
        away_clean = re.sub(r'\s*\(.*?\)\s*', '', away_team).strip()
        keyword = home_clean + ' vs ' + away_clean
        # 有直播的赛事类型
        live_comps = ["欧冠", "英超", "西甲", "德甲", "意甲", "法甲", "国家队", "世界杯", "足总杯", "国王杯", "德国杯", "意大利杯", "法国杯"]
        has_live = any(comp in league_name for comp in live_comps)
        matches.append({
            "date": fmt_date(match_date),
            "home": home_team,
            "away": away_team,
            "score": score_str,
            "goals": g,
            "assists": a,
            "rating": r,
            "minutes": m,
            "league": league_name,
            "leagueCss": tag,
            "weather": {"text": f"{temp}°C {weather_cond}"},
            "hasLive": has_live,
            "liveKeyword": keyword
        })

    schedule = ci.get("schedule", [])
    opponents_key = None
    league_code = ci.get("code", "DEF")

    # 找到对手列表的key
    for key in ["opponents_" + league_code.lower(), "opponents_epl", "opponents_lal",
                 "opponents_bl1", "opponents_sea", "opponents_fr1", "opponents_por",
                 "opponents_ned", "opponents_bel", "opponents_sco", "opponents_tur",
                 "opponents_sad", "opponents_bra", "opponents_mex", "opponents_arg",
                 "opponents_rus", "opponents_mls"]:
        if key in ci:
            opponents_key = key
            break

    opps = list(ci[opponents_key]) if opponents_key else []
    rng.shuffle(opps)

    # ---- 1. 联赛比赛（从赛程中取）----
    match_idx = 0
    for sched_code, match_date in schedule:
        if match_idx >= len(opps):
            match_idx = 0
            rng.shuffle(opps)
        opponent = opps[match_idx % len(opps)]
        is_home = rng.random() > 0.38  # 62% 主场
        home_team = club if is_home else opponent
        away_team = opponent if is_home else club
        sh, sa = gen_score(is_home, "league")
        add_match(match_date, home_team, away_team, f"{sh}-{sa}",
                  ci["league"], ci["tag"], "league")
        match_idx += 1

    # ---- 2. 欧冠比赛（基于硬编码晋级路线）----
    if ci.get("ucl"):
        # 确定该俱乐部欧冠最深晋级阶段
        progress = UCL_PROGRESS.get(club) or UCL_PROGRESS.get(club_base) or "ro16"

        # 用于在该俱乐部各轮次间分配不同日期
        ucl_date_idx = rng.randint(0, 3)

        # --- 1/8决赛（3月4-12日，4个比赛日）---
        ro16_opp = UCL_RO16_OPPONENTS.get(club) or UCL_RO16_OPPONENTS.get(club_base)
        if ro16_opp and len(matches) < 20:
            is_home = rng.random() > 0.45
            ht = club if is_home else ro16_opp
            at = ro16_opp if is_home else club
            # 1/8决赛：晋级的队伍获胜
            ro16_date = UCL_RO16_2ND[ucl_date_idx % len(UCL_RO16_2ND)]
            if progress in ("qf", "sf", "final"):
                sh, sa = (2, 1) if is_home else (1, 2)  # 晋级方胜
            else:
                sh, sa = (0, 1) if is_home else (1, 0)  # 被淘汰
            add_match(ro16_date, ht, at, f"{sh}-{sa}", "欧冠1/8决赛", "ucl-tag", "ucl")

        # --- 1/4决赛（4月8-16日，仅八强及以后）---
        if progress in ("qf", "sf", "final") and len(matches) < 20:
            qf_info = UCL_QF_FIXTURES.get(club) or UCL_QF_FIXTURES.get(club_base)
            if qf_info:
                qf_opp, qf_won_home = qf_info[0], qf_info[1]
                qf_date = UCL_QF[ucl_date_idx % len(UCL_QF)]
                # 根据是否晋级确定比分
                if progress in ("sf", "final"):
                    # 该队晋级了半决赛 → 1/4决赛胜出
                    sh, sa = (3, 1) if qf_won_home else (1, 3)
                else:
                    # 止步1/4决赛 → 输了
                    sh, sa = (1, 2) if qf_won_home else (2, 1)
                ht = club if qf_won_home else qf_opp
                at = qf_opp if qf_won_home else club
                add_match(qf_date, ht, at, f"{sh}-{sa}", "欧冠1/4决赛", "ucl-tag", "ucl")

        # --- 半决赛（4月29日-5月7日，仅四强）---
        if progress in ("sf", "final") and len(matches) < 20:
            sf_info = UCL_SF_FIXTURES.get(club) or UCL_SF_FIXTURES.get(club_base)
            if sf_info:
                sf_opp, sf_won_home = sf_info[0], sf_info[1]
                sf_date = UCL_SF[ucl_date_idx % len(UCL_SF)]
                if progress == "final":
                    # 该队进决赛 → 半决赛胜出
                    sh, sa = (2, 0) if sf_won_home else (0, 2)
                else:
                    # 止步半决赛 → 输了
                    sh, sa = (0, 1) if sf_won_home else (1, 0)
                ht = club if sf_won_home else sf_opp
                at = sf_opp if sf_won_home else club
                add_match(sf_date, ht, at, f"{sh}-{sa}", "欧冠半决赛", "ucl-tag", "ucl")

        # --- 决赛（仅巴黎圣日耳曼 和 阿森纳）---
        if progress == "final" and len(matches) < 20:
            if club == UCL_FINAL_HOME or club == UCL_FINAL_AWAY or club_base == re.sub(r'\s*\(.*?\)\s*', '', UCL_FINAL_HOME).strip() or club_base == re.sub(r'\s*\(.*?\)\s*', '', UCL_FINAL_AWAY).strip():
                add_match(
                    UCL_FINAL,
                    UCL_FINAL_HOME, UCL_FINAL_AWAY, UCL_FINAL_SCORE,
                    "欧冠决赛", "ucl-tag", "ucl"
                )

    # ---- 3. 国内杯赛决赛 ----
    cup_final = ci.get("cup_final")
    cup_name = ci.get("cup_name")
    if cup_final and cup_name:
        opp_cup = rng.choice(opps[:5]) if opps else "未知对手"
        sh, sa = gen_score(True, "cup")
        add_match(cup_final, club, opp_cup, f"{sh}-{sa}", cup_name + "决赛", "cup-tag", "cup")

    # ---- 4. 国家队热身赛 ----
    nationality = get_nationality(player_name)
    nt_display = NT_DISPLAY_NAMES.get(nationality, nationality or "国家队")
    if nationality and nationality in NT_OPPONENTS:
        nt_list = NT_OPPONENTS[nationality]
        nt_idx = 0
        for fri_date, _ in NT_FRIENDLIES:
            if nt_idx >= len(nt_list):
                break
            opp_nt = nt_list[nt_idx]
            if isinstance(opp_nt, tuple):
                opp_nt_name = opp_nt[0]
            elif isinstance(opp_nt, dict):
                opp_nt_name = opp_nt.get("name", "对手")
            else:
                opp_nt_name = str(opp_nt)
            is_home_nt = rng.random() > 0.40
            ht_nt = nt_display if is_home_nt else opp_nt_name
            at_nt = opp_nt_name if is_home_nt else nt_display
            sh, sa = gen_score(is_home_nt, "nt")
            add_match(fri_date, ht_nt, at_nt, f"{sh}-{sa}", "国家队友谊赛", "nt-tag", "nt")
            nt_idx += 1

    # ---- 排序：按日期倒序（最近的在前） ----
    matches.sort(key=lambda m: m["date"], reverse=True)
    # 不限制场次，输出2026年3月至今的所有比赛

    return matches


# ============================================================
# 主程序：读取球员列表 → 生成数据 → 输出JS文件
# 数据源：miniprogram/teamSquads.js（10队）+ 2026wc.html（32队额外）
# ============================================================

# 1. 从 miniprogram/teamSquads.js 读取10支常规球队球员
with open(r'C:\Users\Luojun\WorkBuddy\Claw\miniprogram\data\teamSquads.js', 'r', encoding='utf-8') as f:
    content = f.read()

players_mini = re.findall(r'\{name:"(.*?)",\s*club:"(.*?)"', content)
players_dict = {name: club for name, club in players_mini}

# 2. 从 2026wc.html 读取另外32支球队球员（补充）
HTML_PATH = r'C:\Users\Luojun\WorkBuddy\Claw\2026wc.html'
with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html_content = f.read()

extra_teams = [
    "南非","捷克","波黑","加拿大","卡塔尔","瑞士","苏格兰","海地","澳大利亚","土耳其",
    "巴拉圭","厄瓜多尔","哥伦比亚","新西兰","伊朗","沙特阿拉伯","伊拉克","乌兹别克斯坦",
    "约旦","塞内加尔","埃及","阿尔及利亚","突尼斯","科特迪瓦","加纳","佛得角",
    "刚果民主共和国","奥地利","挪威","瑞典","巴拿马","库拉索"
]

# 找各球队的起止位置（精确边界）
html_team_positions = []
for team in extra_teams:
    pattern = f'"{team}": {{"group":'
    idx = html_content.find(pattern)
    if idx == -1:
        pattern = f'"{team}":{{"group":'
        idx = html_content.find(pattern)
    if idx != -1:
        html_team_positions.append((idx, team))

html_team_positions.sort()

for i, (start_pos, team) in enumerate(html_team_positions):
    end_pos = html_team_positions[i+1][0] if i+1 < len(html_team_positions) else start_pos + 3000
    block = html_content[start_pos:end_pos]
    team_players = re.findall(r'"name":"([^"]+)","club":"([^"]+)"', block)
    for name, club in team_players:
        if name not in players_dict:
            players_dict[name] = club

print(f"miniprogram 球员: {len(players_mini)}")
print(f"HTML额外球队球员: {len(players_dict) - len(players_mini)}")
print(f"总球员数: {len(players_dict)}")

players = list(players_dict.items())

player_matches = {}
for name, club in players:
    player_matches[name] = gen_matches_for_player(name, club)

print(f"\n✅ 生成完成：{len(player_matches)} 位球员的比赛数据")

# 统计信息
total_matches = sum(len(m) for m in player_matches.values())
avg_matches = total_matches / len(player_matches) if player_matches else 0
print(f"   总比赛记录：{total_matches}")
print(f"   平均每球员：{avg_matches:.1f} 场")

# 展示几个样本
sample_names = ["梅西⭐(C)", "C罗", "姆巴佩 ⭐", "哈里·凯恩", "罗德里", "维尼修斯", "穆西亚拉"]
for name in sample_names:
    if name in player_matches:
        ms = player_matches[name]
        print(f"\n=== {name} ({len(ms)}场) ===")
        for m in ms:
            print(f'  {m["date"]:>8s} | {m["home"]} vs {m["away"]:<16s} [{m["score"]}] '
                  f'{m["league"]:<14s} G:{m["goals"]} A:{m["assists"]} R:{m["rating"]} {m["minutes"]}\'')
        print()

# 输出 JS 文件
js_data = {}
for name, matches in player_matches.items():
    js_data[name] = matches

js_content = "// data/playerMatches.js\n"
js_content += "// 球员近10场比赛数据（基于2026世界杯前真实足球赛历预生成）\n"
js_content += "// 包含：联赛收官轮 + 欧冠淘汰赛 + 国内杯赛决赛 + 国家队热身赛\n"
js_content += "// 生成时间：自动\n\n"
js_content += "const playerMatches = "
js_content += json.dumps(js_data, ensure_ascii=False, indent=2)
js_content += ";\n\nmodule.exports = { playerMatches };\n"

output_path = r'C:\Users\Luojun\WorkBuddy\Claw\miniprogram\data\playerMatches.js'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(js_content)

file_size_kb = len(js_content.encode('utf-8')) / 1024
print(f"\n💾 已保存到: {output_path}")
print(f"   文件大小: {file_size_kb:.1f} KB")

# 同时输出根目录HTML版本（浏览器格式，var声明）
html_js_content = "// playerMatches.js (HTML网页版)\n"
html_js_content += "// 球员近10场比赛数据（基于2026世界杯前真实足球赛历预生成）\n"
html_js_content += "var playerMatches = "
html_js_content += json.dumps(js_data, ensure_ascii=False, indent=2)
html_js_content += ";\n"

html_output_path = r'C:\Users\Luojun\WorkBuddy\Claw\playerMatches.js'
with open(html_output_path, 'w', encoding='utf-8') as f:
    f.write(html_js_content)

html_file_size_kb = len(html_js_content.encode('utf-8')) / 1024
print(f"💾 已保存到: {html_output_path}")
print(f"   文件大小: {html_file_size_kb:.1f} KB")
print(f"\n✅ 共生成 {len(player_matches)} 名球员的比赛数据")
