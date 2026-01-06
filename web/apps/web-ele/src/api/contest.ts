import { requestClient } from '#/api/request';

/**
 * --- 基础模型定义 (Model Interfaces) ---
 */

export interface UserGroup {
  id: string;
  name: string;
  description?: string;
  creator_id: string;
  created_at: string;
  member_count: number;
}

export interface UserGroupIn {
  name: string;
  description?: string;
}

export interface ContestProblemItem {
  id: string;
  problem_id: string;
  title?: string; // 关联题目的原始标题
  order: number;
  color: string;
  alias: string;
}

export interface VirtualProblem {
  id: string;
  contest_id: string;
  description: string;
  author_id: string;
  created_at: string;
  real_problem_id?: string;
}

/**
 * --- 竞赛模型 (Contest Interfaces) ---
 */

// 竞赛列表项 (对应 ContestListOut)
export interface ContestListItem {
  id: string;
  title: string;
  contest_start_time: string;
  contest_end_time: string;
  creator_name?: string;
  is_public:boolean
}

// 竞赛详情 (对应 ContestDetailOut)
export interface ContestDetail extends ContestListItem {
  notice: string;
  is_public: boolean;
  freeze_time: number;
  created_at: string;
  updated_at: string;
  creator_id: string;
  virtual_problems: VirtualProblem[];
}



/**
 * --- API 输入模型 (Input/Payload Interfaces) ---
 */

export interface ContestCreateInput {
  title: string;
  contest_start_time: string;
  contest_end_time: string;
  description:string;
  notice?: string;
  is_public: boolean;
  freeze_time?: number;
  allowed_group_ids?: string[]; // 允许访问的用户组UUID列表
}

export interface ContestUpdateInput extends Partial<ContestCreateInput> {}

export interface ContestProblemIn {
  problem_id: string;
  order: number;
  color: string;
  alias: string;
}

export interface VirtualProblemIn {
  description: string;
}

export interface VirtualProblemBindIn {
  real_problem_id: string;
}

export interface VirtualProblemOut {
  id: string
  name: string
  description: string
  order: number
  color: string
  is_bound: boolean
  real_problem_id?: string | null
  real_problem_title?: string | null

  step_title_done: number
  step_limit_done: number
  step_description_done: number
  step_input_description_done: number
  step_output_description_done: number
  step_example_done: number
  step_hint_done: number
  step_testcase_done: number
  step_solution_done: number
}


export interface ContestDetailOutWithVp {
  id: string
  title: string
  description: string
  contest_start_time: string
  contest_end_time: string
  is_public: boolean
  creator_name: string
  virtual_problems: VirtualProblemOut[]
}

export interface VirtualProblemIn {
  name: string
  description: string
  order?: number
  color?: string
}


/**
 * --- API 请求函数 (API Methods) ---
 */

/**
 * --- 用户组相关处理 (UserGroup) ---
 */

/** 获取用户组列表 */
export function getGroupListApi(params?: { name?: string }) {
  // 如果 params 存在且 params.name 有值，则传递 params，否则传空对象或 undefined
  const requestConfig = params?.name ? { params } : {};
  return requestClient.get<UserGroup[]>('/api/contest/groups', requestConfig);
}

/** 创建用户组 */
export function createGroupApi(data: UserGroupIn) {
  return requestClient.post<UserGroup>('/api/contest/groups', data);
}

/** 更新用户组信息 */
export function updateGroupApi(id: string, data: UserGroupIn) {
  return requestClient.patch<UserGroup>(`/api/contest/groups/${id}`, data);
}

/** 删除用户组 */
export function deleteGroupApi(id: string) {
  return requestClient.delete<UserGroup>(`/api/contest/groups/${id}`);
}

/** 向用户组批量增加成员 */
export function addGroupMembersApi(id: string, userIds: string[]) {
  return requestClient.post<UserGroup>(`/api/contest/groups/${id}/members`, {
    user_ids: userIds
  });
}

/** 从用户组移除成员 */
export function removeGroupMembersApi(id: string, userIds: string[]) {
  return requestClient.delete<UserGroup>(`/api/contest/groups/${id}/members`, {
    data: { user_ids: userIds } // 根据请求库约定，delete的body通常放在data里
  });
}

/**
 * --- 竞赛相关处理 (Contest) ---
 */

/** 获取竞赛列表 (带权限过滤) */
export function getContestListApi(params?: { keyword?: string }) {
  const query: Record<string, any> = {};
  if (params?.keyword?.trim()) {
    query.keyword = params.keyword.trim();
  }
  return requestClient.get<ContestListItem[]>('/api/contest/contests', {
    params: query
  });
}

/** 获取竞赛详情 */
export function getContestDetailApi(id: string) {
  return requestClient.get<ContestDetailOutWithVp>(`/api/contest/contests/${id}`);
}

/** 创建竞赛 */
export function createContestApi(data: ContestCreateInput) {
  return requestClient.post<ContestDetail>('/api/contest/contests', data);
}

/** 更新竞赛 */
export function updateContestApi(id: string, data: ContestUpdateInput) {
  return requestClient.patch<ContestDetail>(`/api/contest/contests/${id}`, data);
}

/** 删除竞赛 */
export function deleteContestApi(id: string) {
  return requestClient.delete<ContestDetail>(`/api/contest/contests/${id}`);
}


/**
 * --- 虚拟题目处理 (VirtualProblem) ---
 */

export function getContestDetailVpApi(id: string) {
  return requestClient.get<any>(`/api/contest/contests-vp/${id}`);
}
/** 创建虚拟题目占位 */
export function createVirtualProblemApi(contestId: string, data: VirtualProblemIn) {
  return requestClient.post<{ id: string }>(`/api/contest/contests/${contestId}/virtual-problems`, data);
}

/** 更新虚拟题目属性 */
export function updateVirtualProblemApi(id: string, data: any) {
  return requestClient.patch<{ id: string }>(`/api/contest/virtual-problems/${id}`, data);
}

/** 虚拟题目绑定真实题目 */
export function bindVirtualProblemApi(id: string, data: { real_problem_id: string }) {
  return requestClient.patch<{ id: string }>(`/api/contest/virtual-problems/${id}/bind`, data);
}

/** 删除虚拟题目 */
export function deleteVirtualProblemApi(id: string) {
  return requestClient.delete<void>(`/api/contest/virtual-problems/${id}`);
}
