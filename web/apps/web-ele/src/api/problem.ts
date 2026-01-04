import { requestClient } from '#/api/request';

/**
 * --- 基础模型定义 (Model Interfaces) ---
 */

export interface Tag {
  id: number;
  name: string;
}

export interface TagIn {
  name: string;
}

export interface Example {
  id?: number;
  input_data: string;
  output_data: string;
}

export interface TestCase {
  id: number;
  input_filename?: string,
  input_file?: string; // 文件 URL 地址
  output_filename?: string,
  output_file?: string; //
  created_at: string;
  size: Number;
}

export interface Solution {
  id: number;
  language: string;
  code: string;
  description?: string;
  created_at: string;
}

/**
 * --- 题目模型 (Problem Interfaces) ---
 */

// 题目列表项 (对应 ProblemListOut)
export interface ProblemListItem {
  id: number;
  title: string;
  difficulty: number;
  is_public: boolean;
  created_at: string;
}

// 题目详情 (对应 ProblemDetailOut)
export interface ProblemDetail extends ProblemListItem {
  description: string;
  input_description: string;
  output_description: string;
  analysis?: string;
  tags: Tag[];
  examples: Example[];
  time_limit: number;
  memory_limit: number;
  step_title_done: number
  step_limit_done?: number
  step_description_done: number
  step_input_description_done: number
  step_output_description_done: number
  step_example_done: number
  step_hint_done: number
  step_testcase_done: number
  step_solution_done: number
}
/**
 * --- API 输入模型 (Input/Payload Interfaces) ---
 */

export interface ProblemCreateInput {
  title: string;
  description: string;
  input_description?: string;
  output_description?: string;
  analysis?: string;
  time_limit:number;
  memory_limit:number;
  difficulty: number;
  is_public: boolean;
  tags: Tag[];
  examples: Example[]; // 支持嵌套创建样例
  step_title_done: number
  step_limit_done?: number
  step_description_done: number
  step_input_description_done: number
  step_output_description_done: number
  step_example_done: number
  step_hint_done: number
  step_testcase_done: number
  step_solution_done: number
}

export interface ProblemStatusUpdate {
  step_title_done?: boolean | null
  step_description_done?: boolean | null
  step_input_description_done?: boolean | null
  step_output_description_done?: boolean | null
  step_example_done?: boolean | null
  step_hint_done?: boolean | null
  step_testcase_done?: boolean | null
  step_solution_done?: boolean | null
}

export interface ExampleIn {
  input_data: string;
  output_data: string;
}

export interface ProblemUpdateIn {
  title?: string;
  description?: string;
  input_description?: string;
  output_description?: string;
  analysis?: string;
  difficulty?: number;
  is_public?: boolean;
  time_limit?: number;
  memory_limit?: number;
  tags?: Tag[];
  examples?: ExampleIn[];
  step_title_done?: number
  step_limit_done?: number
  step_description_done?: number
  step_input_description_done?: number
  step_output_description_done?: number
  step_example_done?: number
  step_hint_done?: number
  step_testcase_done?: number
  step_solution_done?: number
}

export interface SolutionInput {
  language: string;
  code: string;
  description?: string;
}

/**
 * --- API 请求函数 (API Methods) ---
 */

/**
 * --- 题目相关逻辑处理(problem) ---
 */
/** 获取题目列表 (包含公开题和自己创建的题) */
export function getProblemListApi(params?: { keyword?: string }) {
  // 构建一个干净的请求对象
  const query: Record<string, any> = {};

  if (params?.keyword && params.keyword.trim() !== '') {
    query.keyword = params.keyword.trim();
  }

  return requestClient.get<ProblemListItem[]>('/api/problem/', {
    params: query
  });
}

/** 获取题目详情 */
export function getProblemDetailApi(id: number) {
  return requestClient.get<ProblemDetail>(`/api/problem/${id}`);
}

/** 创建新题目 */
export function createProblemApi(data: ProblemCreateInput) {
  return requestClient.post<ProblemDetail>('/api/problem/', data);
}

export function updateProblemApi(id: number,data: ProblemUpdateIn) {
  return requestClient.patch(`/api/problem/${id}`,data);
}

/**
 * --- 标签相关处理 (Tag) ---
 */


/** 获取所有标签 (用于下拉选择) */
export function getTagsApi() {
  return requestClient.get<Tag[]>('/api/problem/tags/all');
}
/** 增加新标签 */
export function createTagApi(data: TagIn) {
  return requestClient.post<Tag>(`/api/problem/tag/`, data);
}
export function deleteTagApi(id: number) {
  return requestClient.delete(`/api/problem/tag/${id}`);
}

/**
 * 上传测试用例
 * 注意：涉及文件上传，建议在组件内构建 FormData 传入
 */
export function uploadTestCaseApi(problemId: number, formData: FormData) {
  return requestClient.post<TestCase>(
    `/api/problem/${problemId}/testcase`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' }
    }
  );
}
/**
 * 删除测试用例
 */
export function deleteTestCaseApi(testCaseId: Number) {
  return requestClient.delete<TestCase>(`/api/problem/testcase/${testCaseId}`)
}
/**
 * 获取所有testcase
 */
export function getTestCaseApi(id: Number) {
  return requestClient.get<TestCase[]>(`/api/problem/${id}/testcases`)
}

/** 为指定题目发布题解 */
export function createSolutionApi(problemId: number, data: SolutionInput) {
  return requestClient.post<Solution>(`/api/problem/${problemId}/solutions`, data)
}
/** 获取指定题目的题解 */
export function getSolutionsApi(problem_id:number){
  return requestClient.get<Solution[]>(`/api/problem/${problem_id}/solutions`)
}
/** 删除某个题解 */
export function deleteSolutionApi(solution_id:number){
  return requestClient.delete<Solution>(`/api/problem/solution/${solution_id}`)
}
