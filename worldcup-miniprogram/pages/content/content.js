// 国旗映射
const FLAGS = {
  "墨西哥":"🇲🇽","南非":"🇿🇦","韩国":"🇰🇷","加拿大":"🇨🇦","波黑":"🇧🇦",
  "美国":"🇺🇸","巴拉圭":"🇵🇾","澳大利亚":"🇦🇺","土耳其":"🇹🇷","卡塔尔":"🇶🇦",
  "瑞士":"🇨🇭","巴西":"🇧🇷","摩洛哥":"🇲🇦","海地":"🇭🇹","苏格兰":"🏴󠁧󠁢󠁳󠁣󠁴󠁿",
  "科特迪瓦":"🇨🇮","厄瓜多尔":"🇪🇨","德国":"🇩🇪","库拉索":"🇨🇼","瑞典":"🇸🇪",
  "突尼斯":"🇹🇳","荷兰":"🇳🇱","日本":"🇯🇵","西班牙":"🇪🇸","佛得角":"🇨🇻",
  "比利时":"🇧🇪","埃及":"🇪🇬","沙特阿拉伯":"🇸🇦","乌拉圭":"🇺🇾","伊朗":"🇮🇷",
  "新西兰":"🇳🇿","法国":"🇫🇷","塞内加尔":"🇸🇳","伊拉克":"🇮🇶","挪威":"🇳🇴",
  "阿根廷":"🇦🇷","阿尔及利亚":"🇩🇿","奥地利":"🇦🇹","约旦":"🇯🇴","英格兰":"🏴󠁧󠁢󠁥󠁮󠁧󠁿",
  "克罗地亚":"🇭🇷","加纳":"🇬🇭","巴拿马":"🇵🇦","乌兹别克斯坦":"🇺🇿","哥伦比亚":"🇨🇴",
  "葡萄牙":"🇵🇹","刚果民主共和国":"🇨🇩","捷克":"🇨🇿"
};

