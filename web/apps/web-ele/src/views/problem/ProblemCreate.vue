<template>
  <div class="p-4 min-h-screen">
    <div class="max-w-7xl mx-auto">
      <!-- 页面头部 -->
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-2xl font-bold">创建新题目</h1>
          <p >发布题目到题库，包含描述、样例及权限设置</p>
        </div>
        <el-button type="primary" size="large" :loading="loading" @click="handleSubmit">
          <el-icon class="mr-1">
            <Upload />
          </el-icon> 发布题目
        </el-button>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-row :gutter="24">
          <!-- 左侧：主要信息 -->
          <el-col :span="16">
            <el-card shadow="never" class="mb-6 rounded-xl border-none">
              <template #header><span class="font-bold text-lg">题目详情</span></template>

              <el-form-item label="题目标题" prop="title">
                <el-input v-model="form.title" placeholder="请输入直观的题目名称" size="large" />
              </el-form-item>

              <el-form-item label="题目描述 (Markdown)" prop="description">
                <!-- <el-input v-model="form.description" type="textarea" :rows="10" placeholder="详述背景、任务及限制..." /> -->
                <MdEditor v-model="form.description" :theme="isDark ? 'dark' : 'light'" />
              </el-form-item>

              <el-form-item label="输入描述">
                <el-input v-model="form.input_description" type="textarea" :rows="3" placeholder="如：第一行输入一个整数N..." />
              </el-form-item>
              <el-form-item label="输出描述">
                <el-input v-model="form.output_description" type="textarea" :rows="3" placeholder="如：输出N行结果..." />
              </el-form-item>
            </el-card>

            <!-- 样例管理区 -->
            <el-card shadow="never" class="rounded-xl border-none">
              <template #header>
                <div class="flex justify-between items-center">
                  <span class="font-bold text-lg">测试样例 (Examples)</span>
                  <el-button type="primary" link @click="addExample">
                    <el-icon class="mr-1">
                      <Plus />
                    </el-icon> 添加样例对
                  </el-button>
                </div>
              </template>

              <div v-for="(ex, index) in form.examples" :key="index" class="example-item">
                <div class="flex justify-between mb-2">
                  <span class="text-gray-400 text-xs uppercase font-bold">Example #{{ index + 1 }}</span>
                  <el-button v-if="form.examples.length > 1" type="danger" link
                    @click="removeExample(index)">删除</el-button>
                </div>
                <el-row :gutter="15">
                  <el-col :span="12">
                    <el-form-item label="样例输入">
                      <el-input v-model="ex.input_data" type="textarea" :rows="3" class="font-mono" />
                    </el-form-item>
                  </el-col>
                  <el-col :span="12">
                    <el-form-item label="样例输出">
                      <el-input v-model="ex.output_data" type="textarea" :rows="3" class="font-mono" />
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>
            </el-card>
          </el-col>

          <!-- 右侧：属性配置 -->
          <el-col :span="8">
            <el-card shadow="never" class="mb-6 rounded-xl border-none sticky top-4">
              <template #header><span class="font-bold">基础设置</span></template>
              <!-- <el-form-item label="时间限制" prop="time_limit"> -->
              <div class="flex items-center gap-2 whitespace-nowrap mb-2">
                <label class="text-sm  shrink-0" style="width: 80px;color: #323639;">时间限制</label>
                <el-input-number v-model="form.time_limit" :min="0" :max="10000" :controls="false"
                  style="width: 140px" />
                <span class="text-gray-500">ms</span>
              </div>
              <div class="flex items-center gap-2 whitespace-nowrap mb-2">
                <label class="text-sm  shrink-0" style="width: 80px;color: #323639;">空间限制</label>
                <el-input-number v-model="form.memory_limit" :min="0" :controls="false" style="width: 140px" />
                <span class="text-gray-500">kb</span>
              </div>
              <!-- </el-form-item> -->
              <el-form-item label="难度评级">
                <el-rate v-model="form.difficulty" :max="5" show-score score-template="{value} 星" />
              </el-form-item>

              <el-form-item label="题目标签">
                <el-select v-model="form.tags" multiple filterable placeholder="关联知识点" class="w-full">
                  <el-option v-for="tag in tagOptions" :key="tag.id" :label="tag.name" :value="tag.id" />
                </el-select>
              </el-form-item>

              <el-divider />

              <!-- 公共题库开关 -->
              <el-form-item label="发布选项">
                <div class="flex items-center justify-between w-full p-4 rounded-lg border border-blue-100 bg-blue-50">
                  <div>
                    <div class="text-blue-900 font-bold">公开题目</div>
                    <div class="text-blue-700 text-xs">开启后将出现在公共题库</div>
                  </div>
                  <el-switch v-model="form.is_public" />
                </div>
              </el-form-item>

              <el-form-item label="题目提示 (Hints)">
                <el-input v-model="form.analysis" type="textarea" :rows="6" placeholder="输入解题提示（可留空）" />
              </el-form-item>

              <div class="mt-6">
                <el-button class="w-full" type="primary" size="large" @click="handleSubmit">确认提交</el-button>
              </div>
            </el-card>
            <el-card shadow="never" class="mb-6 rounded-xl border-none sticky top-4">
              <template #header><span class="font-bold">进度处理表</span></template>
              <div class="flex flex-col w-full px-2">
                <div class="space-y-2">
                  <div v-for="item in stepList" :key="item.key"
                    class="flex items-center justify-between rounded-lg px-4 py-2">
                    <span class="text-sm font-medium ">
                      {{ item.label }}
                    </span>

                    <div class="flex gap-3">
                      <el-tooltip :content="content[s]" placement="top" v-for="s in [0, 1, 2]" effect="light">

                        <span class="inline-flex h-6 w-6 items-center justify-center">
                          <!-- 状态灯 -->
                          <span
                            class="select-none cursor-pointer text-lg opacity-40 transition-all duration-150 traffic-dot"
                            :class="[
                              s === 0 && 'text-red-500',
                              s === 1 && 'text-yellow-500',
                              s === 2 && 'text-green-500',
                              form[item.key] === s && 'active'
                            ]" @click="form[item.key] = s">
                            ●
                          </span>
                        </span>
                      </el-tooltip>
                    </div>
                  </div>
                </div>
                <div class="w-full mt-4 text-cente" v-if="isAllAccepted">
                  <el-button type="success" plain class="w-full">All Accepted!</el-button>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted,computed } from 'vue';
