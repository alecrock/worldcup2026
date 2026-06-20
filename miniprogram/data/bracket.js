// data/bracket.js
// 淘汰赛晋级路线图数据（从上到下，从左到右）
// 每一轮包含 matchSlots，每个 slot 对应一个比赛位置
const bracketData = {
  rounds: [
    {
      title: "1/32决赛",
      short: "R32",
      matches: [
        { code: "M73", home: "A组第2", away: "B组第2" },
        { code: "M74", home: "E组第1", away: "最佳第三1" },
        { code: "M75", home: "F组第1", away: "C组第2" },
        { code: "M76", home: "C组第1", away: "F组第2" },
        { code: "M77", home: "I组第1", away: "最佳第三2" },
        { code: "M78", home: "E组第2", away: "I组第2" },
        { code: "M79", home: "A组第1", away: "最佳第三3" },
        { code: "M80", home: "L组第1", away: "最佳第三4" },
        { code: "M81", home: "D组第1", away: "最佳第三5" },
        { code: "M82", home: "G组第1", away: "最佳第三6" },
        { code: "M83", home: "K组第2", away: "L组第2" },
        { code: "M84", home: "H组第1", away: "J组第2" },
        { code: "M85", home: "B组第1", away: "最佳第三7" },
        { code: "M86", home: "J组第1", away: "H组第2" },
        { code: "M87", home: "K组第1", away: "最佳第三8" },
        { code: "M88", home: "D组第2", away: "G组第2" }
      ]
    },
    {
      title: "1/16决赛",
      short: "R16",
      matches: [
        { code: "M89", home: "M74胜", away: "M77胜" },
        { code: "M90", home: "M73胜", away: "M75胜" },
        { code: "M91", home: "M76胜", away: "M78胜" },
        { code: "M92", home: "M79胜", away: "M80胜" },
        { code: "M93", home: "M83胜", away: "M84胜" },
        { code: "M94", home: "M81胜", away: "M82胜" },
        { code: "M95", home: "M86胜", away: "M88胜" },
        { code: "M96", home: "M85胜", away: "M87胜" }
      ]
    },
    {
      title: "1/4决赛",
      short: "QF",
      matches: [
        { code: "M97", home: "M89胜", away: "M90胜" },
        { code: "M98", home: "M93胜", away: "M94胜" },
        { code: "M99", home: "M91胜", away: "M92胜" },
        { code: "M100", home: "M95胜", away: "M96胜" }
      ]
    },
    {
      title: "半决赛",
      short: "SF",
      matches: [
        { code: "M101", home: "M97胜", away: "M98胜" },
        { code: "M102", home: "M99胜", away: "M100胜" }
      ]
    },
    {
      title: "季军赛",
      short: "3rd",
      matches: [
        { code: "M103", home: "M101负", away: "M102负" }
      ]
    },
    {
      title: "★决赛★",
      short: "Final",
      matches: [
        { code: "M104", home: "M101胜", away: "M102胜" }
      ]
    }
  ]
};

module.exports = { bracketData };
