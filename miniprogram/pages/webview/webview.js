// pages/webview/webview.js
Page({
  data: {
    url: '',
    title: '直播'
  },

  onLoad(options) {
    const app = getApp();
    const url = app.globalData.webviewUrl || options.url || '';
    const title = app.globalData.webviewTitle || options.title || '直播';
    
    this.setData({ url, title });
    
    if (title) {
      wx.setNavigationBarTitle({ title });
    }
  }
});
