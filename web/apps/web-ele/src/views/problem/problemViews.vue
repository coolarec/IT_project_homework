<template>
  <div class="p-4  min-h-screen">
    <el-card shadow="never" class="rounded-xl border-none">
      <template #header>
        <div class="flex justify-between items-center">
          <span class="text-xl font-bold">题目管理库</span>
          <el-button type="primary" @click="fetchList">刷新列表</el-button>
        </div>
      </template>

      <el-input v-model="keyword" style="width: 240px" class="my-2" placeholder="请输入提示词" :suffix-icon="Search" />

      <!-- 题目表格 -->
      <el-table :data="tableData" v-loading="loading" style="width: 100%" stripe>
        <!-- <el-table-column prop="id" label="ID" width="80" /> -->
        <el-table-column prop="title" label="题目名称" min-width="200">
          <template #default="{ row }">
            <span class="font-bold">{{ row.title }}</span>
            <el-tag v-if="!row.is_public" type="info" size="small" class="ml-2">私有</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="难度" width="150">
          <template #default="{ row }">
            <el-rate v-model="row.difficulty" disabled />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleDateString() }}
          </template>
        </el-table-column>

        <!-- 操作列 -->
        <el-table-column label="快捷管理" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" plain @click="openDrawer(row, 'testcase')">
              测试点
            </el-button>
            <el-button type="success" size="small" plain @click="openDrawer(row, 'solution')">
              写题解
            </el-button>
            <el-button type="info" size="small" plain @click="openEditor(row)">
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 右侧遮罩抽屉 -->
    <el-drawer v-model="drawerVisible" :title="drawerTitle" size="45%" destroy-on-close>
      <div v-if="activeProblem" class="px-4">
        <div v-if="drawerType === 'testcase'">
          <testcase-list :active-problem-id="activeProblem.id" />
        </div>
        <!-- 切换：增加题解 -->
        <div v-if="drawerType === 'solution'">
          <solution-list :active-problem-id="activeProblem.id" />
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch,nextTick } from 'vue';
import {
  ElDrawer, ElTable, ElTableColumn,
  ElCard, ElRate, ElButton, ElTag, ElInput
} from 'element-plus';
import { getProblemListApi, type ProblemListItem, } from '#/api/problem';
import { router } from '#/router';
import { Search } from '@element-plus/icons-vue'
import testcaseList from '#/components/testcase-list/testcase-list.vue';
import SolutionList from '#/components/solution-list/solution-list.vue';
const loading = ref(false);
const tableData = ref<ProblemListItem[]>([]);

const drawerVisible = ref(false);
const drawerType = ref<'testcase' | 'solution'>('testcase');
const drawerTitle = ref('');
const activeProblem = ref<any>(null);

// 题解表单数据
const solutionForm = reactive({
  language: 'Python',
  code: '',
  description: ''
});

// 获取题目列表
const keyword = ref(''); // 搜索框绑定的变量

const fetchList = async () => {
  loading.value = true;
  try {
    // 传给 API 一个包含 keyword 的对象
    tableData.value = await getProblemListApi({
      keyword: keyword.value
    });
  } catch (error) {
    console.error('获取题目列表失败:', error);
  } finally {
    loading.value = false;
  }
};

watch(
  () => keyword.value,
  () => {
    fetchList()
  }
)

onMounted(async()=>{
  await nextTick();
  fetchList()
}
);

// 打开侧边栏
const openDrawer = async (problem: any, type: 'testcase' | 'solution') => {
  activeProblem.value = problem;
  drawerType.value = type;
  drawerTitle.value = type === 'testcase'
    ? `管理测试点: ${problem.title}`
    : `撰写题解: ${problem.title}`;

  // 重置表单
  solutionForm.code = '';
  drawerVisible.value = true;

};

const openEditor = (row: ProblemListItem) => {
  router.push(`/problem/problemDetail?id=${row.id}`);
}

</script>

<style scoped>
.font-mono :deep(textarea) {
  font-family: 'Fira Code', 'Courier New', monospace;
  background-color: #f8f9fa;
}

:deep(.el-drawer__header) {
  margin-bottom: 0;
  padding: 20px;
  font-weight: bold;
  border-bottom: 1px solid #eee;
}

:deep(.el-upload-dragger) {
  width: 190px;
  height: 190px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.upload :deep(.el-icon) {
  font-size: 48px;
  display: flex;
  flex-direction: column;
  align-items: center;
  /* 水平居中 */
  justify-content: center;
  /* 垂直居中 */
}

:deep(.el-upload-list__item-name) {
  max-width: 190px;
}

.example-box {
  border-left: 4px solid #409eff;
}
</style>
