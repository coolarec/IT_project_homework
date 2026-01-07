<template>
  <!-- 主容器：使用 Tailwind 背景和内边距 -->
  <div class="min-h-screen  p-6 ">

    <!-- 页眉区域 -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-bold ">用户组管理</h1>
        <p class=" text-sm mt-1">创建并管理您的参赛名单或权限分组</p>
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
    <div class="grid grid-cols-[repeat(auto-fill,minmax(300px,1fr))] gap-7 my-4 px-4">
      <!-- 使用 v-for 循环渲染卡片 -->
      <el-card v-for="item in tableData" :key="item.id" shadow="never" class="h-full !rounded-xl">
        <template #header>
          <div class="flex justify-between items-center">
            <div>
              <div class="font-bold text-lg truncate w-40 my-1">{{ item.name }}</div>
              <p class="text-sm text-gray-500">
                创建者 {{ item.creator_name || '未知' }}
              </p>
            </div>
            <div class="flex gap-1">
              <el-button type="info" :icon="Edit" circle size="small" plain @click="openDialog('edit', item)" />
              <el-button type="primary" :icon="AddLocation" circle size="small" plain @click="openMemberDialog(item)" />
              <el-button type="danger" :icon="Delete" circle size="small" plain @click="handleDelete(item)" />
            </div>
          </div>
        </template>

        <div class="space-y-4">
          <!-- 描述 -->
          <p class="text-sm text-gray-500 line-clamp-2 h-10">
            {{ item.description || '暂无描述' }}
          </p>

          <!-- 成员头像堆叠区 -->
          <div class="flex items-center justify-between">
            <div class="flex -space-x-3 overflow-hidden">
              <!-- 假设 item.members 是后端返回的成员预览数组 -->
              <!-- 如果后端没给，你可以先循环一个固定长度的占位符测试样式 -->
              <template v-if="item.members && item.members.length > 0">
                <el-avatar v-for="(member, index) in item.members.slice(0, 5)" :key="member.id ?? index" :size="32"
                  :src="member.avatar ? getFileStreamUrl(member.avatar) : ''" class="border-2 border-white">
                  {{ member.name?.charAt(0) }}
                </el-avatar>
              </template>

              <!-- 无成员时的占位 -->
              <el-avatar v-else :size="32" class="!bg-gray-100 !text-gray-400 border-2 border-white">
                <el-icon>
                  <User />
                </el-icon>
              </el-avatar>

              <!-- 超过 5 个成员时的省略标记 -->
              <div v-if="item.member_count > 5"
                class="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 text-gray-500 text-[10px] border-2 border-white z-10">
                +{{ item.member_count - 5 }}
              </div>
            </div>

            <!-- 右侧人数统计 -->
            <span class="text-xs text-gray-400 font-medium">
              {{ item.member_count }} 人
            </span>
          </div>
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
    <user-selector v-model:visible="memberSelectorVisible" :id="currentGroupId" :existing-users="currentGroupMembers"
      @success="fetchList" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue';
import {
  ElMessage, ElMessageBox, ElInput, ElCard, ElButton, ElDialog,
  ElAvatar, ElIcon
} from 'element-plus';
import { Search, Plus, Edit, AddLocation, Delete } from '@element-plus/icons-vue';
import type { UserGroup, UserGroupIn } from '#/api/contest';
import userSelector from '#/components/user-selector/user-selector.vue';
import {
  getGroupListApi,
  createGroupApi,
  updateGroupApi,
  deleteGroupApi,
} from '#/api/contest';
import { getFileStreamUrl } from '#/api/core/file';
import { User } from '@element-plus/icons-vue'; // 记得引入 User 图标

// --- 状态与数据 ---
const loading = ref(false);
const tableData = ref<UserGroup[]>([]);
const searchKeyword = ref('');
const memberSelectorVisible = ref(false);

// 弹窗控制
const dialogVisible = ref(false);
const dialogType = ref<'create' | 'edit'>('create');
const currentGroupId = ref('');
const form = reactive<UserGroupIn>({
  name: '',
  description: ''
});


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

const currentGroupMembers = computed(() => {
  // 从大列表 tableData 中找到 id 匹配的那一项
  const group = tableData.value.find(g => g.id === currentGroupId.value);
  if (!group || !group.members) return [];

  // 处理头像 URL
  return group.members.map(member => ({
    ...member,
    avatarUrl: member.avatar != null ? getFileStreamUrl(member.avatar) : ''
  }));
});

const openMemberDialog = (row: UserGroup) => {
  currentGroupId.value = row.id;
  memberSelectorVisible.value = true;
};

onMounted(() => fetchList());
</script>

<style scoped></style>
