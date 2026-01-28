<template>
  <div class="p-6 min-h-screen" v-loading="loading">
    <!-- 1. 竞赛头部概览卡片 -->
    <el-card shadow="never" class="mb-6 rounded-xl border-none">
      <div class="flex justify-between items-start">
        <div class="space-y-2">
          <div class="flex items-center gap-3">
            <h1 class="text-2xl font-bold ">{{ contest?.title || '加载中...' }}</h1>
            <el-tag :type="contest?.is_public ? 'success' : 'warning'" effect="dark">
              {{ contest?.is_public ? '全体公开' : '指定小组' }}
            </el-tag>
          </div>
          <p class=" max-w-2xl text-sm">{{ contest?.description || '暂无比赛详细描述' }}</p>
          <div class="flex gap-6 mt-4 text-xs ">
            <span class="flex items-center gap-1">
              <el-icon>
                <Clock />
              </el-icon> 开始时间：{{ contest?.contest_start_time }}
            </span>
            <span class="flex items-center gap-1">
              <el-icon>
                <User />
              </el-icon> 创建者：{{ contest?.creator_name }}
            </span>
          </div>
        </div>
        <div class="flex gap-2">
          <el-button type="success" :icon="Plus" @click="openVpDialog('create')">
            添加题目占位
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 2. 题目矩阵管理表格 -->
    <el-card shadow="never" class="rounded-xl border-none">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="font-bold text-lg ">题目准备进度</span>
          <div class="flex gap-4 text-[12px] font-normal">
            <span class="flex items-center gap-1"><i class="matrix-dot bg-slate-200"></i> 未开始</span>
            <span class="flex items-center gap-1"><i class="matrix-dot bg-amber-400"></i> 进行中</span>
            <span class="flex items-center gap-1"><i class="matrix-dot bg-emerald-500"></i> 已完成</span>
          </div>
        </div>
      </template>

      <el-table :data="contest?.virtual_problems" style="width: 100%" border stripe>
        <el-table-column label="#" width="60" align="center">
          <template #default="{ $index }">
            {{ String.fromCharCode(65 + $index) }}
          </template>
        </el-table-column>
        <el-table-column label="题目名" width="120" align="center">

          <template #default="{ row }">

            <div class="flex flex-col items-center gap-1">
              <el-tag effect="dark" class="!border-none font-bold px-4" :color="row.color">
                {{ row.name || '?' }}
              </el-tag>
              <span class="text-[10px] ">排序: {{ row.order }}</span>
            </div>
          </template>
        </el-table-column>

        <!-- 虚拟描述 -->
        <el-table-column prop="description" label="出题方向及难度预期" min-width="160" />

        <el-table-column label="关联真实题目及准备进度" min-width="380">
          <template #default="{ row }">
            <div class="flex flex-col gap-2 py-1">
              <div class="flex items-center justify-between pr-4">
                <span v-if="row.is_bound"
                  class="text-sm font-bold text-blue-600 truncate max-w-[220px] cursor-pointer hover:underline"
                  @click="goProblemEditor(row.real_problem_id)">
                  {{ row.real_problem_title }}
                </span>
                <el-tag v-if="row.is_bound" size="small" type="success" plain class="scale-90">已绑定</el-tag>
              </div>

              <!-- 九个圆点进度条 -->
              <div class="flex gap-2 mt-1">
                <el-tooltip v-for="step in stepConfig" :key="step.key"
                  :content="`${step.label}: ${getStatusText(row[step.key])}`" placement="top">
                  <div
                    class="w-5 h-5 rounded-full border-2 border-white shadow-sm flex items-center justify-center transition-all duration-300"
                    :class="[
                      getStatusClass(row[step.key]),
                      row[step.key] === 1 ? 'animate-pulse' : ''
                    ]">
                    <el-icon v-if="row[step.key] === 2" :size="10" color="white">
                      <Check />
                    </el-icon>
                  </div>
                </el-tooltip>
              </div>
            </div>
          </template>
        </el-table-column>

        <!-- 操作区 -->
        <el-table-column label="管理操作" width="300" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleOpenBind(row)">
              {{ row.is_bound ? '更换题目' : '关联题目' }}
            </el-button>
            <el-button link type="primary" @click="openVpDialog('edit', row)">属性</el-button>
            <el-button v-if="row.is_bound" link type="success" @click="openDrawer('testcase', row)">测试点</el-button>
            <el-button v-if="row.is_bound" link type="info" @click="openDrawer('solution', row)">题解</el-button>
            <el-button link type="danger" @click="handleDeleteVp(row.id)">移除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 弹窗1：新增/编辑虚拟题目属性 -->
    <el-dialog v-if="vpDialog.visible" v-model="vpDialog.visible"
      :title="vpDialog.type === 'create' ? '新增题目占位' : '修改占位属性'" width="440px" append-to-body destroy-on-close>
      <el-form :model="vpDialog.form" label-position="top" class="px-2">
        <el-form-item label="题目名" required>
          <el-input v-model="vpDialog.form.name" placeholder="请输入题号，如: A" />
        </el-form-item>
        <el-form-item label="出题方向及难度预期" required>
          <el-input v-model="vpDialog.form.description" placeholder="请输入题目名称" />
        </el-form-item>
        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="列表排序 (从小到大)">
            <el-input-number v-model="vpDialog.form.order" :min="0" class="!w-full" />
          </el-form-item>
          <el-form-item label="标识背景色">
            <el-color-picker v-model="vpDialog.form.color" class="!w-full" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <div class="px-2 pb-2">
          <el-button @click="vpDialog.visible = false">取消</el-button>
          <el-button type="primary" :loading="vpDialog.loading" @click="submitVpForm">确认保存</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 弹窗2：绑定/更换真实题目 (远程搜索) -->
    <el-dialog v-if="bindDialog.visible" v-model="bindDialog.visible" title="关联题库中的真实题目" width="500px" append-to-body
      destroy-on-close>
      <div class="p-2">
        <div class="mb-4 text-xs text-amber-600 bg-amber-50 p-3 rounded border border-amber-100 flex items-start gap-2">
          <el-icon class="mt-0.5">
            <InfoFilled />
          </el-icon>
          <span>提示：请输入题目名称进行搜索。关联后，系统将自动同步该题目的所有出题步骤进度。</span>
        </div>

        <el-form label-position="top">
          <el-form-item label="搜索并选择题目" required>
            <el-select v-model="bindDialog.selectedProblemId" filterable remote reserve-keyword
              placeholder="请输入题目名称关键词..." :remote-method="searchProblems" :loading="bindDialog.searching"
              class="w-full">
              <el-option v-for="item in bindDialog.options" :key="item.id" :label="`${item.title}`" :value="item.id!" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="px-2 pb-2">
          <el-button @click="bindDialog.visible = false">取消</el-button>
          <el-button type="primary" :loading="bindDialog.submitting" :disabled="!bindDialog.selectedProblemId"
            @click="submitBind">
            执行关联
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 抽屉：测试点管理 -->
    <el-drawer v-model="drawer.visible" :title="drawer.type === 'testcase' ? '测试点管理' : '题解管理'" 
      size="40%" destroy-on-close>
      <template #header>
        <div class="flex flex-col">
          <span class="text-lg font-bold">{{ drawer.type === 'testcase' ? '测试点管理' : '题解管理' }}</span>
          <span class="text-xs text-gray-500 mt-1">{{ drawer.problemTitle }}</span>
        </div>
      </template>
      <TestcaseList v-if="drawer.type === 'testcase'" :active-problem-id="drawer.problemId" />
      <SolutionList v-if="drawer.type === 'solution'" :active-problem-id="drawer.problemId" />
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import {
  ElMessage, ElMessageBox, ElTooltip, ElDialog, ElButton,
  ElForm, ElFormItem, ElOption, ElSelect, ElIcon,
  ElColorPicker, ElInput, ElTable, ElTableColumn,
  ElCard, ElInputNumber, ElTag, ElDrawer
} from 'element-plus';
import { Clock, User, Plus, Check, InfoFilled } from '@element-plus/icons-vue';
import TestcaseList from '#/components/testcase-list/testcase-list.vue';
import SolutionList from '#/components/solution-list/solution-list.vue';