// 小组赛数据（含已完成比赛比分）
const groupMatches = [
  {date:"6月11日 凌晨1:00", group:"A组", home:"墨西哥", away:"南非", venue:"墨西哥城 Estadio Azteca", score:"2-1"},
  {date:"6月11日 上午10:00", group:"A组", home:"韩国", away:"捷克", venue:"瓜达拉哈拉 Estadio Akron", score:"3-0"},
  {date:"6月12日 凌晨3:00", group:"B组", home:"加拿大", away:"波黑", venue:"多伦多 BMO Field", score:"1-1"},
  {date:"6月12日 上午9:00", group:"D组", home:"美国", away:"巴拉圭", venue:"洛杉矶 SoFi Stadium", score:"2-0"},
  {date:"6月12日 下午12:00", group:"D组", home:"澳大利亚", away:"土耳其", venue:"温哥华 BC Place", score:"1-2"},
  {date:"6月13日 凌晨3:00", group:"B组", home:"卡塔尔", away:"瑞士", venue:"圣克拉拉 Levi's Stadium", score:"0-2"},
  {date:"6月13日 上午6:00", group:"C组", home:"巴西", away:"摩洛哥", venue:"纽约 MetLife Stadium", score:"1-1"},
  {date:"6月13日 上午9:00", group:"C组", home:"海地", away:"苏格兰", venue:"马萨诸塞 Gillette Stadium", score:"0-3"},
  {date:"6月14日 上午7:00", group:"E组", home:"科特迪瓦", away:"厄瓜多尔", venue:"费城 Lincoln Financial Field", score:"1-1"},
  {date:"6月14日 上午9:00", group:"E组", home:"德国", away:"库拉索", venue:"休斯敦 NRG Stadium", score:"5-0"},
  {date:"6月14日 上午10:00", group:"F组", home:"瑞典", away:"突尼斯", venue:"蒙特雷 Estadio BBVA", score:"2-0"},
  {date:"6月14日 下午12:00", group:"F组", home:"荷兰", away:"日本", venue:"达拉斯 AT&T Stadium", score:"2-1"},
  {date:"6月15日 上午0:00", group:"H组", home:"西班牙", away:"佛得角", venue:"亚特兰大 Mercedes-Benz Stadium", score:"3-0"},
  {date:"6月15日 凌晨3:00", group:"G组", home:"比利时", away:"埃及", venue:"西雅图 Lumen Field", score:"1-0"},
  {date:"6月15日 上午6:00", group:"H组", home:"沙特阿拉伯", away:"乌拉圭", venue:"迈阿密 Hard Rock Stadium", score:"0-2"},
  {date:"6月15日 上午9:00", group:"G组", home:"伊朗", away:"新西兰", venue:"洛杉矶 SoFi Stadium", score:"2-1"},
  {date:"6月16日 凌晨3:00", group:"I组", home:"法国", away:"塞内加尔", venue:"纽约 MetLife Stadium", score:"3-1"},
  {date:"6月16日 上午6:00", group:"I组", home:"伊拉克", away:"挪威", venue:"马萨诸塞 Gillette Stadium", score:"1-4"},
  {date:"6月16日 上午9:00", group:"J组", home:"阿根廷", away:"阿尔及利亚", venue:"堪萨斯城 Arrowhead Stadium", score:"3-0"},
  {date:"6月16日 下午12:00", group:"J组", home:"奥地利", away:"约旦", venue:"圣克拉拉 Levi's Stadium", score:"3-1"},
  {date:"6月17日 凌晨4:00", group:"L组", home:"英格兰", away:"克罗地亚", venue:"达拉斯 AT&T Stadium", score:"4-2"},
  {date:"6月17日 上午7:00", group:"L组", home:"加纳", away:"巴拿马", venue:"多伦多 BMO Field", score:"1-0"},
  {date:"6月17日 上午10:00", group:"K组", home:"乌兹别克斯坦", away:"哥伦比亚", venue:"墨西哥城 Estadio Azteca", score:"1-3"},
  {date:"6月17日 上午11:00", group:"K组", home:"葡萄牙", away:"刚果民主共和国", venue:"休斯敦 NRG Stadium", score:"1-1"},
  {date:"6月19日 上午0:00", group:"A组", home:"捷克", away:"南非", venue:"亚特兰大 Mercedes-Benz Stadium", score:"1-2"},
  {date:"6月19日 凌晨3:00", group:"B组", home:"瑞士", away:"波黑", venue:"洛杉矶 SoFi Stadium", score:"2-0"},
  {date:"6月19日 上午6:00", group:"B组", home:"加拿大", away:"卡塔尔", venue:"温哥华 BC Place", score:"6-0"},
  {date:"6月19日 上午9:00", group:"A组", home:"墨西哥", away:"韩国", venue:"瓜达拉哈拉 Estadio Akron", score:"1-2"},
  {date:"6月20日 上午0:00", group:"D组", home:"土耳其", away:"巴拉圭", venue:"圣克拉拉 Levi's Stadium"},
  {date:"6月20日 上午3:00", group:"D组", home:"美国", away:"澳大利亚", venue:"西雅图 Lumen Field"},
  {date:"6月20日 上午6:00", group:"C组", home:"苏格兰", away:"摩洛哥", venue:"马萨诸塞 Gillette Stadium"},
  {date:"6月20日 上午9:00", group:"C组", home:"巴西", away:"海地", venue:"费城 Lincoln Financial Field"},
  {date:"6月21日 上午0:00", group:"F组", home:"突尼斯", away:"日本", venue:"蒙特雷 Estadio BBVA"},
  {date:"6月21日 下午1:00", group:"F组", home:"荷兰", away:"瑞典", venue:"休斯敦 NRG Stadium"},
  {date:"6月21日 下午4:00", group:"E组", home:"德国", away:"科特迪瓦", venue:"多伦多 BMO Field"},
  {date:"6月21日 上午8:00", group:"E组", home:"厄瓜多尔", away:"库拉索", venue:"堪萨斯城 Arrowhead Stadium"},
  {date:"6月22日 上午0:00", group:"H组", home:"西班牙", away:"沙特阿拉伯", venue:"亚特兰大 Mercedes-Benz Stadium"},
  {date:"6月22日 凌晨3:00", group:"G组", home:"比利时", away:"伊朗", venue:"洛杉矶 SoFi Stadium"},
  {date:"6月22日 上午6:00", group:"H组", home:"乌拉圭", away:"佛得角", venue:"迈阿密 Hard Rock Stadium"},
  {date:"6月22日 上午9:00", group:"G组", home:"新西兰", away:"埃及", venue:"温哥华 BC Place"},
  {date:"6月23日 上午5:00", group:"I组", home:"法国", away:"伊拉克", venue:"费城 Lincoln Financial Field"},
  {date:"6月23日 上午8:00", group:"I组", home:"挪威", away:"塞内加尔", venue:"纽约 MetLife Stadium"},
  {date:"6月23日 上午11:00", group:"J组", home:"约旦", away:"阿尔及利亚", venue:"圣克拉拉 Levi's Stadium"},
  {date:"6月23日 下午1:00", group:"J组", home:"阿根廷", away:"奥地利", venue:"达拉斯 AT&T Stadium"},
  {date:"6月24日 上午4:00", group:"L组", home:"英格兰", away:"加纳", venue:"马萨诸塞 Gillette Stadium"},
  {date:"6月24日 上午7:00", group:"L组", home:"巴拿马", away:"克罗地亚", venue:"多伦多 BMO Field"},
  {date:"6月24日 上午10:00", group:"K组", home:"哥伦比亚", away:"刚果民主共和国", venue:"瓜达拉哈拉 Estadio Akron"},
  {date:"6月24日 下午1:00", group:"K组", home:"葡萄牙", away:"乌兹别克斯坦", venue:"休斯敦 NRG Stadium"},
  {date:"6月25日 凌晨3:00", group:"B组", home:"瑞士", away:"加拿大", venue:"温哥华 BC Place"},
  {date:"6月25日 凌晨3:00", group:"B组", home:"波黑", away:"卡塔尔", venue:"西雅图 Lumen Field"},
  {date:"6月25日 上午6:00", group:"C组", home:"苏格兰", away:"巴西", venue:"迈阿密 Hard Rock Stadium"},
  {date:"6月25日 上午6:00", group:"C组", home:"摩洛哥", away:"海地", venue:"亚特兰大 Mercedes-Benz Stadium"},
  {date:"6月25日 上午9:00", group:"A组", home:"捷克", away:"墨西哥", venue:"墨西哥城 Estadio Azteca"},
  {date:"6月25日 上午9:00", group:"A组", home:"南非", away:"韩国", venue:"蒙特雷 Estadio BBVA"},
  {date:"6月26日 上午4:00", group:"E组", home:"库拉索", away:"科特迪瓦", venue:"费城 Lincoln Financial Field"},
  {date:"6月26日 上午4:00", group:"E组", home:"厄瓜多尔", away:"德国", venue:"纽约 MetLife Stadium"},
  {date:"6月26日 上午7:00", group:"F组", home:"日本", away:"瑞典", venue:"达拉斯 AT&T Stadium"},
  {date:"6月26日 上午7:00", group:"F组", home:"突尼斯", away:"荷兰", venue:"堪萨斯城 Arrowhead Stadium"},
  {date:"6月26日 上午10:00", group:"D组", home:"土耳其", away:"美国", venue:"洛杉矶 SoFi Stadium"},
  {date:"6月26日 上午10:00", group:"D组", home:"巴拉圭", away:"澳大利亚", venue:"圣克拉拉 Levi's Stadium"},
  {date:"6月27日 凌晨3:00", group:"I组", home:"挪威", away:"法国", venue:"马萨诸塞 Gillette Stadium"},
  {date:"6月27日 凌晨3:00", group:"I组", home:"塞内加尔", away:"伊拉克", venue:"多伦多 BMO Field"},
  {date:"6月27日 上午8:00", group:"H组", home:"佛得角", away:"沙特阿拉伯", venue:"休斯敦 NRG Stadium"},
  {date:"6月27日 上午8:00", group:"H组", home:"乌拉圭", away:"西班牙", venue:"瓜达拉哈拉 Estadio Akron"},
  {date:"6月27日 上午11:00", group:"G组", home:"埃及", away:"伊朗", venue:"西雅图 Lumen Field"},
  {date:"6月27日 上午11:00", group:"G组", home:"新西兰", away:"比利时", venue:"温哥华 BC Place"},
  {date:"6月28日 上午5:00", group:"L组", home:"巴拿马", away:"英格兰", venue:"纽约 MetLife Stadium"},
  {date:"6月28日 上午5:00", group:"L组", home:"克罗地亚", away:"加纳", venue:"费城 Lincoln Financial Field"},
  {date:"6月28日 上午7:30", group:"K组", home:"哥伦比亚", away:"葡萄牙", venue:"迈阿密 Hard Rock Stadium"},
  {date:"6月28日 上午7:30", group:"K组", home:"刚果民主共和国", away:"乌兹别克斯坦", venue:"亚特兰大 Mercedes-Benz Stadium"},
  {date:"6月28日 上午10:00", group:"J组", home:"阿尔及利亚", away:"奥地利", venue:"堪萨斯城 Arrowhead Stadium"},
  {date:"6月28日 上午10:00", group:"J组", home:"约旦", away:"阿根廷", venue:"达拉斯 AT&T Stadium"}
];