import {
  ElCard, ElForm, ElFormItem, ElInput, ElRow, ElCol, ElRate, ElSelect,
  ElOption, ElButton, ElSwitch, ElIcon, ElDivider, ElMessage, ElInputNumber, ElTooltip
} from 'element-plus';
import { Upload, Plus } from '@element-plus/icons-vue';
import type { FormInstance } from 'element-plus';
import { createProblemApi, getTagsApi, type Tag, type ProblemDetail } from '#/api/problem';
import { watch } from 'vue'
import { MdEditor } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';
import { useRouter } from 'vue-router';


const router = useRouter();
const formRef = ref<FormInstance>();
const loading = ref(false);
const tagOptions = ref<Tag[]>([]);

const content = ["未完成", "创作中", "已完成"]
const isAllAccepted = computed(() => {
  // 检查数组中的每一项，只有全部返回 true，结果才为 true
  return autoSteps.every(item => form[item.step] === 2) && form['step_limit_done'] === 2 && form['step_example_done'] === 2;
});


const form = reactive<ProblemDetail>({
  title: '',
  description: '',
  input_description: '',
  output_description: '',
  analysis: '',
  difficulty: 3,
  is_public: false,
  time_limit: 1000,
  memory_limit: 32768,
  tags: [] as Tag[],
  examples: [{ input_data: '', output_data: '' }],
  step_title_done: 0,
  step_limit_done: 0,
  step_description_done: 0,
  step_input_description_done: 0,
  step_output_description_done: 0,
  step_example_done: 0,
  step_hint_done: 0,
  step_testcase_done: 0,
  step_solution_done: 0,
  created_at: ''
});

watch(
  () => form.title,
  (val) => {
    form.step_title_done = val && val.trim() !== '' ? 2 : 0
  },
  { immediate: true }
)

const stepList = [
  { label: '题目标题', key: 'step_title_done' },
  { label: '时空限制', key: 'step_limit_done' },
  { label: '题目描述', key: 'step_description_done' },
  { label: '输入描述', key: 'step_input_description_done' },
  { label: '输出描述', key: 'step_output_description_done' },
  { label: '测试样例', key: 'step_example_done'},
  { label: '提示（如果有的话）', key: 'step_hint_done' },
] as const;



const autoSteps = [
  { field: 'title', step: 'step_title_done' },
  { field: 'description', step: 'step_description_done' },
  { field: 'input_description', step: 'step_input_description_done' },
  { field: 'output_description', step: 'step_output_description_done' },
  { field: 'analysis', step: 'step_hint_done' },
] as const;

const isEmpty = (val: any) => {
  if (Array.isArray(val)) return val.length === 0;
  return !val || String(val).trim() === '';
};
autoSteps.forEach(({ field, step }) => {
  watch(
    () => form[field as keyof typeof form],
    (newVal, oldVal) => {
      const stepKey = step as keyof typeof form;

      const setStatus = (status: number) => {
        (form as Record<string, any>)[stepKey] = status;
      };

      if (isEmpty(newVal)) {
        setStatus(0);
      } else if (isEmpty(oldVal)) {
        setStatus(1);
      } else if (!form[stepKey]) {
        setStatus(1);
      }
    },
    { deep: true }
  );
});

watch(
  () => form.examples,
  (list) => {
    form.step_example_done = list.some(
      e => e.input_data.trim() || e.output_data.trim()
    ) ? 1 : 0
  },
  { deep: true }
)

const rules = {
  title: [{ required: true, message: '请输入题目标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入题目描述', trigger: 'blur' }]
};

onMounted(async () => {
  try {
    tagOptions.value = await getTagsApi();
  } catch (e) {
    console.error('加载标签失败');
  }
});
const isDark = computed(()=>{return document.documentElement.classList.contains('dark')?true:false})

const addExample = () => form.examples.push({ input_data: '', output_data: '' });
const removeExample = (idx: number) => form.examples.splice(idx, 1);

const handleSubmit = async () => {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        await createProblemApi(form);
        ElMessage.success('发布成功！');
        router.push('/problem/ProblemView');
        // 可选：跳转回列表页
      } catch (err: any) {
        ElMessage.error(err.message || '发布失败');
      } finally {
        loading.value = false;
      }
    }
  });
};
watch(
  // 同时监听这两个字段
  () => [form.time_limit, form.memory_limit],
  ([newTime, newMemory]) => {
    // 确保两个值都大于 0
    const isTimeValid = (newTime ?? 0) > 0;
    const isMemoryValid = (newMemory ?? 0) > 0;

    if (isTimeValid && isMemoryValid) {
      // 如果都填了，设为 2 (已完成) 或 1 (根据你的业务逻辑)
      form.step_limit_done = 2;
    } else {
      // 只要有一个没填对，就回退到 0
      form.step_limit_done = 0;
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.example-item {
  border: 1px dashed #dcdfe6;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 20px;
}

:deep(.el-card__header) {
  border-bottom: 1px solid #f2f2f2;
}

.font-mono :deep(textarea) {
  font-family: 'Courier New', Courier, monospace;
}

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
