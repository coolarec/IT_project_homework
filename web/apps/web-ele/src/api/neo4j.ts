import { requestClient } from '#/api/request';

/** 榜单单行预览模型 */
export interface ProblemResult {
  status: string;   // AC 或 FB
  attempts: number; // 尝试发数
  time: number;     // 罚时(分钟)
}

export interface AnalysisItem {
  rank: number | null;
  medal: string;
  organization: string;
  name: string;      // 队伍名
  members: string[];
  score: number;
  penalty: number;
  problems: Record<string, ProblemResult>;
}

/** 1. 预览 Excel */
export function previewAnalysisApi(file: File) {
  const fd = new FormData();
  // 核心：这个 'file' 字符串必须和后端 Python 函数里的变量名 'file' 完全一致
  fd.append('file', file);

  return requestClient.post<any[]>('/api/neo4j/preview', fd, {
    // 覆盖拦截器的默认行为
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}

/** 2. 持久化存入 Neo4j */
export function saveAnalysisApi(contestName: string, items: AnalysisItem[]) {
  return requestClient.post('/api/neo4j/save', {
    contest_name: contestName,
    items: items
  });
}

/**
 * 获取仪表盘深度分析数据
 * @param contestName 可选，如果不传则返回全局统计数据
 */
export function getDashboardApi(contestName?: string) {
  return requestClient.get<any>('/api/neo4j/dashboard', {
    // 这里的参数名必须和后端 python 函数的 contest_name 一致
    params: { contest_name: contestName || null }
  });
}

/**
 * 获取所有已上传的比赛列表
 */
export function getUploadedContestsApi() {
  return requestClient.get<string[]>('/api/neo4j/contests');
}