// 淘汰赛数据
const knockoutMatches = [
  {
    round:"1/32决赛",
    matches:[
      {code:"M73", date:"6月29日 上午2:00", home:"A组第2名", away:"B组第2名"},
      {code:"M74", date:"6月30日 上午1:00", home:"E组第1名", away:"最佳第三名1"},
      {code:"M75", date:"6月30日 上午3:00", home:"F组第1名", away:"C组第2名"},
      {code:"M76", date:"6月30日 上午6:00", home:"C组第1名", away:"F组第2名"},
      {code:"M77", date:"7月1日 上午1:00", home:"I组第1名", away:"最佳第三名2"},
      {code:"M78", date:"7月1日 上午3:00", home:"E组第2名", away:"I组第2名"},
      {code:"M79", date:"7月1日 上午6:00", home:"A组第1名", away:"最佳第三名3"},
      {code:"M80", date:"7月2日 上午0:00", home:"L组第1名", away:"最佳第三名4"},
      {code:"M81", date:"7月2日 上午3:00", home:"D组第1名", away:"最佳第三名5"},
      {code:"M82", date:"7月2日 上午6:00", home:"G组第1名", away:"最佳第三名6"},
      {code:"M83", date:"7月3日 上午0:00", home:"K组第2名", away:"L组第2名"},
      {code:"M84", date:"7月3日 上午3:00", home:"H组第1名", away:"J组第2名"},
      {code:"M85", date:"7月3日 上午5:00", home:"B组第1名", away:"最佳第三名7"},
      {code:"M86", date:"7月4日 上午2:00", home:"J组第1名", away:"H组第2名"},
      {code:"M87", date:"7月4日 上午3:00", home:"K组第1名", away:"最佳第三名8"},
      {code:"M88", date:"7月4日 上午5:00", home:"D组第2名", away:"G组第2名"}
    ]
  },
  {
    round:"1/16决赛",
    matches:[
      {code:"M89", date:"7月5日 上午3:00", home:"M74胜者", away:"M77胜者"},
      {code:"M90", date:"7月5日 上午6:00", home:"M73胜者", away:"M75胜者"},
      {code:"M91", date:"7月6日 上午3:00", home:"M76胜者", away:"M78胜者"},
      {code:"M92", date:"7月6日 上午6:00", home:"M79胜者", away:"M80胜者"},
      {code:"M93", date:"7月7日 上午3:00", home:"M83胜者", away:"M84胜者"},
      {code:"M94", date:"7月7日 上午6:00", home:"M81胜者", away:"M82胜者"},
      {code:"M95", date:"7月8日 上午3:00", home:"M86胜者", away:"M88胜者"},
      {code:"M96", date:"7月8日 上午6:00", home:"M85胜者", away:"M87胜者"}
    ]
  },
  {
    round:"1/4决赛",
    matches:[
      {code:"M97", date:"7月10日 上午9:00", home:"M89胜者", away:"M90胜者"},
      {code:"M98", date:"7月11日 上午8:00", home:"M93胜者", away:"M94胜者"},
      {code:"M99", date:"7月12日 上午7:00", home:"M91胜者", away:"M92胜者"},
      {code:"M100", date:"7月12日 上午10:00", home:"M95胜者", away:"M96胜者"}
    ]
  },
  {
    round:"半决赛",
    matches:[
      {code:"M101", date:"7月15日 上午9:00", home:"M97胜者", away:"M98胜者"},
      {code:"M102", date:"7月16日 上午8:00", home:"M99胜者", away:"M100胜者"}
    ]
  },
  {
    round:"三四名决赛",
    matches:[
      {code:"M103", date:"7月19日 上午8:00", home:"M101负者", away:"M102负者"}
    ]
  },
  {
    round:"★冠军决赛★",
    matches:[
      {code:"M104", date:"7月20日 上午8:00", home:"M101胜者", away:"M102胜者", isFinal:true}
    ]
  }
];

