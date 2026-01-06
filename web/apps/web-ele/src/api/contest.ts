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
  status: number;
  contest_start_time: string;
  contest_end_time: string;
  creator_name?: string;
}

// 竞赛详情 (对应 ContestDetailOut)
export interface ContestDetail extends ContestListItem {
  prepare_start_time: string;
  prepare_end_time: string;
  notice: string;
  privite_permission: number; // 沿用后端拼写错误
  freeze_time: number;
  created_at: string;
  updated_at: string;
  creator_id: string;
  dept_id?: string;
  problems: ContestProblemItem[];
  virtual_problems: VirtualProblem[];
}

/**
 * --- API 输入模型 (Input/Payload Interfaces) ---
 */

export interface ContestCreateInput {
  title: string;
  prepare_start_time: string;
  prepare_end_time: string;
  contest_start_time: string;
  contest_end_time: string;
  notice?: string;
  status?: number;
  privite_permission?: number;
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

/** 获取竞赛详情 (含题目和虚拟题) */
export function getContestDetailApi(id: string) {
  return requestClient.get<ContestDetail>(`/api/contest/contests/${id}`);
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
 * --- 竞赛题目关联处理 ---
 */

/** 向竞赛添加题目 */
export function addProblemToContestApi(data: ContestProblemIn) {
  return requestClient.post<{ id: string }>('/api/contest/contest-problems', data);
}

/** 从竞赛中移除题目 */
export function removeProblemFromContestApi(id: string) {
  return requestClient.delete<{ id: string }>(`/api/contest/contest-problems/${id}`);
}

/**
 * --- 虚拟题目处理 (VirtualProblem) ---
 */

/** 创建虚拟题目 */
export function createVirtualProblemApi(data: VirtualProblemIn) {
  return requestClient.post<{ id: string }>('/api/contest/virtual-problems', data);
}

/** 虚拟题目转正 (绑定真实题目) */
export function bindVirtualProblemApi(id: string, data: VirtualProblemBindIn) {
  return requestClient.patch<{ id: string }>(`/api/contest/virtual-problems/${id}/bind`, data);
}
