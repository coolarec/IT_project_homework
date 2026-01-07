<template>
  <!-- v-if="drawerType === 'testcase'" -->

  <el-form label-position="top">
    <!-- 合并为一个上传框 -->
    <el-form-item label="批量上传测试点 (同时选择多个 .in 和 .out 文件)">
      <el-upload class="upload-demo w-full" action="#" :auto-upload="false" :on-change="onFileChange"
        :on-remove="onFileRemove" :file-list="fileList" multiple drag accept=".in,.out">
        <el-icon class="el-icon--upload">
          <upload-filled />
        </el-icon>
        <div class="el-upload__text">
          将所有文件拖到此处，或 <em>点击上传</em>
          <div class="text-xs mt-2">系统将自动匹配文件名相同的 .in 和 .out 文件</div>
        </div>
      </el-upload>
    </el-form-item>

<!-- 匹配结果预览区 -->
<div v-if="fileList.length > 0" class="mt-4 p-4 rounded-xl border border-gray-100 bg-gray-50/50">
  <div class="flex items-center justify-between mb-3">
    <h4 class="text-sm font-bold text-gray-700 flex items-center">
      <el-icon class="mr-2 text-blue-500"><Memo /></el-icon>
      解析预览
    </h4>
    <div class="space-x-2">
      <el-tag size="small" type="success" effect="light">已就绪: {{ matchedPairs.length }} 组</el-tag>
      <el-tag v-if="unmatchedFiles.length > 0" size="small" type="danger" effect="light">
        待完善: {{ unmatchedFiles.length }} 个
      </el-tag>
    </div>
  </div>

  <!-- 滚动区域 -->
  <el-scrollbar max-height="200px">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
      <!-- 已匹配成功的卡片 -->
      <div
        v-for="pair in matchedPairs"
        :key="pair.name"
        class="flex items-center justify-between p-2 bg-white border border-emerald-100 rounded-lg shadow-sm"
      >
        <div class="flex items-center overflow-hidden">
          <el-icon class="text-emerald-500 mr-2"><CircleCheckFilled /></el-icon>
          <span class="text-xs font-mono text-gray-600 truncate">{{ pair.name }}</span>
        </div>
        <div class="flex gap-1 shrink-0">
          <span class="text-[10px] px-1.5 py-0.5 bg-emerald-50 text-emerald-600 rounded border border-emerald-200">.in</span>
          <span class="text-[10px] px-1.5 py-0.5 bg-emerald-50 text-emerald-600 rounded border border-emerald-200">.out</span>
        </div>
      </div>

      <!-- 未匹配的错误卡片 -->
      <div
        v-for="miss in unmatchedFiles"
        :key="miss"
        class="flex items-center justify-between p-2 bg-red-50/50 border border-red-100 rounded-lg"
      >
        <div class="flex items-center overflow-hidden">
          <el-icon class="text-red-400 mr-2"><WarningFilled /></el-icon>
          <span class="text-xs font-mono text-red-500 truncate">{{ miss }}</span>
        </div>
        <span class="text-[10px] text-red-400 italic">缺失配对</span>
      </div>
    </div>
  </el-scrollbar>

  <!-- 提示信息 -->
  <div v-if="matchedPairs.length === 0" class="text-center py-4 text-gray-400 text-xs">
    等待文件解析... 请确保文件名一致（如 1.in 和 1.out）
  </div>
