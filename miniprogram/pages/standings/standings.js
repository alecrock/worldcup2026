// pages/standings/standings.js
const { groupMatches } = require('../../data/groupMatches.js');

// 计算积分榜
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
    
    [m.home, m.away].forEach((team, idx) => {
      let entry = result[g].find(e => e.team === team);
      if (!entry) {
        entry = { team, played:0, won:0, drawn:0, lost:0, goalsFor:0, goalsAgainst:0, points:0 };
        result[g].push(entry);
      }
      entry.played++;
      entry.goalsFor += (idx===0 ? homeGoals : awayGoals);
      entry.goalsAgainst += (idx===0 ? awayGoals : homeGoals);
      if (homeGoals > awayGoals) {
        if (idx===0) { entry.won++; entry.points+=3; }
        else { entry.lost++; }
      } else if (homeGoals < awayGoals) {
        if (idx===0) { entry.lost++; }
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

// 射手榜数据
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
    subTab: 'standings',
    groups: ['全部', 'A组', 'B组', 'C组', 'D组', 'E组', 'F组', 'G组', 'H组', 'I组', 'J组', 'K组', 'L组'],
    groupFilter: '全部',
    standingsData: [],
    topScorersList: []
  },

  onLoad() {
    this.loadData();
  },

  onShow() {
    this.loadData();
  },

  loadData() {
    const standingsData = calculateStandings();
    const groups = this.data.groups;
    const standingsList = groups.slice(1).map(g => ({
      group: g,
      teams: standingsData[g] || []
    }));
    
    const topScorersList = topScorers.map((s, i) => ({ ...s, rank: i+1 }));
    
    this.setData({
      standingsList,
      topScorersList
    });
  },

  switchSubTab(e) {
    const tab = e.currentTarget.dataset.tab;
    this.setData({ subTab: tab });
  },

  filterGroup(e) {
    const group = e.currentTarget.dataset.group;
    const standingsData = calculateStandings();
    
    let standingsList;
    if (group === '全部') {
      const groups = this.data.groups;
      standingsList = groups.slice(1).map(g => ({
        group: g,
        teams: standingsData[g] || []
      }));
    } else {
      standingsList = [{ group: group, teams: standingsData[group] || [] }];
    }
    
    this.setData({
      groupFilter: group,
      standingsList
    });
  }
});
