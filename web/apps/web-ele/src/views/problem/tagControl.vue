<template>
  <div class="p-4 min-h-screen">

    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-bold">标签管理</h1>
        <p class=" text-sm mt-1">增加或删除题目标签</p>
      </div>
      <div class="flex items-center gap-2">
        <el-form ref="formRef" class="flex items-center gap-2">
          <el-input v-model="newTag.name" placeholder="请输入新标签" style="width: 200px" />
          <el-button type="primary" @click="addTag">新增标签</el-button>
        </el-form>

        <el-button type="primary" @click="fetchTagList">
          刷新列表
        </el-button>
      </div>
    </div>
    <el-card shadow="never" class="rounded-xl border-none">
      <el-table :data="tableData" style="width: 100%" stripe v-loading="loading">
        <el-table-column type="index" label="#" width="60" align="center" />

        <!-- <el-table-column prop="id" label="ID" width="80px" /> -->
        <el-table-column prop="name" label="标签名">
          <template #default="{ row }">
            <span class="font-bold">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column label="快捷管理" width="100px" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" plain @click="deleteTag(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ElTableColumn, ElCard, ElButton, ElTable, ElForm, ElInput, ElMessage } from 'element-plus';
import { onMounted, ref } from 'vue';
import { type Tag, getTagsApi, createTagApi, type TagIn, deleteTagApi } from "#/api/problem"

const tableData = ref<Tag[]>([])
const loading = ref(true)
const newTag = ref<TagIn>({
  "name": '',
});
onMounted(() => {
  fetchTagList()
})
const fetchTagList = async () => {
  loading.value = true;
  try {
    tableData.value = await getTagsApi();
  }
  catch (e) {
    console.log(e);
  }
  finally {
    loading.value = false;
  }
}
const addTag = async () => {
  if (!newTag.value.name.trim()) {
    ElMessage.warning('标签不能为空');
    return;
  }

  try {
    await createTagApi(newTag.value);

    ElMessage.success('新增成功');
    newTag.value.name = '';
    await fetchTagList();
  }
  catch (e) {
    ElMessage.error("请勿重复添加相同标签")
  }
};

const deleteTag = async (id: string) => {
  try {
    await deleteTagApi(id);
    await fetchTagList();
  }
  catch (e) {
    console.log(e);
  }
};

</script>

<style scoped>
:deep(.el-card__body) {
  padding: 0;
}

:deep(.el-table) {
  border-radius: 0 0 12px 12px;
}
</style>
