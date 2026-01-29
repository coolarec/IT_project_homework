<script lang="ts" setup>
import { ElCard, ElTimeline, ElTimelineItem } from 'element-plus';
import { useRouter } from 'vue-router';

interface GuideStep {
  title: string;
  description: string;
  details?: string[];
}

const router = useRouter();

const problemSetterGuide: GuideStep[] = [
  {
    title: '1. 创建题目',
    description: '进入【问题管理->新增问题】，点击"新增题目"按钮',
    details: [
      '填写题目标题、时间限制、内存限制',
      '编写题目描述、输入输出格式说明',
      '添加样例输入输出'
    ]
  },
  {
    title: '2. 上传测试数据',
    description: '在【问题管理->问题管理】的"测试点"标签中上传测试数据',
    details: [
      '准备配对的 .in 和 .out 文件',
      '使用批量上传功能同时选择多个文件，如(data1.in, data1.out, data2.in, data2.out)',
      '系统会自动匹配文件名相同的输入输出对',
      '可下载所有测试点打包文件进行备份'
    ]
  },
  {
    title: '3. 编写题解',
    description: '在"题解"标签中发布标准题解',
    details: [
      '选择编程语言（Python/C++/Java）',
      '提供代码链接（推荐使用 paste.then.ac）',
      '用 Markdown 格式编写解题思路',
      '标记题解完成状态（未完成/创作中/已完成）'
    ]
  },
  {
    title: '4. 完善题目信息',
    description: '逐步完成九个出题步骤',
    details: [
      '题目标题 → 时空限制 → 题目描述',
      '输入描述 → 输出描述 → 测试样例',
      '提示分析 → 测试点 → 标准题解',
      '每个步骤都有进度圆点标识（灰/黄/绿）'
    ]
  },
  {
    title: '5. 题目审核与发布',
    description: '完成所有必要步骤后，题目可被关联到比赛',
    details: [
      '确保所有关键信息已填写完整',
      '检查测试数据的正确性和覆盖度',
      '将题目关联到具体竞赛'
    ]
  }
];

const contestCreatorGuide: GuideStep[] = [
  {
    title: '1. 创建用户组',
    description: '进入【竞赛管理->用户组管理】，点击"新增用户组"，一个用户组可以对应多场私有比赛，除管理员外其他账号仅能查看所在用户组下的比赛',
    details: [
      '填写用户组标题和详细描述',
      '编辑用户组成员（仅创建者可编辑）',
    ]
  },
  {
    title: '2. 创建比赛',
    description: '进入【竞赛管理->比赛列表】，点击"新增比赛"',
    details: [
      '填写比赛标题和详细描述',
      '设置比赛起止时间',
      '选择比赛类型：公开赛或私有赛',
      '私有赛需指定允许参与的用户组'
    ]
  },
  {
    title: '3. 添加题目占位',
    description: '在【竞赛管理->比赛列表】页点击操作栏的题目可进入竞赛详情页，为比赛添加题目占位槽',
    details: [
      '点击"添加题目占位"按钮',
      '设置题目名称',
      '填写题目简要描述或知识点',
      '设置排序顺序和标识颜色'
    ]
  },
  {
    title: '4. 关联真实题目',
    description: '将题库中的题目绑定到占位槽',
    details: [
      '点击"关联题目"按钮',
      '使用搜索功能查找题库中的题目',
      '选择合适的题目进行绑定',
      '系统会自动同步题目的准备进度'
    ]
  },
  {
    title: '5. 查看题目详细信息',
    description: '通过可视化进度条跟踪每道题的准备情况，点击题目名称可跳转到题目编辑器进行修改',
    details: [
      '九个圆点代表题目的九个准备步骤',
      '灰色 = 未开始，黄色 = 进行中，绿色 = 已完成',
      '点击题目名称可跳转到题目编辑器',
      '实时查看所有题目的整体进度'
    ]
  },
  {
    title: '5. 管理测试点和题解',
    description: '在比赛详情中直接管理关联题目的内容',
    details: [
      '点击"测试点"按钮查看和管理测试数据',
      '点击"题解"按钮查看标准题解，点击负责可以复制markdown内容',
      '可以在抽屉中快速编辑和完善内容',
      '确保比赛开始前所有题目准备就绪'
    ]
  }
];
</script>

