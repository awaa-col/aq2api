# aq2api


> 通过群之前佬友提供的python脚本 `info.py` 获取凭证信息

## 多账号轮询功能

本项目支持多账号轮询，可以配置多个 Amazon Q 账号，系统会自动在账号之间轮询分配请求，提高可用性和请求限制。

### 配置方式

#### 方式 1: 多个凭证文件

创建多个凭证文件：
- `amazonq_credentials.json` (账号 0)
- `amazonq_credentials_0.json` (账号 0，可选)
- `amazonq_credentials_1.json` (账号 1)
- `amazonq_credentials_2.json` (账号 2)
- ...

系统会自动发现并加载所有凭证文件。

#### 方式 2: 在 config.json 中配置

在 `config.json` 中添加 `accounts` 数组：

```json
{
  "accounts": [
    "amazonq_credentials.json",
    "amazonq_credentials_1.json",
    {
      "client_id": "your_client_id",
      "client_secret": "your_client_secret",
      "refresh_token": "your_refresh_token",
      "access_token": "will_be_auto_updated",
      "region": "us-east-1"
    }
  ],
  "logging": {
    "enabled": true,
    "level": "INFO"
  }
}
```

#### 方式 3: 通过 API 批量设置

```bash
curl -X POST http://localhost:8000/credentials \
  -H "Content-Type: application/json" \
  -d '[
    {
      "client_id": "account1_client_id",
      "client_secret": "account1_client_secret",
      "refresh_token": "account1_refresh_token"
    },
    {
      "client_id": "account2_client_id",
      "client_secret": "account2_client_secret",
      "refresh_token": "account2_refresh_token"
    }
  ]'
```

### 轮询策略

系统使用**轮询（Round-Robin）**策略在多个账号之间分配请求：
1. 每次收到请求时，选择下一个账号
2. 账号索引自动循环，均匀分配负载
3. 所有账号的 token 独立管理和刷新

### 自动故障转移

系统支持账号健康追踪和自动故障转移：
- **健康追踪**: 记录每个账号的错误次数和最后错误信息
- **自动重试**: 如果当前账号请求失败，自动尝试下一个账号
- **最多重试**: 默认最多重试 3 次或所有可用账号数（取较小值）
- **恢复检测**: 账号请求成功后自动重置错误计数

### 查看账号状态

```bash
curl http://localhost:8000/credentials
```

返回示例：
```json
{
  "account_count": 3,
  "current_index": 1,
  "accounts": [
    {
      "account_index": 0,
      "credentials_file": "amazonq_credentials.json",
      "has_credentials": true,
      "has_access_token": true,
      "token_expiry": "2025-11-08T17:00:00",
      "health": {
        "error_count": 0,
        "last_error": null
      }
    },
    {
      "account_index": 1,
      "credentials_file": "amazonq_credentials_1.json",
      "has_credentials": true,
      "has_access_token": true,
      "token_expiry": "2025-11-08T17:05:00",
      "health": {
        "error_count": 2,
        "last_error": "Token expired"
      }
    }
  ]
}
```

### 测试多账号功能

运行测试脚本验证多账号轮询功能：

```bash
python3 test_multi_account.py
```

## 凭证文件格式

`amazonq_credentials.json` 需要包含：

```json
{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "refresh_token": "your_refresh_token",
  "access_token": "will_be_auto_updated",
  "region": "us-east-1"
}
```

参考示例文件：`amazonq_credentials.example.json`

## 配置文件

创建 `config.json` 文件来自定义服务行为。

### 示例配置文件

- **单账号**: 参考 `config.example.json`
- **多账号**: 参考 `config.multi-account.example.json`

### 默认配置

```json
{
  "logging": {
    "enabled": true,
    "level": "INFO",
    "log_requests": true,
    "log_responses": true,
    "log_token_refresh": true,
    "max_log_length": 500
  },
  "performance": {
    "stream_chunk_size": 1024,
    "buffer_max_size": 10240,
    "token_refresh_margin_seconds": 300
  }
}
```

## 配置项说明

### logging 日志配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enabled` | boolean | `true` | 是否启用日志 |
| `level` | string | `"INFO"` | 日志级别: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"` |
| `log_requests` | boolean | `true` | 是否记录请求日志 |
| `log_responses` | boolean | `true` | 是否记录响应日志 |
| `log_token_refresh` | boolean | `true` | 是否记录 token 刷新日志 |
| `max_log_length` | integer | `500` | 日志内容最大长度（字符） |

### performance 性能配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `stream_chunk_size` | integer | `1024` | 流式读取的块大小（字节） |
| `buffer_max_size` | integer | `10240` | 缓冲区最大大小（字符） |
| `token_refresh_margin_seconds` | integer | `300` | Token 过期前多少秒刷新 |