// 球队阵容数据（简化版，省略部分球员）
const teamSquads = {
  "墨西哥": { group:"A组", players: {"GK":["奥乔亚","科塔","马拉贡"], "DF":["阿劳霍","加利亚多","蒙特斯"], "MF":["埃雷拉","瓜尔达多","罗莫"], "FW":["希梅内斯","洛萨诺","安图尼亚"]}},
  "南非": { group:"A组", players: {"GK":["威廉姆斯","库内","莫莱法"], "DF":["莫迪巴","马塞科","西亚洛巴"], "MF":["齐韦","马梅拉","马戈希"], "FW":["莫蒂巴","拉西亚","多萨尔"]}},
  "韩国": { group:"A组", players: {"GK":["金承奎","赵贤祐","宋范根"], "DF":["金玟哉","金英权","薛英佑"], "MF":["李刚仁","黄仁范","孙兴慜"], "FW":["黄喜灿","曹圭成","吴贤揆"]}},
  "波黑": { group:"A组", players: {"GK":["谢希奇","皮里奇","卡利奇"], "DF":["科拉希纳茨","比查克契奇"], "MF":["皮亚尼奇","梅贾什维利"], "FW":["哲科","伊比里契奇","德米罗维奇"]}},
  "加拿大": { group:"B组", players: {"GK":["博扬","圣克莱尔","克雷波"], "DF":["戴维斯","维多利亚","米勒"], "MF":["埃斯塔奎奥","哈奇森","欧斯塔基奥"], "FW":["大卫","拉林","布坎南"]}},
  "卡塔尔": { group:"B组", players: {"GK":["巴里","哈桑","希卜里"], "DF":["哈桑","胡希","萨利姆"], "MF":["哈特姆","布迪亚夫","阿菲夫"], "FW":["莫埃兹·阿里","阿拉丁","哈立德"]}},
  "瑞士": { group:"B组", players: {"GK":["索默","科贝尔","奥姆林"], "DF":["阿坎吉","沙尔","罗德里格斯"], "MF":["扎卡","弗罗伊勒","沙奇里"], "FW":["塞费罗维奇","恩博洛","巴尔加斯"]}},
  "巴西": { group:"C组", players: {"GK":["阿利松","埃德森","韦弗顿"], "DF":["马尔基尼奥斯","蒂亚戈·席尔瓦","米利唐"], "MF":["卡塞米罗","布鲁诺·吉马良斯","帕奎塔"], "FW":["维尼修斯","内马尔","理查利森"]}},
  "摩洛哥": { group:"C组", players: {"GK":["布努","穆尼尔","卡约维"], "DF":["阿什拉夫","赛斯","阿格尔德"], "MF":["阿姆拉巴特","奥纳西","阿马拉"], "FW":["齐耶赫","恩内斯里","布法尔"]}},
  "美国": { group:"D组", players: {"GK":["特纳","霍瓦特","斯蒂芬"], "DF":["亚当斯","理查兹","齐默尔曼"], "MF":["麦肯尼","穆萨","蒂莱曼斯"], "FW":["普利西奇","维阿","费雷拉"]}},
  "阿根廷": { group:"J组", players: {"GK":["马丁内斯","鲁利","阿尔马尼"], "DF":["奥塔门迪","罗梅罗","莫利纳"], "MF":["德保罗","帕雷德斯","麦卡利斯特"], "FW":["梅西","阿尔瓦雷斯","劳塔罗"]}},
  "法国": { group:"I组", players: {"GK":["迈尼昂","阿雷奥拉","桑巴"], "DF":["萨利巴","于帕梅卡诺","孔德"], "MF":["楚阿梅尼","卡马文加","格列兹曼"], "FW":["姆巴佩","登贝莱","图拉姆"]}},
  "西班牙": { group:"H组", players: {"GK":["乌奈·西蒙","拉亚","凯帕"], "DF":["拉波尔特","罗德里","纳乔"], "MF":["佩德里","加维","鲁伊斯"], "FW":["莫拉塔","亚马尔","威廉姆斯"]}},
  "英格兰": { group:"L组", players: {"GK":["皮克福德","拉姆斯代尔","亨德森"], "DF":["沃克","斯通斯","马奎尔"], "MF":["贝林厄姆","赖斯","福登"], "FW":["凯恩","拉什福德","格里利什"]}}
};