// 导入 API
import {
  getContestDetailVpApi,
  createVirtualProblemApi,
  updateVirtualProblemApi,
  deleteVirtualProblemApi,
  bindVirtualProblemApi,
  type ContestDetailOutWithVp,
} from '#/api/contest';
import { getProblemListApi, type ProblemListItem } from '#/api/problem';

const route = useRoute();
const router = useRouter();
const loading = ref(false);
const contest = ref<ContestDetailOutWithVp>({
  id: '',
  title: '',
  description: '',
  contest_start_time: '',
  contest_end_time: '',
  is_public: false,
  creator_name: '',
  virtual_problems: []
})

// 9步准备流程配置
const stepConfig = [
  { label: '题目标题', key: 'step_title_done' },
  { label: '时空限制', key: 'step_limit_done' },
  { label: '题目描述', key: 'step_description_done' },
  { label: '输入描述', key: 'step_input_description_done' },
  { label: '输出描述', key: 'step_output_description_done' },
  { label: '测试样例', key: 'step_example_done' },
  { label: '提示分析', key: 'step_hint_done' },
  { label: '测试点', key: 'step_testcase_done' },
  { label: '标准题解', key: 'step_solution_done' }
];

// --- 基础状态处理 ---
const getStatusText = (s: number) => ['未开始', '进行中', '已完成'][s] || '未开始';
const getStatusClass = (s: number) => [
  'bg-slate-200 border-slate-300',
  'bg-amber-400 border-amber-500',
  'bg-emerald-500 border-emerald-600'
][s] || 'bg-slate-200';

