<template>
  <div class="p-4 min-h-screen">
    <div class="max-w-7xl mx-auto">
      <!-- 页面头部 -->
      <div class="flex justify-between items-center mb-6">
        <!-- 返回按钮 -->
        <el-button circle size="large" @click="goBack">
          <el-icon>
            <ArrowLeft />
          </el-icon>
        </el-button>
        <div class="flex flex-col items-center">
          <h1 class="text-2xl font-bold ">编辑题目</h1>
          <p class="text-gray-500">修改题目详细信息、样例及限制设置</p>
        </div>
        <el-button type="primary" size="large" @click="handleSubmit">
          <el-icon class="mr-1">
            <Upload />
          </el-icon> 保存更新
        </el-button>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-row :gutter="24">
          <!-- 左侧：主要信息 (保持不变) -->
          <el-col :span="16">
            <el-card shadow="never" class="mb-6 rounded-xl border-none">
              <template #header><span class="font-bold text-lg">题目详情</span></template>

              <el-form-item label="题目标题" prop="title">
                <el-input v-model="form.title" placeholder="请输入直观的题目名称" size="large" />
              </el-form-item>

              <el-form-item label="题目描述 (Markdown)" prop="description">
                <MdEditor v-model="form.description" :theme="isDark ? 'dark' : 'light'" />
              </el-form-item>

              <el-form-item label="输入描述">
                <el-input v-model="form.input_description" type="textarea" :rows="3" placeholder="如：第一行输入一个整数N..." />
              </el-form-item>
              <el-form-item label="输出描述">
                <el-input v-model="form.output_description" type="textarea" :rows="3" placeholder="如：输出N行结果..." />
              </el-form-item>
            </el-card>

            <!-- 样例管理区 (保持不变) -->
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
                  <el-button v-if="form.examples?.length ?? 0 > 1" type="danger" link
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
              <div class="flex items-center gap-2 whitespace-nowrap mb-2">
                <label class="text-sm shrink-0" style="width: 80px;color: #323639;">时间限制</label>
                <el-input-number v-model="form.time_limit" :min="0" :max="10000" :controls="false"
                  style="width: 140px" />
                <span class="text-gray-500">ms</span>
              </div>
              <div class="flex items-center gap-2 whitespace-nowrap mb-2">
                <label class="text-sm shrink-0" style="width: 80px;color: #323639;">空间限制</label>
                <el-input-number v-model="form.memory_limit" :min="0" :controls="false" style="width: 140px" />
                <span class="text-gray-500">kb</span>
              </div>

              <el-form-item label="难度评级">
                <el-rate v-model="form.difficulty" :max="5" show-score score-template="{value} 星" />
              </el-form-item>

              <el-form-item label="题目标签">
                <el-select v-model="form.tags" multiple filterable placeholder="关联知识点" class="w-full">
                  <el-option v-for="tag in tagOptions" :key="tag.id" :label="tag.name" :value="tag.id" />
                </el-select>
              </el-form-item>

              <el-divider />

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

              <!-- 这里修改为两个按钮 -->
              <div class="mt-6 ">
                <div class="flex gap-3">
                  <el-button class="flex-1" type="primary" size="large" :loading="loading" @click="handleSubmit">
                    提交更新
                  </el-button>
                  <el-button class="flex-1" type="danger" plain size="large" @click="handleDelete">
                    删除题目
                  </el-button>
                </div>
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
import { ref, reactive, onMounted, watch, computed } from 'vue';
import {
  ElCard, ElForm, ElFormItem, ElInput, ElRow, ElCol, ElRate, ElSelect,
  ElOption, ElButton, ElSwitch, ElIcon, ElDivider, ElMessage, ElInputNumber, ElMessageBox,
  ElTooltip
} from 'element-plus';
import { Upload, Plus, ArrowLeft } from '@element-plus/icons-vue';
import type { FormInstance } from 'element-plus';
import { useRoute, useRouter } from 'vue-router';
import { getTagsApi, getProblemDetailApi, type Tag, type ProblemUpdateIn, type ExampleIn, updateProblemApi, type ProblemDetail,deleteProblemApi } from '#/api/problem';

import { MdEditor } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';


const content = ["未完成", "创作中", "已完成"]

const route = useRoute();
const router = useRouter();
const formRef = ref<FormInstance>();
const loading = ref(false);
const tagOptions = ref<Tag[]>([]);

// 判定是否为编辑模式
const problemId = route.query.id ? String(route.query.id) : null;

const form = reactive<ProblemUpdateIn>({
  title: '',
  description: '',
  input_description: '',
  output_description: '',
  analysis: '',
  difficulty: 3,
  is_public: true,
  time_limit: 0,
  memory_limit: 0,
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
  step_solution_done: 0
});
const isAllAccepted = computed(() => {
  // 检查数组中的每一项，只有全部返回 true，结果才为 true
  return autoSteps.every(item => form[item.step] === 2) && form['step_limit_done'] === 2;
});
const rules = {
  title: [{ required: true, message: '请输入题目标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入题目描述', trigger: 'blur' }]
};

const stepList = [
  { label: '题目标题', key: 'step_title_done' },
  { label: '题目描述', key: 'step_description_done' },
  { label: '时空限制', key: 'step_limit_done' },
  { label: '输入描述', key: 'step_input_description_done' },
  { label: '输出描述', key: 'step_output_description_done' },
  { label: '提示（如果有的话）', key: 'step_hint_done' },
] as const;

const autoSteps = [
  { field: 'title', step: 'step_title_done' },
  { field: 'description', step: 'step_description_done' },
  { field: 'input_description', step: 'step_input_description_done' },
  { field: 'output_description', step: 'step_output_description_done' },
  { field: 'analysis', step: 'step_hint_done' },
] as const;

