# PHASE_2_REMAINING_GAPS_AND_COMPLETION_PLAN

## 结论
当前系统已经明显超过“最小闭环”，但还没有达到“完整上线版”。
本文件的目标是把剩余缺口、完成路径、收口标准一次性写清。

---

## 一、当前已完成基础
### 已完成并已验证
1. Phase 1 最小闭环
   - 4 个 skill
   - task / resume / next-task / changelog / event log / safe write / risk gate
2. next-task v2
   - priority / dependency / override 已实现并验证
3. canonical state
   - state store / index / next-task state 已落地
   - task / resume / TASKS / NEXT_TASK 视图已开始由 state store 渲染
4. memory retrieval
   - retrieval order 已固定
   - retrieve_context 已实现
   - degraded / normal fallback 已验证
   - read_project_context 已开始接入统一 retrieval
5. risk policy
   - policy evaluator 已实现
   - allow / require-confirmation / reject 已验证
   - check_risk_level 已开始调用 policy evaluator
6. Phase 2 mainline integration
   - 当前统一检查已 PASS

---

## 二、剩余缺口

### Gap 1：next-task v2 尚未彻底替代旧决议链
#### 现状
- v2 已存在并已桥接到主链路
- 旧 `decide_next_task.py` 仍保留且部分链路仍兼容回退

#### 缺口
- bulk / resume / readiness / audit 仍未统一依赖 v2
- 旧链路仍可能被继续使用

#### 完成标准
- `decide_next_task_v2.py` 成为默认主决议器
- 旧决议脚本降级为 fallback 或移除
- 所有 next-task 输出统一来自 canonical state

---

### Gap 2：canonical state 尚未成为唯一事实源
#### 现状
- update 主链路已写入 state store
- task / resume / TASKS / NEXT_TASK 已开始由 state 渲染

#### 缺口
- 仍存在 markdown-first 反向解析逻辑
- 部分脚本仍把 markdown 当事实源而不是视图
- audit / healthcheck / completeness / readiness 尚未全面改成 state-first

#### 完成标准
- 结构化 state 为唯一 source of truth
- markdown 仅保留为视图层
- 旧 markdown-first 解析被清理或降级为 fallback

---

### Gap 3：memory retrieval 仍未全局接管所有读取入口
#### 现状
- `read_project_context.py` 已接入 `retrieve_context.py`
- `resume_task.py` / `resume_many_tasks.py` 已接 retrieval
- `system_healthcheck.py` 已接 retrieval
- retrieval priority check 已接回统一主检查

#### 缺口
- delivery / readiness / 其余历史读取入口仍未统一走 retrieval protocol
- retrieval 输出标准虽然已明显收敛，但还未彻底统一到所有入口

#### 完成标准
- 主要读取脚本统一使用 retrieval order
- facts > task state > summary > chat 成为全系统默认读取协议
- retrieval 行为在主检查与端到端验证里持续可证

---

### Gap 4：risk policy 已配置化，但还未完全收口为完整策略系统
#### 现状
- `risk_policy.json` 已落地
- `evaluate_risk_policy.py` 已改为读取外置配置
- 已支持 `action + scope + target + context` 细粒度判定
- 已完成基础矩阵、细粒度矩阵与一致性检查
- risk policy 一致性已接回统一主检查

#### 缺口
- `check_risk_level.py` 旧入口虽已依赖 policy evaluator，但更高层链路对 risk 结果的复用还不够完整
- 风险结果进入审计 / readiness / delivery 等链路的复用范围还可继续扩大

#### 完成标准
- policy 配置化与细粒度规则稳定收口
- 风险结果能被更多主链路检查与审计链复用
- 发布版同步后仍保持兼容与可验证

---

### Gap 5：主链路检查已开始一致性化，但还没达到完整统一验收口
#### 现状
- mainline check 已 PASS
- 已不再只是文件存在性检查
- 已开始校验：
  - state/view 一致性
  - next-task 一致性
  - retrieval 行为摘要
  - risk policy 一致性
  - risk matrix / granularity 关键 case
- 已完成三条端到端验证：
  - `PHASE2_SINGLE_TASK_E2E_RESULT.md = PASS`
  - `PHASE2_BULK_E2E_RESULT.md = PASS`
  - `PHASE2_RESUME_E2E_RESULT.md = PASS`

#### 缺口
- 主检查覆盖面仍可继续扩大
- 还缺发布版侧的等价验收
- 统一验收口还没有完全延伸到 release 同步后的检查链

#### 完成标准
- 主检查成为真正统一验收入口
- state / view / next-task / retrieval / risk policy 均有稳定语义断言
- 发布版侧也完成至少一轮完整端到端验证

---

## 三、上线版收口标准
只要以下全部满足，才算“完整上线版”：

### A. 调度
- next-task v2 成为唯一默认决议链
- priority / dependency / override 全部进入主链路
- bulk / resume / update / checks 统一读取 next-task v2 输出

### B. 状态
- canonical state 成为唯一事实源
- task / resume / TASKS / NEXT_TASK 全部由 state 渲染
- markdown-first 反向解析不再是主路径

### C. 读取
- retrieval protocol 接管主要上下文读取入口
- facts > task state > summary > chat 全系统成立
- degraded fallback 可验证

### D. 风控
- risk policy 替换旧动作枚举逻辑
- policy 支持 action / scope / target / context 粒度判断
- 风险门控结果能被日志/审计链复用

### E. 检查
- 存在性检查 + 一致性检查都通过
- 至少有一轮完整 mainline verification

### F. 交付
- 文档、脚本、状态结构、检查链路一致
- 发布版可重新收口并通过 readiness / healthcheck / delivery checks

---

## 四、推荐完成顺序
1. next-task v2 全量替代旧链路
2. canonical state 全面接管 facts/state/view 生成
3. retrieval 接管主要读取入口
4. risk policy 配置化与细粒度化
5. 一致性检查补齐
6. 发布版再收口、再验证、再推送