// 计算积分榜（根据已完成比赛的比分）
function calculateStandings() {
  const groups = [...new Set(groupMatches.map(m => m.group))].sort();
  const result = {};
  groups.forEach(g => { result[g] = []; });
  
  groupMatches.forEach(m => {
    if (!m.score) return;
    const g = m.group;
    if (!result[g]) result[g] = [];
    
    const parts = m.score.split('-');
    const homeGoals = parseInt(parts[0]) || 0;
    const awayGoals = parseInt(parts[1]) || 0;
    
    [m.home, m.away].forEach((team, i) => {
      let entry = result[g].find(e => e.team === team);
      if (!entry) {
        entry = { team, played:0, won:0, drawn:0, lost:0, goalsFor:0, goalsAgainst:0, points:0 };
        result[g].push(entry);
      }
      entry.played++;
      entry.goalsFor += (i===0 ? homeGoals : awayGoals);
      entry.goalsAgainst += (i===0 ? awayGoals : homeGoals);
      if (homeGoals > awayGoals) {
        if (i===0) { entry.won++; entry.points+=3; }
        else { entry.lost++; }
      } else if (homeGoals < awayGoals) {
        if (i===0) { entry.lost++; }
        else { entry.won++; entry.points+=3; }
      } else {
        entry.drawn++;
        entry.points+=1;
      }
    });
  });
  
  groups.forEach(g => {
    if (result[g]) {
      result[g].forEach(e => { e.gd = e.goalsFor - e.goalsAgainst; });
      result[g].sort((a,b) => b.points - a.points || b.gd - a.gd || b.goalsFor - a.goalsFor);
    }
  });
  return result;
}

