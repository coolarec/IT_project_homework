<template>
  <!-- 主背景改为浅灰色 -->
  <div class="p-6 min-h-screen bg-gray-50 text-slate-800">
    <!-- 顶部：比赛过滤器与全局操作 -->
    <div class="flex items-center justify-between mb-8 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
      <div class="flex items-center gap-6">
        <div class="flex items-center gap-2">
          <div class="w-2 h-6 bg-blue-600 rounded-full"></div>
          <h1 class="text-xl font-bold tracking-wider text-slate-800 uppercase">RANK ANALYISIS</h1>
        </div>

        <div class="flex items-center gap-3 ml-4">
          <span class="text-xs font-bold text-slate-500 uppercase">当前视野:</span>
          <el-select v-model="selectedContest" placeholder="全生涯总览 (Global)" clearable @change="handleRefresh"
            class="analysis-select" style="width: 280px">
            <el-option label="🌏 全生涯总览 (Aggregated)" value="" />
            <el-option v-for="name in contestList" :key="name" :label="name" :value="name" />
          </el-select>
        </div>
      </div>

      <div class="flex gap-3">
        <el-button type="primary" :loading="loading" @click="handleRefresh" round>
          <el-icon class="mr-1">
            <Refresh />
          </el-icon> 刷新分析数据
        </el-button>
      </div>
    </div>

    <!-- 第一排：题目画像与奖牌分析 -->
    <el-row :gutter="20" class="mb-6">
      <!-- 题目战术象限图 -->
      <el-col :span="16">
        <div class="bg-white p-6 rounded-2xl border border-slate-200 h-[520px] shadow-sm">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-sm font-bold text-slate-600 uppercase tracking-widest">赛题战术画像 (X: 尝试次数 / Y: 罚时)</h3>
            <el-tooltip content="气泡大小代表通过人数。左下角为签到题，右上角为压轴/陷阱题。" placement="top">
              <el-icon class="text-slate-400 cursor-help">
                <QuestionFilled />
              </el-icon>
            </el-tooltip>
          </div>
          <!-- 移除 h-full，改为固定高度防止溢出 -->
          <div ref="bubbleChartRef" class="w-full h-[420px]"></div>
        </div>
      </el-col>

      <!-- 奖牌构成 -->
      <el-col :span="8">
        <div class="bg-white p-6 rounded-2xl border border-slate-200 h-[520px] flex flex-col shadow-sm">
          <h3 class="text-sm font-bold text-slate-600 uppercase tracking-widest mb-6">奖牌分布明细</h3>
          <div ref="pieChartRef" class="flex-1"></div>
          <div class="mt-4 grid grid-cols-3 gap-2">
            <div v-for="item in medalSummary" :key="item.label"
              class="bg-slate-50 p-3 rounded-xl border border-slate-100 text-center">
              <div class="text-[10px] text-slate-400 uppercase font-bold">{{ item.label }}</div>
              <div class="text-lg font-black" :style="{ color: item.color }">{{ item.value }}</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 第二排：学校排行与选手协同 -->
    <el-row :gutter="20">
      <!-- 学校综合战力 -->
      <el-col :span="10">
        <div class="bg-white p-6 rounded-2xl border border-slate-200 h-[480px] shadow-sm">
          <h3 class="text-sm font-bold text-slate-600 uppercase tracking-widest mb-6">学校综合底蕴评分 (Top 15)</h3>
          <div ref="rankChartRef" class="w-full h-[380px]"></div>
        </div>
      </el-col>

      <!-- 黄金搭档协同分析 -->
      <el-col :span="14">
        <div class="bg-white p-6 rounded-2xl border border-slate-200 h-[480px] shadow-sm">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-sm font-bold text-slate-600 uppercase tracking-widest">选手组合协同效应 (Synergy)</h3>
            <span class="text-[10px] text-blue-600 bg-blue-50 px-2 py-1 rounded border border-blue-100">图数据库动态计算</span>
          </div>
          <el-table :data="synergyData" style="width: 100%" height="360" stripe>
            <el-table-column prop="pair" label="队员搭档" min-width="200">
              <template #default="{ row }">
                <span class="font-mono text-slate-700 font-bold">{{ row.pair }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="together_count" label="共同获奖" width="100" align="center" />
            <el-table-column label="协同稳定性" width="200">
              <template #default="{ row }">
                <el-progress :percentage="Math.min(row.together_count * 20, 100)"
                  :color="row.together_count > 3 ? '#10b981' : '#3b82f6'" :stroke-width="8"
                  :format="(p) => p >= 80 ? '极高' : '稳定'" />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import * as echarts from 'echarts';
import { Refresh, QuestionFilled } from '@element-plus/icons-vue';
import { getDashboardApi, getUploadedContestsApi } from '#/api/neo4j';
import { ElMessage, ElCol, ElRow, ElTooltip, ElTable, ElTableColumn, ElProgress, ElButton, ElSelect, ElOption, ElIcon } from 'element-plus';

// 页面状态
const loading = ref(false);
const selectedContest = ref('');
const contestList = ref<string[]>([]);
const synergyData = ref([]);
const medalSummary = ref<any[]>([]);

// 图表实例
const bubbleChartRef = ref<HTMLElement>();
const pieChartRef = ref<HTMLElement>();
const rankChartRef = ref<HTMLElement>();
let charts: echarts.ECharts[] = [];

/** 初始化加载：获取比赛列表并执行第一次分析 */
const initPage = async () => {
  try {
    const contests = await getUploadedContestsApi();
    contestList.value = contests;
    await handleRefresh();
  } catch (e) {
    ElMessage.error('无法连接到分析服务');
  }
};

/** 刷新数据逻辑 */
const handleRefresh = async () => {
  loading.value = true;
  try {
    const data = await getDashboardApi(selectedContest.value);
    synergyData.value = data.member_synergy || [];
    medalSummary.value = [
      {
        label: 'Gold',
        value: data.medal_pie.find((i: { label: string; value: number }) => i.label === '金')?.value || 0,
        color: '#d97706'
      },
      {
        label: 'Silver',
        value: data.medal_pie.find((i: { label: string; value: number }) => i.label === '银')?.value || 0,
        color: '#64748b'
      },
      {
        label: 'Bronze',
        value: data.medal_pie.find((i: { label: string; value: number }) => i.label === '铜')?.value || 0,
        color: '#92400e'
      },
    ];

    await nextTick();
    renderAllCharts(data);
  } finally {
    loading.value = false;
  }
};

/** 统一渲染入口 */
const renderAllCharts = (data: any) => {
  charts.forEach(c => c.dispose());
  charts = [];
  // 这里不再传 'dark' 参数，使用默认浅色主题
  if (bubbleChartRef.value) renderBubble(data.problem_profile);
  if (pieChartRef.value) renderPie(data.medal_pie);
  if (rankChartRef.value) renderRank(data.org_ranking);
};

// --- ECharts 配置函数 (针对浅色背景优化配色) ---

const renderBubble = (list: any[]) => {
  const chart = echarts.init(bubbleChartRef.value!);
  chart.setOption({
    tooltip: {
      formatter: (p: any) => `题目 ${p.data[2]}<br/>均尝试: ${p.data[0]}次<br/>平均罚时: ${p.data[1]}min`
    },
    grid: { top: '10%', left: '5%', right: '10%', bottom: '10%', containLabel: true },
    xAxis: {
      name: '尝试次数',
      nameTextStyle: { color: '#64748b' },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLine: { lineStyle: { color: '#cbd5e1' } }
    },
    yAxis: {
      name: '耗时',
      nameTextStyle: { color: '#64748b' },
      splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
      axisLine: { lineStyle: { color: '#cbd5e1' } }
    },
    series: [{
      type: 'scatter',
      data: list.map(i => [i.avg_attempts, i.avg_time, i.code, i.solve_count]),
      symbolSize: (val: any) => Math.min(val[3] * 2 + 10, 60),
      label: { show: true, formatter: '{@2}', color: '#fff', fontSize: 10, fontWeight: 'bold' },
      itemStyle: {
        color: new echarts.graphic.RadialGradient(0.4, 0.3, 1, [
          { offset: 0, color: '#60a5fa' },
          { offset: 1, color: '#2563eb' }
        ]),
        shadowBlur: 10,
        shadowColor: 'rgba(37, 99, 235, 0.2)'
      }
    }]
  });
  charts.push(chart);
};

const renderPie = (list: any[]) => {
  const chart = echarts.init(pieChartRef.value!);
  chart.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['55%', '75%'],
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      data: list.map(i => ({
        name: i.label,
        value: i.value,
        itemStyle: { color: i.label === '金' ? '#fbbf24' : (i.label === '银' ? '#94a3b8' : '#b45309') }
      }))
    }]
  });
  charts.push(chart);
};

