<template>
  <el-form label-position="top">
    <el-form-item label="编程语言">
      <el-select v-model="solutionForm.language" class="w-full">
        <el-option label="Python 3" value="Python" />
        <el-option label="C++" value="C++" />
        <el-option label="Java" value="Java" />
      </el-select>
    </el-form-item>
    <el-form-item label="核心代码">
      <template #label>
        核心代码链接
        <a href="https://paste.then.ac" target="_blank" class="text-blue-500 ">
          paste.then.ac
        </a>
      </template>
      <el-input v-model="solutionForm.code" placeholder="请粘贴标准解法代码链接..." class="font-mono" />
    </el-form-item>
    <el-form-item label="解题思路说明">
      <MdEditor v-model="solutionForm.description" style="height: 300px;">
      </MdEditor>
    </el-form-item>
    <el-button type="success" class="w-full" @click="submitSolution">发布题解</el-button>
  </el-form>
  <div class="flex items-center justify-between p-4 bg-gray-50 rounded-xl border border-gray-100 my-2">
    <div class="flex items-center gap-4">
      <span class="text-sm font-bold text-gray-700">题解进度:</span>
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
  <el-card v-for="solution in solutionList" body-class="p-2" class="my-2 p-0" shadow="never">
    <MdPreview :modelValue="solution.description" />

    <template #footer>
      <div class="flex items-center justify-between">
        <span>{{ solution.code }}</span>
        <el-button type="danger" plain @click="deleteSolution(solution.id)">删除</el-button>
      </div>
    </template>
  </el-card>

</template>
<script setup lang="ts">
import { ElForm, ElFormItem, ElInput, ElSelect, ElOption, ElButton, ElMessage, ElCard,ElTooltip } from 'element-plus';
import { onMounted, reactive, ref, watch } from 'vue';
import { createSolutionApi, type Solution, getSolutionsApi, type SolutionInput, deleteSolutionApi, type ProblemUpdateIn, updateProblemApi, getProblemDetailApi } from '#/api/problem';
import { MdEditor, MdPreview } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';
interface Props {
  activeProblemId: string
}
const currentStatus = ref<number>(0);
const origin = ref<number>(0);
const content = ["未完成", "创作中", "已完成"]

const deleteSolution = async (id: string) => {
  await deleteSolutionApi(id);
  solutionList.value = await getSolutionsApi(props.activeProblemId)
}
const props = defineProps<Props>();
// 题解表单数据
const solutionForm = reactive<SolutionInput>({
  language: 'Python',
  code: '',
  description: ''
});
const solutionList = ref<Solution[]>([])
// 提交题解
const submitSolution = async () => {
  if (!solutionForm.code) return ElMessage.warning('代码不能为空');

  try {
    await createSolutionApi(props.activeProblemId, solutionForm);
    ElMessage.success('题解已发布');
    solutionList.value = await getSolutionsApi(props.activeProblemId)
  } catch (e: any) {
    ElMessage.error('发布失败');
  }
};

watch(
  () => solutionList.value.length,
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

onMounted(async () => {
  try {
    solutionList.value = await getSolutionsApi(props.activeProblemId)
    // console.log(solutionList.value)
    const detail = await getProblemDetailApi(props.activeProblemId);
    currentStatus.value = detail.step_solution_done
    origin.value = currentStatus.value
  } catch (e) {
    solutionList.value = []
  }
})

const updateStatusOnly = async () => {
  if (currentStatus.value === origin.value) {
    ElMessage.info('状态未改变');
    return;
  }

  try {
    const payload: ProblemUpdateIn = {};
    if (currentStatus.value !== origin.value)
      payload.step_solution_done = currentStatus.value;
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
