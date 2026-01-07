<template>
  <el-dialog v-model="dialogVisible" title="管理成员" width="540px" class="!rounded-xl" append-to-body destroy-on-close>
    <div class="p-2 space-y-4">
      <!-- 1. 选择框：仅显示不在组内的用户 -->
      <div class="space-y-2">
        <p class="text-xs font-medium text-gray-500 uppercase">添加新成员</p>
        <el-select
          v-model="selectedUserIds"
          multiple
          filterable
          placeholder="搜索并选择用户..."
          class="w-full"
          :loading="loading"
        >
          <!-- 这里改用 availableUsers -->
          <el-option v-for="item in availableUsers" :key="item.id" :label="item.name" :value="item.id">
            <div class="flex items-center gap-3">
              <el-avatar :size="24" :src="item.avatarUrl">{{ item.name?.charAt(0) }}</el-avatar>
              <span class="text-sm">{{ item.name }}</span>
              <span class="text-[10px] text-gray-400 ml-auto">ID: {{ item.id.substring(0, 5) }}</span>
            </div>
          </el-option>
        </el-select>
      </div>

      <!-- 2. 已有成员列表 -->
      <div class="space-y-2">
        <p class="text-xs font-medium text-gray-500 uppercase">当前组成员 ({{ props.existingUsers.length }})</p>
        <el-table :data="props.existingUsers" style="width: 100%" max-height="300px" size="small" border class="rounded-lg">
          <el-table-column label="成员信息">
            <template #default="{ row }">
              <div class="flex items-center gap-3">
                <el-avatar :size="32" :src="row.avatarUrl">{{ row.name?.charAt(0) }}</el-avatar>
                <span class="text-sm font-medium">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" align="center">
            <template #default="{ row }">
              <el-button type="danger" link @click="handleDeleteMembers(row.id)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end gap-3 px-2">
        <el-button class="!rounded-md" @click="dialogVisible = false">关闭</el-button>
        <el-button
          type="primary"
          class="!rounded-md"
          :disabled="selectedUserIds.length === 0"
          :loading="submitting"
          @click="handleAddMembers"
        >
          确认添加 ({{ selectedUserIds.length }})
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { getFileStreamUrl } from '#/api/core/file';
import { fetchAllUsersInfo, type UserItem, addGroupMembersApi, removeGroupMembersApi } from '#/api/contest'
import { ElMessage, ElDialog, ElOption, ElButton, ElSelect, ElAvatar, ElTag, ElTable, ElTableColumn } from 'element-plus';

const props = defineProps<{
  visible: boolean;
  id: string;
  existingUsers: UserItem[];
}>();

const emit = defineEmits(['update:visible', 'success']);

const dialogVisible = ref(false);
const submitting = ref(false);
const allUsers = ref<UserItem[]>([]);
const loading = ref(false);
const selectedUserIds = ref<string[]>([]);

/**
 * 【关键逻辑】计算可选用户：排除掉已在组内的用户
 */
const availableUsers = computed(() => {
  // 使用 Set 提高查找效率
  const existingIds = new Set(props.existingUsers.map(u => u.id));
  return allUsers.value.filter(user => !existingIds.has(user.id));
});

// 监听弹窗打开
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal;
  if (newVal) {
    selectedUserIds.value = []; // 每次打开重置选择
    initData();
  }
});

// 同步弹窗状态
watch(dialogVisible, (newVal) => {
  if (newVal !== props.visible) {
    emit('update:visible', newVal);
  }
});

const initData = async () => {
  // 注意：此处如果需要实时获取最新用户库，可以去掉 allUsers.value.length 的判断
  if (allUsers.value.length > 0) return;
  loading.value = true;
  try {
    const res = await fetchAllUsersInfo();
    const rawList = Array.isArray(res) ? res : (res as any)?.data || [];
    allUsers.value = rawList.map((user: any) => ({
      ...user,
      avatarUrl: user.avatar ? getFileStreamUrl(user.avatar) : ''
    }));
  } catch (error) {
    console.error('加载用户库失败', error);
  } finally {
    loading.value = false;
  }
};

/**
 * 添加成员
 */
const handleAddMembers = async () => {
  if (selectedUserIds.value.length === 0) return;
  submitting.value = true;
  try {
    await addGroupMembersApi(props.id, selectedUserIds.value);
    ElMessage.success('添加成功');
    selectedUserIds.value = [];
    // 实时更新：通知父组件刷新接口，从而刷新 props.existingUsers
    emit('success');
    // dialogVisible.value = false; // 如果你想继续添加，可以不关闭
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || '添加失败');
  } finally {
    submitting.value = false;
  }
};

/**
 * 删除成员
 */
/**
 * 删除成员逻辑
 */
const handleDeleteMembers = async (user_id: string) => {
  try {
    // 1. 调用接口
    await removeGroupMembersApi(props.id, user_id);
    ElMessage.success("已移除该成员");

    // 2. 关键：通知父组件刷新 fetchList
    emit('success');

  } catch (e: any) {
    ElMessage.error("移除失败");
  }
};
</script>
