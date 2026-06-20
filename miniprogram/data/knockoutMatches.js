// data/knockoutMatches.js
// 淘汰赛场地映射
const knockoutVenues = {
  "M73":"洛杉矶 SoFi Stadium", "M74":"费城 Lincoln Financial Field", "M75":"达拉斯 AT&T Stadium",
  "M76":"纽约 MetLife Stadium", "M77":"亚特兰大 Mercedes-Benz Stadium", "M78":"西雅图 Lumen Field",
  "M79":"墨西哥城 Estadio Azteca", "M80":"休斯敦 NRG Stadium", "M81":"迈阿密 Hard Rock Stadium",
  "M82":"洛杉矶 SoFi Stadium", "M83":"圣克拉拉 Levi's Stadium", "M84":"多伦多 BMO Field",
  "M85":"温哥华 BC Place", "M86":"瓜达拉哈拉 Estadio Akron", "M87":"马萨诸塞 Gillette Stadium",
  "M88":"堪萨斯城 Arrowhead Stadium",
  "M89":"达拉斯 AT&T Stadium", "M90":"纽约 MetLife Stadium", "M91":"洛杉矶 SoFi Stadium",
  "M92":"休斯敦 NRG Stadium", "M93":"亚特兰大 Mercedes-Benz Stadium", "M94":"西雅图 Lumen Field",
  "M95":"迈阿密 Hard Rock Stadium", "M96":"墨西哥城 Estadio Azteca",
  "M97":"达拉斯 AT&T Stadium", "M98":"纽约 MetLife Stadium", "M99":"洛杉矶 SoFi Stadium",
  "M100":"休斯敦 NRG Stadium", "M101":"达拉斯 AT&T Stadium", "M102":"纽约 MetLife Stadium",
  "M103":"迈阿密 Hard Rock Stadium", "M104":"纽约 MetLife Stadium"
};

// 淘汰赛数据
const knockoutMatches = [
  {
    round:"1/32决赛",
    matches:[
      {code:"M73", date:"6月29日 上午2:00", home:"A组第2名", away:"B组第2名", venue:"洛杉矶 SoFi Stadium"},
      {code:"M74", date:"6月30日 上午1:00", home:"E组第1名", away:"最佳第三名1", venue:"费城 Lincoln Financial Field"},
      {code:"M75", date:"6月30日 上午3:00", home:"F组第1名", away:"C组第2名", venue:"达拉斯 AT&T Stadium"},
      {code:"M76", date:"6月30日 上午6:00", home:"C组第1名", away:"F组第2名", venue:"纽约 MetLife Stadium"},
      {code:"M77", date:"7月1日 上午1:00", home:"I组第1名", away:"最佳第三名2", venue:"亚特兰大 Mercedes-Benz Stadium"},
      {code:"M78", date:"7月1日 上午3:00", home:"E组第2名", away:"I组第2名", venue:"西雅图 Lumen Field"},
      {code:"M79", date:"7月1日 上午6:00", home:"A组第1名", away:"最佳第三名3", venue:"墨西哥城 Estadio Azteca"},
      {code:"M80", date:"7月2日 上午0:00", home:"L组第1名", away:"最佳第三名4", venue:"休斯敦 NRG Stadium"},
      {code:"M81", date:"7月2日 上午3:00", home:"D组第1名", away:"最佳第三名5", venue:"迈阿密 Hard Rock Stadium"},
      {code:"M82", date:"7月2日 上午6:00", home:"G组第1名", away:"最佳第三名6", venue:"洛杉矶 SoFi Stadium"},
      {code:"M83", date:"7月3日 上午0:00", home:"K组第2名", away:"L组第2名", venue:"圣克拉拉 Levi's Stadium"},
      {code:"M84", date:"7月3日 上午3:00", home:"H组第1名", away:"J组第2名", venue:"多伦多 BMO Field"},
      {code:"M85", date:"7月3日 上午5:00", home:"B组第1名", away:"最佳第三名7", venue:"温哥华 BC Place"},
      {code:"M86", date:"7月4日 上午2:00", home:"J组第1名", away:"H组第2名", venue:"瓜达拉哈拉 Estadio Akron"},
      {code:"M87", date:"7月4日 上午3:00", home:"K组第1名", away:"最佳第三名8", venue:"马萨诸塞 Gillette Stadium"},
      {code:"M88", date:"7月4日 上午5:00", home:"D组第2名", away:"G组第2名", venue:"堪萨斯城 Arrowhead Stadium"}
    ]
  },
  {
    round:"1/16决赛",
    matches:[
      {code:"M89", date:"7月5日 上午3:00", home:"M74胜者", away:"M77胜者", venue:"达拉斯 AT&T Stadium"},
      {code:"M90", date:"7月5日 上午6:00", home:"M73胜者", away:"M75胜者", venue:"纽约 MetLife Stadium"},
      {code:"M91", date:"7月6日 上午3:00", home:"M76胜者", away:"M78胜者", venue:"洛杉矶 SoFi Stadium"},
      {code:"M92", date:"7月6日 上午6:00", home:"M79胜者", away:"M80胜者", venue:"休斯敦 NRG Stadium"},
      {code:"M93", date:"7月7日 上午3:00", home:"M83胜者", away:"M84胜者", venue:"亚特兰大 Mercedes-Benz Stadium"},
      {code:"M94", date:"7月7日 上午6:00", home:"M81胜者", away:"M82胜者", venue:"西雅图 Lumen Field"},
      {code:"M95", date:"7月8日 上午3:00", home:"M86胜者", away:"M88胜者", venue:"迈阿密 Hard Rock Stadium"},
      {code:"M96", date:"7月8日 上午6:00", home:"M85胜者", away:"M87胜者", venue:"墨西哥城 Estadio Azteca"}
    ]
  },
  {
    round:"1/4决赛",
    matches:[
      {code:"M97", date:"7月10日 上午9:00", home:"M89胜者", away:"M90胜者", venue:"达拉斯 AT&T Stadium"},
      {code:"M98", date:"7月11日 上午8:00", home:"M93胜者", away:"M94胜者", venue:"纽约 MetLife Stadium"},
      {code:"M99", date:"7月12日 上午7:00", home:"M91胜者", away:"M92胜者", venue:"洛杉矶 SoFi Stadium"},
      {code:"M100", date:"7月12日 上午10:00", home:"M95胜者", away:"M96胜者", venue:"休斯敦 NRG Stadium"}
    ]
  },
  {
    round:"半决赛",
    matches:[
      {code:"M101", date:"7月15日 上午9:00", home:"M97胜者", away:"M98胜者", venue:"达拉斯 AT&T Stadium"},
      {code:"M102", date:"7月16日 上午8:00", home:"M99胜者", away:"M100胜者", venue:"纽约 MetLife Stadium"}
    ]
  },
  {
    round:"三四名决赛",
    matches:[
      {code:"M103", date:"7月19日 上午8:00", home:"M101负者", away:"M102负者", venue:"迈阿密 Hard Rock Stadium"}
    ]
  },
  {
    round:"★冠军决赛★",
    matches:[
      {code:"M104", date:"7月20日 上午8:00", home:"M101胜者", away:"M102胜者", venue:"纽约 MetLife Stadium", isFinal:true}
    ]
  }
];

module.exports = { knockoutVenues, knockoutMatches };