// --- 数据初始化 ---
const loadDetail = async () => {
  const id = route.query.id as string;
  if (!id || id.trim() === '') {
    router.push('/404')
  }
  if (!id) return;
  loading.value = true;
  try {
    const res = await getContestDetailVpApi(id);
    contest.value = res;
  } catch (error) {
    ElMessage.error('获取竞赛详情失败');
  } finally {
    loading.value = false;
  }
};

// --- 虚拟题目属性对话框 (新增/修改) ---
const vpDialog = reactive({
  visible: false,
  type: 'create', // create | edit
  loading: false,
  targetId: '',
  form: { name: '', description: '', order: 0, color: '#543874' }
});

const openVpDialog = (type: 'create' | 'edit', row?: any) => {
  vpDialog.type = type;
  if (type === 'edit' && row) {
    vpDialog.targetId = row.id;
    vpDialog.form = {
      name: row.name,
      description: row.description,
      order: row.order,
      color: row.color
    };
  } else {
    vpDialog.form = { name: '', description: '', order: 0, color: '#543874' };
  }
  vpDialog.visible = true;
};

const submitVpForm = async () => {
  if (!vpDialog.form.name || !vpDialog.form.description) {
    return ElMessage.warning('请填写必填项');
  }
  vpDialog.loading = true;
  try {
    if (vpDialog.type === 'create') {
      await createVirtualProblemApi(contest.value.id, vpDialog.form);
    } else {
      await updateVirtualProblemApi(vpDialog.targetId, vpDialog.form);
    }
    ElMessage.success('保存成功');
    vpDialog.visible = false;
    loadDetail();
  } catch (error) {
    ElMessage.error('操作失败');
  } finally {
    vpDialog.loading = false;
  }
};

// --- 题目绑定对话框 (远程搜索真实题目) ---
const bindDialog = reactive({
  visible: false,
  targetVpId: '',
  selectedProblemId: '',
  searching: false,
  submitting: false,
  options: [] as ProblemListItem[]
});

// --- 抽屉状态 (测试点 & 题解) ---
const drawer = reactive({
  visible: false,
  type: 'testcase', // testcase | solution
  problemId: '',
  problemTitle: ''
});

const handleOpenBind = (row: any) => {
  bindDialog.targetVpId = row.id;
  bindDialog.selectedProblemId = row.real_problem_id || '';
  bindDialog.options = [];
  bindDialog.visible = true;
  searchProblems(''); // 初始加载热门或默认题目
};

const searchProblems = async (query: string) => {
  bindDialog.searching = true;
  try {
    const res = await getProblemListApi({ keyword: query });
    console.log(res)
    bindDialog.options = Array.isArray(res) ? res : (res as any).items || [];
  } finally {
    bindDialog.searching = false;
  }
};

const submitBind = async () => {
  bindDialog.submitting = true;
  try {
    await bindVirtualProblemApi(bindDialog.targetVpId, {
      real_problem_id: bindDialog.selectedProblemId
    });
    ElMessage.success('关联绑定成功');
    bindDialog.visible = false;
    loadDetail();
  } catch (error: any) {
    ElMessage.error(error?.message || '关联失败，该题目可能已被占用');
  } finally {
    bindDialog.submitting = false;
  }
};

const handleDeleteVp = (id: string) => {
  ElMessageBox.confirm('确定要从比赛中移除该题目位置吗？', '操作警告', {
    type: 'warning',
    confirmButtonText: '确定移除',
    cancelButtonText: '取消'
  }).then(async () => {
    await deleteVirtualProblemApi(id);
    ElMessage.success('已移除');
    loadDetail();
  }).catch(() => { });
};

const goProblemEditor = (id: string) => {
  router.push(`/problem/problemDetail?id=${id}`);
};

const openDrawer = (type: 'testcase' | 'solution', row: any) => {
  if (!row.is_bound || !row.real_problem_id) {
    return ElMessage.warning('请先关联真实题目');
  }
  drawer.type = type;
  drawer.problemId = row.real_problem_id;
  drawer.problemTitle = row.real_problem_title || '';
  drawer.visible = true;
};

onMounted(loadDetail);

</script>

<style scoped>
/* 状态圆点核心背景色 */
.bg-slate-200 {
  background-color: #e2e8f0 !important;
}

.bg-amber-400 {
  background-color: #fbbf24 !important;
}

.bg-emerald-500 {
  background-color: #10b981 !important;
}

/* 矩阵辅助圆点（用于图例） */
.matrix-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

/* 呼吸动画：进行中的状态增加警示感 */
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {

  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }

  50% {
    opacity: 0.6;
    transform: scale(0.9);
  }
}

:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
}

:deep(.el-table .cell) {
  overflow: visible;
}
</style>
