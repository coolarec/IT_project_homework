<template>
  <!-- v-if="drawerType === 'testcase'" -->

  <el-form label-position="top">
    <div class="grid grid-cols-2 gap-4 justify-items-center items-start">
      <!-- 输入文件 -->
      <el-form-item label="输入文件 (.in)">
        <el-upload action="#" :auto-upload="false" :limit="1" :on-change="onInputFileChange" drag>
          <el-icon class="el-icon--upload" :size="100">
            <upload-filled />
          </el-icon>
          <div class="el-upload__text">
            <em>上传</em>
          </div>
          <!-- <el-button type="primary">选择 IN 文件</el-button> -->
        </el-upload>

      </el-form-item>

      <!-- 输出文件 -->
      <el-form-item label="对应输出文件 (.out)">
        <el-upload action="#" :auto-upload="false" :limit="1" :on-change="onOutputFileChange" drag>
          <!-- <el-button type="success">选择 OUT 文件</el-button> -->
          <el-icon class="el-icon--upload" :size="100">
            <upload-filled />
          </el-icon>
          <div class="el-upload__text">
            <em>上传文件</em>
          </div>
        </el-upload>
      </el-form-item>
    </div>

    <el-form-item label="该点分值权重">

      <el-input-number v-model="testCaseForm.weight" :min="1" />
    </el-form-item>

    <el-button type="primary" class="w-full" @click="submitTestCase">确认上传</el-button>
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
        <span class="font-bold">{{ row.size }}</span>
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
import { ref, reactive, onMounted, watch } from 'vue';
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
const testCaseForm = reactive({
  weight: 1,
  inputFile: null as any,
  outputFile: null as any
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

// 处理输入文件
const onInputFileChange = (file: any) => {
  testCaseForm.inputFile = file.raw;
};

// 处理输出文件
const onOutputFileChange = (file: any) => {
  testCaseForm.outputFile = file.raw;
};

const submitTestCase = async () => {
  if (!testCaseForm.inputFile || !testCaseForm.outputFile) {
    return ElMessage.warning('请同时上传输入和输出文件');
  }

  const fd = new FormData();
  fd.append('input_file', testCaseForm.inputFile);
  fd.append('output_file', testCaseForm.outputFile);
  fd.append('weight', testCaseForm.weight.toString());

  loading.value = true;
  try {
    // 调用接口
    await uploadTestCaseApi(props.activeProblemId, fd);
    ElMessage.success('测试点上传成功并存入文件系统');
    testcaseData.value = await getTestCaseApi(props.activeProblemId)

    // 刷新列表逻辑...
  } catch (e) {
    ElMessage.error('上传失败');
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
