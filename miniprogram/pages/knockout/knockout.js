// pages/knockout/knockout.js
const { knockoutMatches } = require('../../data/knockoutMatches.js');
const { venueCoords } = require('../../data/venueCoords.js');
const { bracketData } = require('../../data/bracket.js');
const { streamingPlatforms } = require('../../data/streamingPlatforms.js');

Page({
  data: {
    knockoutMatches: [],
    bracketData: bracketData,
    showBracket: false,
    streamingPlatforms: streamingPlatforms,
    showLiveModal: false,
    liveMatchInfo: ''
  },

  onLoad() {
    const matches = knockoutMatches.map(round => ({
      ...round,
      matches: round.matches.map(m => {
        const coord = venueCoords[m.venue];
        return {
          ...m,
          venueLat: coord ? coord.lat : 0,
          venueLng: coord ? coord.lng : 0,
          hasCoord: !!coord
        };
      })
    }));
    this.setData({ knockoutMatches: matches });
  },

  toggleBracket() {
    this.setData({ showBracket: !this.data.showBracket });
  },

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

  onPlatformTap(e) {
    const platform = e.currentTarget.dataset.platform;
    const { liveMatchInfo } = this.data;
    const homeAwayMatch = liveMatchInfo.replace(/.*(\S+)\s+VS\s+(\S+)/, '$1 vs $2');
    const keyword = `${homeAwayMatch} 2026世界杯`;
    const fullKeyword = `${keyword} ${platform.keyword || ''}`;

    // 咪咕特殊处理：优先尝试唤起APP或打开场次详情页
    if (platform.id === 'migu') {
      const matchUrl = platform.matchUrl ? (platform.matchUrl + encodeURIComponent(keyword)) : null;
      const fallbackUrl = platform.webUrl || 'https://www.migu.cn/sports/football/';

      if (platform.miniprogram) {
        wx.navigateToMiniProgram({
          appId: platform.miniprogram.appId,
          path: platform.miniprogram.path,
          extraData: { keyword: keyword },
          fail() {
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
        wx.setClipboardData({
          data: matchUrl || fallbackUrl,
          success() { wx.showToast({ title: '已复制场次链接', icon: 'success' }); }
        });
      }
      this.setData({ showLiveModal: false });
      return;
    }

    // 其他平台
    let copyData = fullKeyword;
    if (platform.id !== 'cctv5' && platform.searchUrl) {
      copyData = platform.searchUrl + encodeURIComponent(keyword);
    }

    if (platform.miniprogram) {
      wx.navigateToMiniProgram({
        appId: platform.miniprogram.appId,
        path: platform.miniprogram.path,
        extraData: { keyword: fullKeyword },
        fail() {
          wx.setClipboardData({
            data: copyData,
            success() { wx.showToast({ title: '已复制，去' + platform.shortName + '搜索', icon: 'none', duration: 2500 }); }
          });
        }
      });
    } else {
      wx.setClipboardData({
        data: copyData,
        success() { wx.showToast({ title: platform.searchUrl ? '已复制搜索链接' : '已复制搜索关键词', icon: 'success' }); }
      });
    }
    this.setData({ showLiveModal: false });
  },

  onCopyAll() {
    const { liveMatchInfo } = this.data;
    const text = `${liveMatchInfo}\n\n推荐平台：\n央视频 | 咪咕视频 | 抖音体育 | 腾讯体育`;
    wx.setClipboardData({
      data: text,
      success() {
        wx.showToast({ title: '已复制比赛信息', icon: 'success' });
      }
    });
    this.setData({ showLiveModal: false });
  }
});