// 射手榜数据（更新至2026年6月20日）
const topScorers = [
  { name:'利昂内尔·梅西', team:'阿根廷', goals:3 },
  { name:'乔纳森·大卫', team:'加拿大', goals:3 },
  { name:'基利安·姆巴佩', team:'法国', goals:2 },
  { name:'埃尔林·哈兰德', team:'挪威', goals:2 },
  { name:'凯·哈弗茨', team:'德国', goals:2 },
  { name:'哈里·凯恩', team:'英格兰', goals:2 },
  { name:'法雷斯·巴洛贡', team:'美国', goals:2 },
  { name:'雅辛·阿亚里', team:'瑞典', goals:2 },
  { name:'克里斯·贾斯特', team:'新西兰', goals:2 },
  { name:'维尼修斯·儒尼奥尔', team:'巴西', goals:1 }
];

Page({
  data: {
    currentTab: 'group',
    currentGroup: 'all',
    groups: [],
    filteredMatches: [],
    knockoutRounds: [],
    countries: [],
    currentCountry: '',
    currentSquad: null,
    // 排行榜相关数据
    standingSubTab: 'standings',
    standingGroups: [],
    standingGroupFilter: 'all',
    filteredStandings: [],
    topScorersList: []
  },

  onLoad(options) {
    const tab = options.tab || 'group';
    
    // 处理小组赛数据
    const groups = [...new Set(groupMatches.map(m => m.group))].sort();
    const filteredMatches = groupMatches.map(m => ({
      ...m,
      homeFlag: FLAGS[m.home] || '',
      awayFlag: FLAGS[m.away] || ''
    }));
    
    // 处理淘汰赛数据
    const knockoutRounds = knockoutMatches.map(r => ({
      ...r,
      isFinal: r.round.includes('冠军')
    }));
    
    // 处理球队阵容数据
    const countries = Object.keys(teamSquads).map(name => ({
      name,
      flag: FLAGS[name] || ''
    }));
    
    // 处理排行榜数据
    const standingGroups = ['全部', ...groups];
    const standingsData = calculateStandings();
    const filteredStandings = standingGroups.slice(1).map(g => ({
      group: g,
      teams: standingsData[g] || []
    }));
    const topScorersList = topScorers.map((s, i) => ({ ...s, rank: i+1 }));
    
    this.setData({
      currentTab: tab,
      groups,
      filteredMatches,
      knockoutRounds,
      countries,
      currentCountry: Object.keys(teamSquads)[0],
      standingGroups,
      filteredStandings,
      topScorersList
    });
    
    this.loadSquad(Object.keys(teamSquads)[0]);
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({ currentTab: tab });
    if (tab === 'standings') {
      this.renderStandings();
    }
  },

  filterGroup(e) {
    const group = e.currentTarget.dataset.group;
    const filteredMatches = group === 'all' 
      ? groupMatches.map(m => ({...m, homeFlag: FLAGS[m.home] || '', awayFlag: FLAGS[m.away] || ''}))
      : groupMatches.filter(m => m.group === group).map(m => ({...m, homeFlag: FLAGS[m.home] || '', awayFlag: FLAGS[m.away] || ''}));
    
    this.setData({
      currentGroup: group,
      filteredMatches
    });
  },

  selectCountry(e) {
    const country = e.currentTarget.dataset.country;
    this.setData({ currentCountry: country });
    this.loadSquad(country);
  },

  loadSquad(country) {
    const data = teamSquads[country];
    if (!data) return;
    
    const posMap = {"GK":"🧤 门将","DF":"🛡️ 后卫","MF":"⚽ 中场","FW":"🎯 前锋"};
    const positions = Object.entries(data.players).map(([pos, players], idx) => ({
      pos: posMap[pos] || pos,
      icon: posMap[pos] ? posMap[pos].split(' ')[0] : '',
      players: players.map((name, i) => ({ num: i+1, name }))
    }));
    
    this.setData({
      currentSquad: {
        group: data.group,
        flag: FLAGS[country] || '',
        positions
      }
    });
  },

  // 排行榜子标签切换
  switchStandingSubTab(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({ standingSubTab: tab });
  },

  // 积分榜按小组筛选
  filterStandingGroup(e) {
    const group = e.currentTarget.dataset.group;
    const standingGroups = this.data.standingGroups;
    let filteredStandings;
    if (group === '全部') {
      const standingsData = calculateStandings();
      filteredStandings = standingGroups.slice(1).map(g => ({
        group: g,
        teams: standingsData[g] || []
      }));
    } else {
      const standingsData = calculateStandings();
      filteredStandings = [{ group: group, teams: standingsData[group] || [] }];
    }
    this.setData({
      standingGroupFilter: group,
      filteredStandings
    });
  },

  // 渲染积分榜
  renderStandings() {
    const standingGroups = this.data.standingGroups;
    const standingsData = calculateStandings();
    const filteredStandings = standingGroups.slice(1).map(g => ({
      group: g,
      teams: standingsData[g] || []
    }));
    this.setData({ filteredStandings });
  }
})