</div>

    <el-button type="primary" class="w-full" :loading="loading" :disabled="matchedPairs.length === 0"
      @click="submitTestCase">
      确认上传 {{ matchedPairs.length }} 组测试点
    </el-button>
  </el-form>


  <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-100 my-2">
    <div class="flex items-center gap-4">
      <span class="text-sm font-bold text-gray-700">测试点进度:</span>
      <div class="flex gap-2">
        <el-tooltip v-for="s in [0, 1, 2]" :key="s" :content="content[s]" placement="top" effect="light">
          <span class="inline-flex h-8 w-8 items-center justify-center">
            <span class="select-none cursor-pointer text-2xl transition-all duration-200 traffic-dot" :class="[
              s === 0 && 'text-red-500',
              s === 1 && 'text-yellow-500',
              s === 2 && 'text-green-500',
              currentStatus === s && 'active'
            ]" @click="currentStatus = s">
              ●
            </span>
          </span>
        </el-tooltip>
      </div>
    </div>

    <!-- 提交按钮 -->
    <el-button type="primary" @click="updateStatusOnly" round>
      更新状态
    </el-button>
  </div>

  <el-table :data="testcaseData" v-loading="loading" style="width: 100%;">
    <el-table-column type="index" label="序号" width="80" align="center" />

    <el-table-column prop="input_filename" label="输入文件" min-width="150">
      <template #default="{ row }">
        <span class="font-bold">{{ row.input_filename }}</span>
      </template>
    </el-table-column>

    <el-table-column prop="output_filename" label="输出文件" min-width="150">
      <template #default="{ row }">
        <span class="font-bold">{{ row.output_filename }}</span>
      </template>
    </el-table-column>

    <el-table-column prop="size" label="文件总大小" min-width="150">
      <template #default="{ row }">
        <span class="font-bold">
          <!-- 假设 row.size 是字节 (B) -->
          {{ (row.size / (1024 * 1024)).toFixed(2) }} MB
        </span>
      </template>
    </el-table-column>

    <el-table-column label="快捷管理">
      <template #default="{ row }">
        <el-button type="danger" size="small" plain @click="delTestcase(row.id)">
          删除
        </el-button>
      </template>
    </el-table-column>
  </el-table>

</template>
<script lang="ts" setup>
import { ref, onMounted, watch, computed } from 'vue';
import { ElMessageBox, ElInputNumber, ElUpload, ElForm, ElTable, ElTableColumn, ElMessage, ElButton, ElFormItem, ElIcon, ElTooltip } from 'element-plus';
import { uploadTestCaseApi, getTestCaseApi, deleteTestCaseApi, type TestCase, updateProblemApi, getProblemDetailApi, type ProblemUpdateIn } from '#/api/problem';
import { UploadFilled } from '@element-plus/icons-vue'

const loading = ref(false);
interface Props {
  activeProblemId: string
}

const currentStatus = ref<number>(0);
const origin = ref<number>(0);

const content = ["未完成", "创作中", "已完成"]

const testcaseData = ref<TestCase[]>([])

const fileList = ref<any[]>([]);
const testCaseForm = ref({
  weight: 10
});

watch(
  () => testcaseData.value.length,
  (len, oldLen) => {
    if (len > 0 && oldLen === 0) {
      currentStatus.value = 1
    }
    else if (len == 0) {
      currentStatus.value = 0;
    }
  },
  { immediate: true }
)

const props = defineProps<Props>();

// 处理文件变化
const onFileChange = (file: any, files: any[]) => {
  fileList.value = files;
};

// 处理删除文件
const onFileRemove = (file: any, files: any[]) => {
  fileList.value = files;
};

// 提取文件名逻辑（封装成函数复用）
const getFileNameAndExt = (filename: string) => {
  const lastDotIndex = filename.lastIndexOf('.');
  if (lastDotIndex <= 0) return { name: '', ext: '' }; // 忽略隐藏文件或无后缀文件
  return {
    name: filename.substring(0, lastDotIndex),
    ext: filename.substring(lastDotIndex + 1).toLowerCase()
  };
};

// 1. 自动匹配文件对 (用于提交)
const matchedPairs = computed(() => {
  const groups: Record<string, { in?: any; out?: any }> = {};

  fileList.value.forEach((f) => {
    const { name, ext } = getFileNameAndExt(f.name);
    if (!name) return;

    if (ext === 'in' || ext === 'out') {
      if (!groups[name]) groups[name] = {};
      groups[name][ext] = f.raw;
    }
  });

  return Object.keys(groups)
    .filter(name => groups[name]?.in && groups[name]?.out) // 使用可选链 ?.
    .map(name => ({
      name,
      inputFile: groups[name]?.in,
      outputFile: groups[name]?.out
    }));
});


