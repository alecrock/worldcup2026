// pages/group/group.js
const { groupMatches } = require('../../data/groupMatches.js');
const { venueCoords } = require('../../data/venueCoords.js');
const { streamingPlatforms } = require('../../data/streamingPlatforms.js');

Page({
  data: {
    groups: ['全部', 'A组', 'B组', 'C组', 'D组', 'E组', 'F组', 'G组', 'H组', 'I组', 'J组', 'K组', 'L组'],
    activeGroup: '全部',
    filteredMatches: [],
    allMatches: [],
    // 直播弹窗
    showLiveModal: false,
    liveMatchInfo: '',
    streamingPlatforms: streamingPlatforms
  },

  onLoad() {
    // 为每场比赛附加场地坐标
    const matchesWithCoord = groupMatches.map(m => {
      const coord = venueCoords[m.venue];
      return {
        ...m,
        venueLat: coord ? coord.lat : 0,
        venueLng: coord ? coord.lng : 0,
        hasCoord: !!coord
      };
    });
    this.setData({ allMatches: matchesWithCoord });
    this.filterMatches();
  },

  onGroupTap(e) {
    const group = e.currentTarget.dataset.group;
    this.setData({ activeGroup: group });
    this.filterMatches();
  },

  filterMatches() {
    const { allMatches, activeGroup } = this.data;
    if (activeGroup === '全部') {
      this.setData({ filteredMatches: allMatches });
    } else {
      const filtered = allMatches.filter(m => m.group === activeGroup);
      this.setData({ filteredMatches: filtered });
    }
  },

  // 点击球场 → 打开地图
  onVenueTap(e) {
    const { lat, lng, name } = e.currentTarget.dataset;
    if (!lat) {
      wx.showToast({ title: '暂无该场地坐标', icon: 'none' });
      return;
    }
    wx.openLocation({
      latitude: lat,
      longitude: lng,
      name: name,
      scale: 14
    });
  },

  // 点击"看直播" → 显示直播平台弹窗
  onLiveTap(e) {
    const { home, away, date } = e.currentTarget.dataset;
    this.setData({
      showLiveModal: true,
      liveMatchInfo: `${date} ${home} VS ${away}`
    });
  },

  closeLiveModal() {
    this.setData({ showLiveModal: false });
  },

  // 点击平台 → 跳转小程序或复制搜索关键词（支持场次级URL）
  onPlatformTap(e) {
    const platform = e.currentTarget.dataset.platform;
    const { liveMatchInfo } = this.data;
    const homeAwayMatch = liveMatchInfo.replace(/.*(\S+)\s+VS\s+(\S+)/, '$1 vs $2');
    const keyword = `${homeAwayMatch} 2026世界杯`;
    const fullKeyword = `${keyword} ${platform.keyword || ''}`;

    // 咪咕特殊处理：优先尝试唤起APP或打开场次详情页
    if (platform.id === 'migu') {
      // 构建场次级URL
      const matchUrl = platform.matchUrl ? (platform.matchUrl + encodeURIComponent(keyword)) : null;
      const fallbackUrl = platform.webUrl || 'https://www.migu.cn/sports/football/';

      // 尝试跳转咪咕小程序（带比赛关键词）
      if (platform.miniprogram) {
        wx.navigateToMiniProgram({
          appId: platform.miniprogram.appId,
          path: platform.miniprogram.path,
          extraData: { keyword: keyword },
          fail() {
            // 小程序跳转失败，复制场次搜索链接
            const urlToCopy = matchUrl || fallbackUrl;
            wx.showModal({
              title: '咪咕体育',
              content: '请复制以下链接在浏览器中打开，或直接打开咪咕体育APP搜索',
              confirmText: '复制链接',
              success(res) {
                if (res.confirm) {
                  wx.setClipboardData({ data: urlToCopy });
                }
              }
            });
          }
        });
      } else {
        // 无小程序，直接复制场次URL
        wx.setClipboardData({
          data: matchUrl || fallbackUrl,
          success() {
            wx.showToast({ title: '已复制场次链接', icon: 'success' });
          }
        });
      }
      this.setData({ showLiveModal: false });
      return;
    }

    // 其他平台：有searchUrl则构建完整搜索链接
    let copyData = fullKeyword;
    if (platform.id !== 'cctv5' && platform.searchUrl) {
      copyData = platform.searchUrl + encodeURIComponent(keyword);
    }

    // 优先尝试跳转微信小程序
    if (platform.miniprogram) {
      wx.navigateToMiniProgram({
        appId: platform.miniprogram.appId,
        path: platform.miniprogram.path,
        extraData: { keyword: fullKeyword },
        fail() {
          wx.setClipboardData({
            data: copyData,
            success() {
              wx.showToast({ title: '已复制，去' + platform.shortName + '搜索', icon: 'none', duration: 2500 });
            }
          });
        }
      });
    } else {
      wx.setClipboardData({
        data: copyData,
        success() {
          wx.showToast({ title: platform.searchUrl ? '已复制搜索链接' : '已复制搜索关键词', icon: 'success' });
        }
      });
    }
    this.setData({ showLiveModal: false });
  },

  // 一键复制直播链接（备用）
  onCopyAll(e) {
    const { liveMatchInfo } = this.data;
    const text = `${liveMatchInfo}\n\n推荐平台：\n央视频 | 咪咕视频 | 抖音体育 | 腾讯体育`;
    wx.setClipboardData({
      data: text,
      success() {
        wx.showToast({ title: '已复制比赛信息', icon: 'success' });
      }
    });
    this.setData({ showLiveModal: false });
  },

  // 跳转到球队阵容（分包页面）
  goToSquad() {
    wx.navigateTo({
      url: '/packageSquad/pages/squad/squad'
    });
  }

});
