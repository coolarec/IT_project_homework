<template>
  <!-- 主容器：使用 Tailwind 背景和内边距 -->
  <div class="min-h-screen bg-slate-50 p-6 ">

    <!-- 页眉区域 -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">用户组管理</h1>
        <p class="text-slate-500 text-sm mt-1">创建并管理您的参赛名单或权限分组</p>
      </div>

      <div class="flex items-center gap-3">
        <el-input v-model="searchKeyword" placeholder="搜索用户组名..." class="w-64" :prefix-icon="Search" clearable
          @clear="fetchList" @keyup.enter="fetchList" />
        <el-button type="primary" class="!rounded-md" @click="fetchList">搜索</el-button>
        <el-button type="success" :icon="Plus" class="!rounded-md" @click="openDialog('create')">
          新建小组
        </el-button>
      </div>
    </div>

    <!-- 表格容器：使用卡片样式 -->
    <div class="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-4 gap-7 my-4 px-4">
      <!-- 使用 v-for 循环渲染卡片 -->
      <el-card v-for="item in tableData" :key="item.id" shadow="never" class="h-full">
        <template #header>
          <div class="flex justify-between">
            <div class="font-bold text-lg">{{ item.name }}</div>
            <div>
              <el-button type="info" :icon="Edit" circle @click="openDialog('edit', item)"/>
              <el-button type="primary" :icon="AddLocation" circle @click="openMemberDialog(item)"/>
              <el-button type="danger" :icon="Delete" circle @click="handleDelete(item)"/>

            </div>
          </div>
        </template>

        <div class="text-gray-600">
          <p>成员人数: {{ item.member_count }}</p>
          <p>描述: {{ item.description }}</p>
        </div>

      </el-card>

    </div>

    <!-- 弹窗：新建/编辑 -->
    <el-dialog v-model="dialogVisible" :title="dialogType === 'create' ? '新建用户组' : '编辑用户组'" width="440px"
      class="!rounded-xl" append-to-body destroy-on-close>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">小组名称</label>
          <el-input v-model="form.name" placeholder="例如：ACM校队 A组" />
        </div>
        <div>
          <label class="block text-sm font-medium text-slate-700 mb-1">描述</label>
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入小组的用途描述" />
        </div>
      </div>
      <template #footer>
        <div class="flex justify-end gap-3 px-2">
          <el-button class="!rounded-md" @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" class="!rounded-md px-6" @click="handleSubmit">确认</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 弹窗：管理成员 -->
    <el-dialog v-model="memberDialogVisible" title="管理成员" width="440px" class="!rounded-xl" append-to-body destroy-on-close>
      <div class="p-2">
        <div class="bg-blue-50 border border-blue-100 rounded-lg p-3 mb-4">
          <p class="text-blue-700 text-xs leading-relaxed">
            请在下方输入用户的 <strong>UUID</strong>。如有多个，请使用半角逗号 <code class="bg-white px-1">,</code> 分隔。
          </p>
        </div>
        <el-input v-model="targetUserIds" type="textarea" :rows="5" placeholder="请输入用户 ID..." class="text-sm" />
      </div>
      <template #footer>
        <div class="flex justify-end gap-3 px-2">
          <el-button class="!rounded-md" @click="memberDialogVisible = false">关闭</el-button>
          <el-button type="primary" class="!rounded-md" @click="handleAddMembers">添加成员</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, onActivated } from 'vue';
import { ElMessage, ElMessageBox, ElInput, ElCard, ElButton, ElDialog } from 'element-plus';
import { Search, Plus,Edit,AddLocation,Delete } from '@element-plus/icons-vue';
import type { UserGroup, UserGroupIn } from '#/api/contest';
import {
  getGroupListApi,
  createGroupApi,
  updateGroupApi,
  deleteGroupApi,
  addGroupMembersApi
} from '#/api/contest';
// --- 状态与数据 ---
const loading = ref(false);
const tableData = ref<UserGroup[]>([]);
const searchKeyword = ref('');

// 弹窗控制
const dialogVisible = ref(false);
const dialogType = ref<'create' | 'edit'>('create');
const currentGroupId = ref('');
const form = reactive<UserGroupIn>({
  name: '',
  description: ''
});

// 成员管理
const memberDialogVisible = ref(false);
const targetUserIds = ref('');

// --- 逻辑函数 ---
const fetchList = async () => {
  loading.value = true;
  try {
    const res = await getGroupListApi({ name: searchKeyword.value });
    tableData.value = res;
  } catch (error) {
    ElMessage.error('获取列表失败');
  } finally {
    loading.value = false;
  }
  // console.log(tableData.value)
};

const openDialog = (type: 'create' | 'edit', row?: UserGroup) => {
  dialogType.value = type;
  if (type === 'edit' && row) {
    currentGroupId.value = row.id;
    form.name = row.name;
    form.description = row.description || '';
  } else {
    form.name = '';
    form.description = '';
  }
  dialogVisible.value = true;
};

const handleSubmit = async () => {
  if (!form.name) return ElMessage.warning('请输入名称');
  try {
    if (dialogType.value === 'create') {
      await createGroupApi(form);
      ElMessage.success('创建成功');
    } else {
      await updateGroupApi(currentGroupId.value, form);
      ElMessage.success('更新成功');
    }
    dialogVisible.value = false;
    fetchList();
  } catch (error) {
    ElMessage.error('操作失败');
  }
};

const handleDelete = (row: UserGroup) => {
  ElMessageBox.confirm(`确定要删除用户组 "${row.name}" 吗？`, '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
    buttonSize: 'default'
  }).then(async () => {
    await deleteGroupApi(row.id);
    ElMessage.success('删除成功');
    fetchList();
  }).catch(() => { });
};

const openMemberDialog = (row: UserGroup) => {
  currentGroupId.value = row.id;
  targetUserIds.value = '';
  memberDialogVisible.value = true;
};

const handleAddMembers = async () => {
  const ids = targetUserIds.value.split(',').map(id => id.trim()).filter(id => id);
  if (ids.length === 0) return ElMessage.warning('请输入用户ID');
  try {
    await addGroupMembersApi(currentGroupId.value, ids);
    ElMessage.success('添加成功');
    memberDialogVisible.value = false;
    fetchList();
  } catch (error) {
    ElMessage.error('添加失败');
  }
};

onMounted(() => fetchList());
onActivated(() => fetchList());
</script>

<style scoped></style>