<template>
  <div class="p-6 min-h-screen">
    <!-- 页面标题 -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold mb-2">📚 平台使用指南</h1>
      <p class="text-gray-600">欢迎使用题目与比赛管理系统，根据您的角色选择对应的操作指南</p>
    </div>

    <!-- 两栏布局 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 左栏：出题人指南 -->
      <el-card shadow="hover" class="rounded-xl border-none">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="text-2xl">✍️</span>
              <div>
                <h2 class="text-xl font-bold text-blue-600">出题人操作指南</h2>
                <p class="text-xs text-gray-500 mt-1">Problem Setter Guide</p>
              </div>
            </div>
          </div>
        </template>

        <el-timeline>
          <el-timeline-item v-for="(step, index) in problemSetterGuide" :key="index"
            :color="index === 0 ? '#409EFF' : '#67C23A'" :size="index === 0 ? 'large' : 'normal'">
            <div class="pb-4">
              <h3 class="text-lg font-bold mb-2">{{ step.title }}</h3>
              <p class="text-gray-700 mb-3">{{ step.description }}</p>
              <ul v-if="step.details" class="space-y-2 ml-4">
                <li v-for="(detail, idx) in step.details" :key="idx" class="text-sm text-gray-600 flex items-start">
                  <span class="text-blue-500 mr-2">▸</span>
                  <span>{{ detail }}</span>
                </li>
              </ul>
            </div>
          </el-timeline-item>
        </el-timeline>

        <div class="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-100">
          <p class="text-sm text-blue-800">
            <strong>💡 提示：</strong>
            所有题目数据不会自动保存，建议在完成题目时及时保存。需要帮助时可联系系统管理员（3187170085）。
          </p>
        </div>
      </el-card>

      <!-- 右栏：比赛创建者指南 -->
      <el-card shadow="hover" class="rounded-xl border-none">
        <template #header>
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span class="text-2xl">🏆</span>
              <div>
                <h2 class="text-xl font-bold text-green-600">比赛创建者操作指南</h2>
                <p class="text-xs text-gray-500 mt-1">Contest Creator Guide</p>
              </div>
            </div>
          </div>
        </template>

        <el-timeline>
          <el-timeline-item v-for="(step, index) in contestCreatorGuide" :key="index"
            :color="index === 0 ? '#67C23A' : '#409EFF'" :size="index === 0 ? 'large' : 'normal'">
            <div class="pb-4">
              <h3 class="text-lg font-bold mb-2">{{ step.title }}</h3>
              <p class="text-gray-700 mb-3">{{ step.description }}</p>
              <ul v-if="step.details" class="space-y-2 ml-4">
                <li v-for="(detail, idx) in step.details" :key="idx" class="text-sm text-gray-600 flex items-start">
                  <span class="text-green-500 mr-2">▸</span>
                  <span>{{ detail }}</span>
                </li>
              </ul>
            </div>
          </el-timeline-item>
        </el-timeline>

        <div class="mt-6 p-4 bg-green-50 rounded-lg border border-green-100">
          <p class="text-sm text-green-800">
            <strong>💡 提示：</strong>
            建议在比赛开始前 1-2 天完成所有题目的准备和测试。私有比赛需要提前配置好参赛用户组。
          </p>
        </div>
      </el-card>
    </div>

    <!-- 底部快速链接 -->
    <div class="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <el-card shadow="hover" class="text-center cursor-pointer hover:border-yellow-400 transition-all hover:shadow-xl" @click="router.push('/problem/problemCreate')">
        <div class="py-2">
          <div class="text-3xl mb-2">✏️</div>
          <h3 class="font-bold mb-1">新增题目</h3>
          <p class="text-xs text-gray-500">创建新的题目</p>
        </div>
      </el-card>

      <el-card shadow="hover" class="text-center cursor-pointer hover:border-blue-400 transition-all hover:shadow-xl" @click="router.push('/problem/problemView')">
        <div class="py-2">
          <div class="text-3xl mb-2">📝</div>
          <h3 class="font-bold mb-1">题库管理</h3>
          <p class="text-xs text-gray-500">浏览和编辑题目</p>
        </div>
      </el-card>

      <el-card shadow="hover" class="text-center cursor-pointer hover:border-purple-400 transition-all hover:shadow-xl" @click="router.push('/contest/userGroup')">
        <div class="py-2">
          <div class="text-3xl mb-2">👥</div>
          <h3 class="font-bold mb-1">用户组管理</h3>
          <p class="text-xs text-gray-500">配置权限和小组</p>
        </div>
      </el-card>

      <el-card shadow="hover" class="text-center cursor-pointer hover:border-green-400 transition-all hover:shadow-xl" @click="router.push('/contest/contestView')">
        <div class="py-2">
          <div class="text-3xl mb-2">🏆</div>
          <h3 class="font-bold mb-1">比赛管理</h3>
          <p class="text-xs text-gray-500">创建和管理竞赛</p>
        </div>
      </el-card>

    </div>
  </div>
</template>
