// pages/squad/squad.js
const { teamSquads } = require('../../data/teamSquads.js');
const { playerMatches } = require('../../packageSquad/data/playerMatches.js');

Page({
  data: {
    teamList: Object.keys(teamSquads),
    activeTeam: '',
    currentSquad: null,
    positionLabels: [
      { pos: 'GK', label: '门将 (GK)' },
      { pos: 'DF', label: '后卫 (DF)' },
      { pos: 'MF', label: '中场 (MF)' },
      { pos: 'FW', label: '前锋 (FW)' }
    ],
    showPlayerModal: false,
    playerModalName: '',
    playerModalClub: '',
    playerModalAvatar: '',
    playerModalLoading: false,
    playerModalMatches: []
  },

  onLoad() {
    if (this.data.teamList.length > 0) {
      this.setData({ activeTeam: this.data.teamList[0] });
      this.showTeam(this.data.teamList[0]);
    }
  },

  onTeamTap(e) {
    const team = e.currentTarget.dataset.team;
    this.setData({ activeTeam: team });
    this.showTeam(team);
  },

  showTeam(team) {
    const squad = teamSquads[team];
    this.setData({ currentSquad: squad });
  },

  // 点击球员 - 显示详情弹窗
  onPlayerTap(e) {
    const name = e.currentTarget.dataset.name;
    const club = e.currentTarget.dataset.club || '';

    this.setData({
      showPlayerModal: true,
      playerModalName: name,
      playerModalClub: club,
      playerModalAvatar: '',
      playerModalLoading: true,
      playerModalMatches: []
    });

    // 加载球员头像（零延迟字母头像）
    const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=667eea&color=fff&size=200&font-size=0.45&bold=true&rounded=true`;
    this.setData({ playerModalAvatar: avatarUrl });

    // 加载近期比赛（本地数据，零延迟）
    const matches = playerMatches[name] || [];
    this.setData({
      playerModalLoading: false,
      playerModalMatches: matches
    });
    console.log('[Player]', name, '| 头像已设置 | 比赛', matches.length, '场');

    // 后台静默尝试获取真实头像
    wx.request({
      url: `https://www.thesportsdb.com/api/v1/json/3/searchplayers.php?p=${encodeURIComponent(name)}`,
      timeout: 5000,
      success: (res) => {
        if (res.statusCode === 200 && res.data && res.data.player && res.data.player[0] && res.data.player[0].strThumb) {
          if (this.data.playerModalName === name) {
            const realUrl = res.data.player[0].strThumb.replace(/^http:\/\//i, 'https://');
            console.log('[Avatar] 真实头像:', realUrl);
            this.setData({ playerModalAvatar: realUrl });
          }
        }
      }
    });
  },

  onAvatarError() {
    const name = this.data.playerModalName;
    const fallbackUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&background=667eea&color=fff&size=128&font-size=0.4&bold=true`;
    this.setData({ playerModalAvatar: fallbackUrl });
  },

  closePlayerModal() {
    this.setData({ showPlayerModal: false });
  },

  preventBubble() {},

  forceHttps(url) {
    if (!url) return '';
    return url.replace(/^http:\/\//i, 'https://');
  },

  getCompTag(league) {
    if (!league) return { text: '联赛', css: 'club-tag' };
    const l = league.toLowerCase();
    if (l.indexOf('champions') >= 0 || l.indexOf('uefa champions') >= 0) return { text: '欧冠', css: 'ucl-tag' };
    if (l.indexOf('europa') >= 0 && l.indexOf('conference') < 0) return { text: '欧联', css: 'uel-tag' };
    if (l.indexOf('premier') >= 0 || l.indexOf('english') >= 0) return { text: '英超', css: 'league-tag' };
    if (l.indexOf('la liga') >= 0 || l.indexOf('spanish') >= 0) return { text: '西甲', css: 'league-tag' };
    if (l.indexOf('bundesliga') >= 0 || l.indexOf('german') >= 0) return { text: '德甲', css: 'league-tag' };
    if (l.indexOf('ligue 1') >= 0 || l.indexOf('french') >= 0) return { text: '法甲', css: 'league-tag' };
    if (l.indexOf('serie a') >= 0 || l.indexOf('italian') >= 0) return { text: '意甲', css: 'league-tag' };
    if (l.indexOf('world cup') >= 0) return { text: '世界杯', css: 'wc-tag' };
    if (l.indexOf('friendly') >= 0) return { text: '友谊赛', css: 'nt-tag' };
    return { text: '联赛', css: 'club-tag' };
  }
});