// 未能匹配成功的文件（用于提示用户）
const unmatchedFiles = computed(() => {
  const groups: Record<string, { in?: boolean; out?: boolean }> = {};
  fileList.value.forEach(f => {
    const name = f.name.substring(0, f.name.lastIndexOf('.'));
    const ext = f.name.substring(f.name.lastIndexOf('.') + 1).toLowerCase();
    if (!groups[name]) groups[name] = {};
    if (ext === 'in') groups[name].in = true;
    if (ext === 'out') groups[name].out = true;
  });
  return Object.keys(groups).filter(name => !(groups[name]?.in && groups[name].out));
});

const submitTestCase = async () => {
  if (matchedPairs.value.length === 0) {
    return ElMessage.warning('没有找到匹配的 .in 和 .out 文件对');
  }

  loading.value = true;
  let successCount = 0;
  let failCount = 0;

  try {
    for (const pair of matchedPairs.value) {
      const fd = new FormData();
      fd.append('input_file', pair.inputFile);
      fd.append('output_file', pair.outputFile);
      fd.append('weight', testCaseForm.value.weight.toString());

      try {
        await uploadTestCaseApi(props.activeProblemId, fd);
        successCount++;
      } catch (e) {
        console.error(`上传失败: ${pair.name}`, e);
        failCount++;
      }
    }

    if (failCount === 0) {
      ElMessage.success(`成功上传 ${successCount} 组测试点`);
    } else {
      ElMessage.warning(`上传完成。成功: ${successCount}, 失败: ${failCount}`);
    }

    // 刷新数据
    testcaseData.value = await getTestCaseApi(props.activeProblemId);
    fileList.value = []; // 清空上传列表
  } catch (e) {
    ElMessage.error('请求过程中发生错误');
  } finally {
    loading.value = false;
  }
};
// 删除样例
const delTestcase = async (testCaseId: string) => {
  try {
    // 1. 增加二次确认，防止误删
    await ElMessageBox.confirm(
      '确定要永久删除该测试点吗？相关的输入输出文件记录也将被清理。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );

    // 2. 必须使用 await，否则 API 请求还没结束就会执行后面的刷新逻辑
    await deleteTestCaseApi(testCaseId);

    ElMessage.success("测试点删除成功");

    // 3. 重新获取列表以刷新 UI
    if (props.activeProblemId) {
      testcaseData.value = await getTestCaseApi(props.activeProblemId);
    }
  } catch (e: any) {
    // 如果是点击了“取消”按钮，不需要报错
    if (e !== 'cancel') {
      ElMessage.error(e?.message || "测试点删除失败");
      console.error("删除出错:", e);
    }
  }
};

onMounted(async () => {
  testcaseData.value = await getTestCaseApi(props.activeProblemId)
  const detail = await getProblemDetailApi(props.activeProblemId);
  currentStatus.value = detail.step_testcase_done
  origin.value = currentStatus.value
})

const updateStatusOnly = async () => {
  if (currentStatus.value === origin.value) {
    ElMessage.info('状态未改变');
    return;
  }

  try {
    const payload: ProblemUpdateIn = {};
    if (currentStatus.value !== origin.value)
      payload.step_testcase_done = currentStatus.value;
    await updateProblemApi(props.activeProblemId, payload);
    origin.value = currentStatus.value;
    ElMessage.success('测试点状态已更新');
  } catch (error) {
    console.error(error);
    ElMessage.error('更新失败');
  }
};
</script>
<style lang="css" scoped>
.traffic-dot {
  font-size: 30px;
  cursor: pointer;
  opacity: 0.3;
  transition: all 0.2s;
  user-select: none;
}

.traffic-dot.active {
  opacity: 1;
  transform: scale(1.2);
}

.traffic-dot:hover {
  opacity: 0.6;
}
</style>