const renderRank = (list: any[]) => {
  const chart = echarts.init(rankChartRef.value!);
  chart.setOption({
    grid: { top: '5%', left: '3%', right: '10%', bottom: '5%', containLabel: true },
    xAxis: { type: 'value', splitLine: { show: false }, axisLine: { show: false } },
    yAxis: {
      type: 'category',
      data: list.map(i => i.name).reverse(),
      axisLabel: { fontSize: 11, color: '#475569' },
      axisLine: { lineStyle: { color: '#cbd5e1' } }
    },
    series: [{
      type: 'bar',
      data: list.map(i => i.power_score).reverse(),
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
          { offset: 0, color: '#3b82f6' },
          { offset: 1, color: '#2dd4bf' }
        ]),
        borderRadius: 4
      },
      barWidth: 14
    }]
  });
  charts.push(chart);
};

const handleResize = () => charts.forEach(c => c.resize());

onMounted(() => {
  initPage();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  charts.forEach(c => c.dispose());
});
</script>

<style scoped>
/* 浅色模式下的 Select 适配 */
.analysis-select :deep(.el-input__wrapper) {
  background-color: #ffffff !important;
  box-shadow: 0 0 0 1px #e2e8f0 inset !important;
}

/* Table 样式优化 */
:deep(.el-table) {
  --el-table-header-bg-color: #f8fafc;
  --el-table-border-color: #f1f5f9;
}

:deep(.el-table th.el-table__cell) {
  color: #64748b;
  font-weight: 700;
}

/* 进度条轨道颜色 */
:deep(.el-progress-bar__outer) {
  background-color: #f1f5f9 !important;
}
</style>
