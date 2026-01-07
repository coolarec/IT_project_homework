<template>
  <div class="p-6 space-y-6 bg-slate-50 min-h-screen">
    <!-- 顶部操作区 -->
    <el-card shadow="never" class="!rounded-2xl border-none shadow-sm">
      <div class="flex items-center justify-between">
        <div class="space-y-1">
          <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">
            <el-icon class="text-blue-500"><Document /></el-icon>
            榜单数据导入
          </h2>
          <p class="text-sm text-slate-400">支持解析标准 ACM 榜单 Excel，并自动计算奖项分布</p>
        </div>

        <div class="flex items-center gap-4">
          <el-upload action="" :auto-upload="false" :on-change="handleFile" :show-file-list="false">
            <el-button type="primary" size="large" plain class="!rounded-xl">
              <el-icon class="mr-2"><Upload /></el-icon> 选择榜单文件
            </el-button>
          </el-upload>

          <el-input
            v-model="contestName"
            placeholder="为这场比赛命名 (如: 2025 南京站)"
            class="w-72"
            size="large"
          >
            <template #prefix><el-icon><Flag /></el-icon></template>
          </el-input>

          <el-button
            type="success"
            size="large"
            class="!rounded-xl px-8"
            :disabled="!previewData.length || !contestName"
            @click="handleSave"
            :loading="saving"
          >
            确认并入库图数据库
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 预览表格区 -->
    <div v-if="previewData.length" class="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
      <el-table
        :data="previewData"
        height="calc(100vh - 240px)"
        stripe
        size="default"
        class="custom-table"
      >
        <!-- 排名 -->
        <el-table-column prop="rank" label="Rank" width="80" align="center" fixed />

        <!-- 奖牌 -->
        <el-table-column label="Medal" width="100" align="center" fixed>
          <template #default="{row}">
            <el-tag
              v-if="row.medal !== '打铁'"
              :class="getMedalClass(row.medal)"
              effect="dark"
              size="small"
              class="!border-none font-bold"
            >
              {{ row.medal }}
            </el-tag>
            <span v-else class="text-slate-300 text-xs">-</span>
          </template>
        </el-table-column>

        <!-- 队伍信息 -->
        <el-table-column prop="organization" label="学校 / 组织" width="200" show-overflow-tooltip>
          <template #default="{row}">
            <div class="font-semibold text-slate-700">{{ row.organization }}</div>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="队伍名称" min-width="200" show-overflow-tooltip>
          <template #default="{row}">
            <div class="text-slate-500">{{ row.name }}</div>
          </template>
        </el-table-column>

        <!-- 解题明细 -->
        <el-table-column label="Problem Matrix (AC / Attempts / Time)" min-width="400">
          <template #default="{row}">
            <div class="flex flex-wrap gap-1.5 py-2">
              <el-tooltip
                v-for="(v, k) in row.problems"
                :key="k"
                effect="dark"
                :content="`题目 ${k}: 第 ${v.attempts} 次提交通过`"
                placement="top"
              >
                <div
                  class="problem-tag"
                  :class="v.status === 'FB' ? 'is-fb' : 'is-ac'"
                >
                  <el-icon v-if="v.status === 'FB'" class="mr-0.5"><Zap /></el-icon>
                  <span class="font-black">{{ k }}</span>
                  <span class="opacity-60 ml-1 text-[10px]">{{ v.time }}'</span>
                </div>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>

        <!-- 统计 -->
        <el-table-column prop="score" label="Solved" width="90" align="center">
          <template #default="{row}">
            <span class="text-lg font-black text-blue-600">{{ row.score }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="penalty" label="Penalty" width="100" align="center">
          <template #default="{row}">
            <span class="text-xs font-mono text-slate-400">{{ row.penalty }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 空状态 -->
    <el-empty
      v-else
      description="暂无数据，请上传比赛榜单 Excel 预览"
      :image-size="200"
      class="bg-white rounded-2xl"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { previewAnalysisApi, saveAnalysisApi } from '#/api/neo4j';
import { Document, Upload, Flag, Lightning as Zap } from '@element-plus/icons-vue';
import { ElMessage,ElCard,ElTooltip,ElUpload,ElTable,ElTableColumn ,ElIcon,ElButton,ElInput,ElTag,ElEmpty } from 'element-plus';

const contestName = ref('');
const previewData = ref<any[]>([]);
const saving = ref(false);

const handleFile = async (file: any) => {
  if (!file || !file.raw) return;
  try {
    const data = await previewAnalysisApi(file.raw);
    previewData.value = data;
    ElMessage.success(`成功解析 ${data.length} 条参赛记录`);
  } catch (e) {
    ElMessage.error('解析失败，请检查文件格式');
  }
};

const handleSave = async () => {
  saving.value = true;
  try {
    await saveAnalysisApi(contestName.value, previewData.value);
    ElMessage.success('数据同步成功，可在看板中查看分析结果');
    previewData.value = [];
    contestName.value = '';
  } finally {
    saving.value = false;
  }
};

// 奖牌颜色逻辑
const getMedalClass = (medal: string) => {
  if (medal === '金') return 'medal-gold';
  if (medal === '银') return 'medal-silver';
  if (medal === '铜') return 'medal-bronze';
  return '';
};
</script>

<style scoped>
/* 奖牌自定义颜色 */
.medal-gold { background-color: #fbbf24 !important; color: #78350f !important; }
.medal-silver { background-color: #94a3b8 !important; color: #1e293b !important; }
.medal-bronze { background-color: #b45309 !important; color: #fff !important; }

/* 题目块样式 */
.problem-tag {
  @apply px-2 py-1 rounded text-xs flex items-center transition-all cursor-default;
  min-width: 48px;
  justify-content: center;
}

/* 普通过题 AC */
.is-ac {
  @apply bg-emerald-500 text-white shadow-sm;
}

/* 一血 FB - 深绿色带发光感 */
.is-fb {
  background-color: #064e3b !important; /* Emerald 900 */
  color: #fbbf24 !important; /* Gold text */
  box-shadow: 0 0 8px rgba(6, 78, 59, 0.4);
  @apply scale-105 z-10;
}

.custom-table :deep(.el-table__header) {
  @apply bg-slate-50 text-slate-600 font-bold uppercase text-[11px] tracking-wider;
}

.custom-table :deep(.el-table__row) {
  @apply transition-colors hover:bg-blue-50/30;
}

:deep(.el-input__wrapper) {
  @apply !rounded-xl;
}
</style>
