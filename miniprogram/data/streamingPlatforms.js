// data/streamingPlatforms.js
// 2026世界杯直播平台数据（含APP跳转方案）
// 2026-05-30 更新：咪咕增加场次级跳转能力
//
// 微信小程序内通过 wx.navigateToMiniProgram 跳转其他小程序（咪咕、腾讯体育等）
// 也可通过 web URL 在内置浏览器打开
const streamingPlatforms = [
  {
    id: "yangshipin",
    name: "央视频",
    shortName: "央视频",
    icon: "📺",
    color: "#e53e3e",
    desc: "央视官方·全赛事免费直播",
    // 跳转微信小程序（央视频小程序）
    miniprogram: { appId: "wxb4d5da4a2a0c1b2e", path: "pages/index/index" },
    // Web备用 + 场次搜索
    webUrl: "https://sports.cctv.com/",
    searchUrl: "https://app.cctv.com/special/m/yhsearch/?q=",
    // 关键词（用于复制搜索）
    keyword: "央视频 世界杯直播"
  },
  {
    id: "migu",
    name: "咪咕体育",
    shortName: "咪咕",
    icon: "📱",
    color: "#667eea",
    desc: "央视分授权·多视角观赛·直达场次",
    // 跳转微信小程序（咪咕视频/咪咕体育小程序）
    miniprogram: { appId: "wx5e5a3d3c03e4f1a2", path: "pages/index/index" },
    // Web：首页 + 搜索 + 场次详情页
    webUrl: "https://www.migu.cn/sports/football/live/",
    searchUrl: "https://www.migu.cn/search?keyword=",
    matchUrl: "https://sports.migu.cn/v2/detail/?q=",
    // URL Scheme 唤起原生APP（手机端）
    deepLink: "migusportsscheme://",
    schemes: ["migusportsscheme://search?keyword=", "miguvideo://search?keyword=", "mgvideo://search?keyword=", "migusportsscheme://home"],
    keyword: "咪咕体育 世界杯"
  },
  {
    id: "douyin",
    name: "抖音体育",
    shortName: "抖音",
    icon: "🎵",
    color: "#00f2ea",
    desc: "央视分授权·弹幕互动",
    miniprogram: null,
    webUrl: "https://www.douyin.com/",
    searchUrl: "https://www.douyin.com/search/",
    keyword: "抖音 世界杯直播"
  },
  {
    id: "tencent",
    name: "腾讯体育",
    shortName: "腾讯",
    icon: "🐧",
    color: "#07c160",
    desc: "FIFA独家数字平台",
    miniprogram: { appId: "wxb3d5a0e0d0c0b0a0", path: "pages/index/index" },
    webUrl: "https://sports.qq.com/",
    searchUrl: "https://sports.qq.com/kbsweb/search.htm?query=",
    keyword: "腾讯体育 世界杯"
  },
  {
    id: "cctv5",
    name: "CCTV5 体育频道",
    shortName: "CCTV5",
    icon: "🏆",
    color: "#e53e3e",
    desc: "电视频道·央视五套",
    miniprogram: null,
    webUrl: "https://tv.cctv.com/live/cctv5/",
    keyword: "CCTV5 世界杯直播"
  },
  {
    id: "xiaohongshu",
    name: "小红书",
    shortName: "小红书",
    icon: "📕",
    color: "#ff2442",
    desc: "赛事直播·精彩集锦",
    miniprogram: { appId: "wx7a998bea3e5c1c1e", path: "pages/index/index" },
    webUrl: "https://www.xiaohongshu.com/search_result?keyword=",
    keyword: "小红书 世界杯直播"
  }
];

module.exports = { streamingPlatforms };
