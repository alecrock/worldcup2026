Page({
  data: {
    liked: false
  },

  onLoad() {
    // 检查是否已经点赞过
    const liked = wx.getStorageSync('worldcup_liked')
    if (liked) {
      this.setData({ liked: true })
    }
  },

  onLike() {
    const liked = !this.data.liked
    this.setData({ liked })
    wx.setStorageSync('worldcup_liked', liked)
    
    if (liked) {
      wx.showToast({
        title: '感谢点赞！',
        icon: 'success'
      })
    }
  },

  goToContent(e) {
    if (!this.data.liked) {
      wx.showToast({
        title: '请先点赞',
        icon: 'none'
      })
      return
    }
    
    const tab = e.currentTarget.dataset.tab
    wx.navigateTo({
      url: `/pages/content/content?tab=${tab}`
    })
  }
})
