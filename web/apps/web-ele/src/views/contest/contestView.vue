<template>
  <div class="min-h-screen bg-slate-50 p-6">
    <!-- 页眉区域 -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">比赛管理</h1>
        <p class="text-slate-500 text-sm mt-1">创建、编辑及监控所有竞赛活动</p>
      </div>

      <div class="flex items-center gap-3">
        <el-input v-model="searchKeyword" placeholder="搜索比赛名称..." class="w-64" :prefix-icon="Search" clearable
          @clear="fetchList" @keyup.enter="fetchList" />
        <el-button type="primary" @click="fetchList">搜索</el-button>
        <el-button type="success" :icon="Plus" @click="openDialog('create')">
          新增比赛
        </el-button>
      </div>
    </div>

    <!-- 列表区域 -->
    <el-card shadow="never" class="rounded-xl border-none">
      <el-table :data="tableData" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="title" label="比赛标题" min-width="200">
          <template #default="{ row }">
            <span class="font-bold text-slate-700">{{ row.title }}</span>
          </template>
        </el-table-column>

        <el-table-column label="起止时间" width="340">
          <template #default="{ row }">
            <div class="text-xs text-slate-500">
              <p>起：{{ row.start_time }}</p>
              <p>止：{{ row.end_time }}</p>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row)">{{ getStatusText(row) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="权限" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_public ? 'success' : 'warning'" effect="plain">
              {{ row.is_public ? '公开赛' : '私有赛' }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openDialog('edit', row)">编辑</el-button>
            <el-button type="primary" link @click="manageProblems(row)">题目</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-if="dialogVisible" v-model="dialogVisible" :title="dialogType === 'create' ? '新建比赛项目' : '编辑比赛信息'"
      width="600px" append-to-body destroy-on-close class="!rounded-2xl">
      <el-form :model="form" label-position="top" class="px-2">
        <el-form-item label="比赛标题" required>
          <el-input v-model="form.title" placeholder="请输入比赛名称，如：2026春季校赛" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="起止时间" required>
              <el-date-picker v-model="form.dateRange" type="datetimerange" range-separator="至" start-placeholder="开始时间"
                end-placeholder="结束时间" value-format="YYYY-MM-DD HH:mm:ss" class="!w-full" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="比赛描述">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="比赛规则及详细说明..." />
        </el-form-item>

        <div class="grid grid-cols-2 gap-4">
          <el-form-item label="公开性">
            <el-radio-group v-model="form.is_public">
              <el-radio :label="true">公开 (全站可见)</el-radio>
              <el-radio :label="false">私有 (指定用户组)</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item v-if="!form.is_public" label="关联用户组">
            <el-select v-model="form.group_id" placeholder="选择参赛用户组" class="w-full">
              <el-option v-for="group in groupOptions" :key="group.id" :label="group.name" :value="group.id" />
            </el-select>
          </el-form-item>
        </div>
      </el-form>

      <template #footer>
        <div class="flex justify-end gap-3 pb-2">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">
            确认提交
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue';
import { Search, Plus } from '@element-plus/icons-vue';
import {
  ElMessage, ElMessageBox, ElDialog, ElInput, ElOption, ElForm,
  ElFormItem, ElRadio, ElSelect, ElRadioGroup, ElRow,
  ElCol, ElTable, ElTableColumn, ElButton, ElCard, ElDatePicker
} from 'element-plus';
import {
  getContestListApi,
  createContestApi,
  updateContestApi,
  deleteContestApi,
  getGroupListApi, // 假设已有
  type ContestListItem,
  type UserGroup
} from '#/api/contest';

const loading = ref(false);
const submitting = ref(false);
const tableData = ref<ContestListItem[]>([]);
const searchKeyword = ref('');
const groupOptions = ref<UserGroup[]>([]);

// 弹窗逻辑
const dialogVisible = ref(false);
const dialogType = ref<'create' | 'edit'>('create');
const currentId = ref('');
const form = reactive({
  title: '',
  dateRange: [] as string[],
  description: '',
  is_public: true,
  group_id: ''
});

// 获取数据
const fetchList = async () => {
  loading.value = true;
  try {
    const res = await getContestListApi({ keyword: searchKeyword.value });
    tableData.value = res;
    // 获取用户组用于下拉选择
    groupOptions.value = await getGroupListApi();
  } catch (error) {
    ElMessage.error('加载失败');
  } finally {
    loading.value = false;
  }
};

// 状态判断
const getStatusTag = (row: any) => {
  const now = new Date().getTime();
  const start = new Date(row.start_time).getTime();
  const end = new Date(row.end_time).getTime();
  if (now < start) return 'info';
  if (now > end) return 'danger';
  return 'success';
};

const getStatusText = (row: any) => {
  const now = new Date().getTime();
  const start = new Date(row.start_time).getTime();
  const end = new Date(row.end_time).getTime();
  if (now < start) return '未开始';
  if (now > end) return '已结束';
  return '进行中';
};

// 弹窗操作
const openDialog = (type: 'create' | 'edit', row?: any) => {
  dialogType.value = type;
  if (type === 'edit' && row) {
    currentId.value = row.id;
    form.title = row.title;
    form.dateRange = [row.start_time, row.end_time];
    form.description = row.description;
    form.is_public = row.is_public;
    form.group_id = row.group_id;
  } else {
    Object.assign(form, {
      title: '',
      dateRange: [],
      description: '',
      is_public: true,
      group_id: ''
    });
  }
  dialogVisible.value = true;
};

const handleSubmit = async () => {
  if (!form.title || form.dateRange.length < 2) {
    return ElMessage.warning('请填写完整信息');
  }
  submitting.value = true;
  try {
    const payload = {
      ...form,
      start_time: form.dateRange[0],
      end_time: form.dateRange[1]
    };
    if (dialogType.value === 'create') {
      await createContestApi(payload);
      ElMessage.success('创建成功');
    } else {
      await updateContestApi(currentId.value, payload);
      ElMessage.success('保存成功');
    }
    dialogVisible.value = false;
    fetchList();
  } finally {
    submitting.value = false;
  }
};

const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定删除比赛 "${row.title}" 吗？`, '警告', {
    type: 'warning'
  }).then(async () => {
    await deleteContestApi(row.id);
    ElMessage.success('已删除');
    fetchList();
  });
};

const manageProblems = (row: any) => {
  // 跳转到题目选择界面
  ElMessage.info('正在进入题目管理...');
};

onMounted(fetchList);

// 彻底解决之前白屏隐患的清理工作
onBeforeUnmount(() => {
  dialogVisible.value = false;
  document.body.style.overflow = '';
  document.body.classList.remove('el-popup-parent--hidden');
  const modals = document.querySelectorAll('.v-modal');
  modals.forEach(m => m.remove());
});
</script>

<style scoped>
:deep(.el-card__body) {
  padding: 0;
}

:deep(.el-table) {
  --el-table-header-bg-color: #f8fafc;
  border-radius: 0 0 12px 12px;
}
</style>