watch(
  // 同时监听这两个字段
  () => [form.time_limit, form.memory_limit],
  ([newTime, newMemory]) => {
    // 确保两个值都大于 0
    const isTimeValid = (newTime ?? 0) > 0;
    const isMemoryValid = (newMemory ?? 0) > 0;

    if (isTimeValid && isMemoryValid) {
      // 如果都填了，设为 2 (已完成) 或 1
      form.step_limit_done = 2;
    } else {
      // 只要有一个没填对，就回退到 0
      form.step_limit_done = 0;
    }
  },
  { immediate: true }
);

let origin = reactive<ProblemDetail>({
  title: '',
  description: '',
  input_description: '',
  output_description: '',
  analysis: '',
  difficulty: 3,
  is_public: true,
  time_limit: 0,
  memory_limit: 0,
  tags: [] as Tag[],
  examples: [{ input_data: '', output_data: '' }] as ExampleIn[],
  step_title_done: 0,
  step_limit_done: 0,
  step_description_done: 0,
  step_input_description_done: 0,
  step_output_description_done: 0,
  step_example_done: 0,
  step_hint_done: 0,
  step_testcase_done: 0,
  step_solution_done: 0,
  id: '',
  created_at: '',
});

const fetchDetail = async () => {
  // 加载标签
  tagOptions.value = await getTagsApi();
  const detail = await getProblemDetailApi(problemId!);
  console.log(detail)
  // 数据映射回 form
  Object.assign(form, {
    ...detail,
    tags: detail.tags?.map((t: any) => t.id) || [],
    examples: detail.examples?.length ? detail.examples : [{ input_data: '', output_data: '' }]
  });
  // console.log(form)
  Object.assign(origin, JSON.parse(JSON.stringify(form)));
}

onMounted(async () => {
  loading.value = true;
  if (problemId != null) {
    try {
      await fetchDetail()
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
            } else if (form[stepKey]?.toString().trim() !== '') {
              setStatus(1);
            }
          },
          { deep: true }
        );
      });
    } catch (e) {
      ElMessage.error('初始化数据失败');
    } finally {
      loading.value = false;
    }
  }
  else {
    router.push('/404')
  }

});


const addExample = () => {
  if (!form.examples) form.examples = [];
  form.examples.push({ input_data: '', output_data: '' });
  fetchDetail()
}
const removeExample = (idx: number) => {
  if (!form.examples) form.examples = [];
  form.examples.splice(idx, 1);
  fetchDetail()
}

// 删除题目逻辑
const handleDelete = () => {
  ElMessageBox.confirm('确定要永久删除这道题目吗？', '危险操作', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      // 此处调用你的删除 API
      await deleteProblemApi(problemId!);
      ElMessage.success('题目已删除');
      router.push('/problem/ProblemView');
    } catch (e) {
      ElMessage.error('删除失败');
    }
  });
  fetchDetail()
};

const submitEdit = async (id: string) => {
  const payload: ProblemUpdateIn = {};

  if (form.title !== origin.title)
    payload.title = form.title;

  if (form.description !== origin.description)
    payload.description = form.description;

  if (form.input_description !== origin.input_description)
    payload.input_description = form.input_description;

  if (form.output_description !== origin.output_description)
    payload.output_description = form.output_description;

  if (form.analysis !== origin.analysis)
    payload.analysis = form.analysis;

  if (form.is_public !== origin.is_public)
    payload.is_public = form.is_public;

  if (form.time_limit !== origin.time_limit)
    payload.time_limit = form.time_limit;

  if (form.memory_limit !== origin.memory_limit)
    payload.memory_limit = form.memory_limit;

  if (form.difficulty !== origin.difficulty)
    payload.difficulty = form.difficulty;

  // 补充步骤状态字段的对比逻辑
  if (form.step_title_done !== origin.step_title_done)
    payload.step_title_done = form.step_title_done;

  if (form.step_limit_done !== origin.step_limit_done)
    payload.step_limit_done = form.step_limit_done;

  if (form.step_description_done !== origin.step_description_done)
    payload.step_description_done = form.step_description_done;

  if (form.step_input_description_done !== origin.step_input_description_done)
    payload.step_input_description_done = form.step_input_description_done;

  if (form.step_output_description_done !== origin.step_output_description_done)
    payload.step_output_description_done = form.step_output_description_done;

  if (form.step_example_done !== origin.step_example_done)
    payload.step_example_done = form.step_example_done;

  if (form.step_hint_done !== origin.step_hint_done)
    payload.step_hint_done = form.step_hint_done;

  if (form.step_testcase_done !== origin.step_testcase_done)
    payload.step_testcase_done = form.step_testcase_done;

  if (form.step_solution_done !== origin.step_solution_done)
    payload.step_solution_done = form.step_solution_done;
  if (JSON.stringify(form.tags) !== JSON.stringify(origin.tags))
    payload.tags = form.tags;

  if (JSON.stringify(form.examples) !== JSON.stringify(origin.examples))
    payload.examples = form.examples;

  if (!Object.keys(payload).length) {
    ElMessage.info('未修改任何内容');
  }
  else {
    await updateProblemApi(id, payload);
    Object.assign(origin, JSON.parse(JSON.stringify(form)));
    ElMessage.success('更新成功！');
    fetchDetail()
  }
};


const handleSubmit = async () => {
  if (!formRef.value) return;

  try {
    loading.value = true;

    await formRef.value.validate();
    await submitEdit(problemId!);

  } catch (err: any) {
    ElMessage.error(err?.message || '操作失败');
  } finally {
    loading.value = false;
  }
  fetchDetail()
};

const goBack = () => {
  router.push('/problem/problemView')
}
const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
</script>

<style scoped>
/* 保持原有样式不变 */
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
