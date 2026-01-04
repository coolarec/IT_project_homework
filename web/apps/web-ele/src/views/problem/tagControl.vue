<template>
  <div class="p-4 min-h-screen">
    <el-card shadow="never" class="rounded-xl border-none">
      <template #header>

        <div class="flex justify-between items-center">
          <span class="text-xl font-bold">标签管理库</span>
          <div class="flex items-center gap-2">
            <el-form ref="formRef" class="flex items-center gap-2">
              <el-input v-model="newTag.name" placeholder="请输入" style="width: 200px" />
              <el-button type="primary" @click="addTag">新增标签</el-button>
            </el-form>

            <el-button type="primary" @click="fetchTagList">
              刷新列表
            </el-button>
          </div>
        </div>
      </template>
      <el-table :data="tableData" style="width: 100%" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80px" />
        <el-table-column prop="name" label="name">
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

const deleteTag = async (id: number) => {
  try {
    await deleteTagApi(id);
    await fetchTagList();
  }
  catch (e) {
    console.log(e);
  }
};

</script>

<style scoped></style>
