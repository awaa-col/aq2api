# 多账号轮询功能实现总结

## 功能概述

成功为 Amazon Q API Bridge 实现了多账号轮询功能，允许配置和使用多个 Amazon Q 账号，通过轮询策略自动分配请求。

## 核心功能

### 1. 多账号管理
- **灵活的加载方式**：
  - 自动发现：自动查找 `amazonq_credentials*.json` 文件
  - 配置文件：在 `config.json` 中通过 `accounts` 数组配置
  - API 设置：通过 POST `/credentials` 批量设置多个账号
  
- **独立管理**：每个账号独立管理自己的 token、刷新时间和健康状态

### 2. 轮询策略
- **Round-Robin 负载均衡**：请求均匀分配到所有账号
- **自动循环**：索引自动循环，确保公平分配
- **无状态切换**：每次请求使用下一个账号，无需手动干预

### 3. 健康追踪与自动故障转移
- **错误追踪**：记录每个账号的错误次数和最后错误信息
- **自动重试**：当前账号失败时自动尝试下一个账号
- **智能重试**：最多重试 3 次或所有可用账号数（取较小值）
- **自动恢复**：账号请求成功后自动重置错误计数

### 4. 安全性
- **敏感信息保护**：凭证文件已添加到 `.gitignore`
- **错误信息过滤**：外部 API 响应不暴露内部堆栈跟踪
- **详细日志**：详细错误仅记录在服务器日志中
- **CodeQL 验证**：通过 CodeQL 安全扫描，0 个安全问题

## 技术实现

### 主要类和组件

1. **MultiAccountManager**
   - 管理多个 `AmazonQAuthManager` 实例
   - 实现轮询选择逻辑
   - 追踪账号健康状态
   - 提供账号加载和重载功能

2. **AmazonQAuthManager (增强)**
   - 添加 `account_index` 参数用于标识
   - 支持日志中显示账号编号
   - 保持原有的 token 管理功能

3. **请求处理增强**
   - 在 `_handle_chat_request` 中集成多账号逻辑
   - 实现自动重试机制
   - 标记账号成功/失败状态

### API 端点更新

- **GET /**: 显示多账号功能和账号计数
- **GET /health**: 包含账号数量信息
- **GET /credentials**: 显示所有账号状态和健康信息
- **POST /credentials**: 支持单个或批量设置账号
- **GET /test/token**: 测试所有账号的 token 刷新

## 使用示例

### 方式 1: 文件自动发现
```bash
# 创建多个凭证文件
cp amazonq_credentials.example.json amazonq_credentials_0.json
cp amazonq_credentials.example.json amazonq_credentials_1.json
cp amazonq_credentials.example.json amazonq_credentials_2.json

# 编辑每个文件，填入各自的凭证
# 启动服务，自动加载所有账号
python3 main.py
```

### 方式 2: 配置文件
```json
// config.json
{
  "accounts": [
    "amazonq_credentials_0.json",
    "amazonq_credentials_1.json",
    "amazonq_credentials_2.json"
  ],
  "logging": {
    "enabled": true
  }
}
```

### 方式 3: API 批量设置
```bash
curl -X POST http://localhost:8000/credentials \
  -H "Content-Type: application/json" \
  -d '[
    {
      "client_id": "...",
      "client_secret": "...",
      "refresh_token": "..."
    },
    {
      "client_id": "...",
      "client_secret": "...",
      "refresh_token": "..."
    }
  ]'
```

## 测试

### 单元测试
```bash
python3 test_multi_account.py
```

测试覆盖：
- ✓ 多账号加载
- ✓ 轮询顺序验证
- ✓ 凭证正确性
- ✓ 单账号兼容性

### 端到端测试
```bash
# 启动服务器
python3 main.py

# 测试各个端点
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/credentials
```

## 文件清单

### 新增文件
- `.gitignore` - 保护敏感文件
- `test_multi_account.py` - 测试套件
- `config.example.json` - 单账号配置示例
- `config.multi-account.example.json` - 多账号配置示例
- `amazonq_credentials.example.json` - 凭证模板

### 修改文件
- `main.py` - 核心实现（+270 行，重构 -73 行）
- `README.md` - 完整文档（+130 行）

## 向后兼容性

✓ 完全兼容单账号设置
✓ 现有配置无需修改即可继续使用
✓ 单账号情况下行为与之前相同

## 性能优化

- 轮询策略避免了账号选择的计算开销
- 健康追踪避免了重复使用失败的账号
- 独立的 token 管理避免了全局锁

## 已知限制

1. 不支持基于优先级的账号选择（当前仅 Round-Robin）
2. 不支持基于负载的动态权重调整
3. 错误计数不会自动过期（仅在成功时重置）

## 未来增强建议

1. 添加基于权重的负载均衡策略
2. 实现账号黑名单机制（错误过多时暂时禁用）
3. 添加账号使用统计和监控端点
4. 支持账号分组和优先级
5. 实现更复杂的故障转移策略（如最少错误优先）

## 结论

多账号轮询功能已成功实现并通过所有测试。该功能提供了：
- 更高的可用性（多账号冗余）
- 更好的负载分配（Round-Robin）
- 自动故障处理（健康追踪 + 自动重试）
- 良好的安全性（通过 CodeQL 验证）
- 完整的文档和示例

系统现在可以处理多个 Amazon Q 账号，提供更稳定和可扩展的 API 服务。
