# 加密货币合约分析交易系统配置指南

本文档详细介绍了系统配置文件的各个参数及其作用，帮助您根据自己的需求定制系统。

## 配置文件概述

系统的主要配置文件是`config.yaml`，使用YAML格式，包含以下主要部分：

- 交易所配置
- 交易对配置
- 时间周期配置
- 分析参数配置
- 信号生成参数
- 风险管理参数
- Telegram通知配置
- 日志配置
- 高级设置

## 详细配置说明

### 1. 交易所配置

```yaml
exchanges:
  gateio:
    api_key: "YOUR_API_KEY"
    secret_key: "YOUR_SECRET_KEY"
    use_testnet: true
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| api_key | 交易所API密钥 | - |
| secret_key | 交易所API密钥 | - |
| use_testnet | 是否使用测试网络 | true |

您可以配置多个交易所，系统将按顺序尝试连接。例如：

```yaml
exchanges:
  gateio:
    api_key: "GATE_API_KEY"
    secret_key: "GATE_SECRET_KEY"
  binance:
    api_key: "BINANCE_API_KEY"
    secret_key: "BINANCE_SECRET_KEY"
```

### 2. 交易对配置

```yaml
symbols:
  - "BTC/USDT"
  - "ETH/USDT"
  - "SOL/USDT"
```

这里列出您要分析的交易对。确保使用标准格式（基础货币/计价货币）。

### 3. 时间周期配置

```yaml
timeframes:
  - "1m"
  - "5m"
  - "15m"
  - "30m"
  - "1h"
  - "4h"
  - "1d"
```

设置您要分析的时间周期。支持的时间周期取决于您使用的交易所。

### 4. 分析参数配置

```yaml
analysis_params:
  # 均线参数
  ma_periods:
    - 5
    - 10
    - 20
    - 50
    - 100
    - 200
  
  # RSI参数
  rsi:
    period: 14
    overbought: 70
    oversold: 30
  
  # KDJ参数
  kdj:
    k_period: 9
    d_period: 3
    j_period: 3
  
  # MACD参数
  macd:
    fast_period: 12
    slow_period: 26
    signal_period: 9
  
  # 布林带参数
  bollinger:
    period: 20
    std_dev: 2
```

这部分配置技术指标的参数。您可以根据自己的交易策略调整这些值。

#### 均线参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| ma_periods | 计算移动平均线的周期列表 | [5, 10, 20, 50, 100, 200] |

#### RSI参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| period | RSI计算周期 | 14 |
| overbought | 超买阈值 | 70 |
| oversold | 超卖阈值 | 30 |

#### KDJ参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| k_period | K线计算周期 | 9 |
| d_period | D线计算周期 | 3 |
| j_period | J线计算周期 | 3 |

#### MACD参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| fast_period | 快线周期 | 12 |
| slow_period | 慢线周期 | 26 |
| signal_period | 信号线周期 | 9 |

#### 布林带参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| period | 计算周期 | 20 |
| std_dev | 标准差倍数 | 2 |

### 5. 信号生成参数

```yaml
signal_params:
  # 信号阈值
  thresholds:
    strong_buy: 80
    buy: 60
    neutral: 40
    sell: 20
    strong_sell: 0
  
  # 指标权重 (权重总和应为1)
  weights:
    trend: 0.3
    oscillators: 0.3
    volume: 0.2
    sentiment: 0.2
```

这部分配置信号生成的参数，包括各种信号的阈值和不同指标的权重。

#### 信号阈值

| 参数 | 说明 | 默认值 |
|------|------|--------|
| strong_buy | 强烈买入信号阈值 | 80 |
| buy | 买入信号阈值 | 60 |
| neutral | 中性区间上限 | 40 |
| sell | 卖出信号阈值 | 20 |
| strong_sell | 强烈卖出信号阈值 | 0 |

#### 指标权重

| 参数 | 说明 | 默认值 |
|------|------|--------|
| trend | 趋势指标权重 | 0.3 |
| oscillators | 震荡指标权重 | 0.3 |
| volume | 交易量指标权重 | 0.2 |
| sentiment | 市场情绪指标权重 | 0.2 |

注意：所有权重之和应为1。

### 6. 风险管理参数

```yaml
risk_management:
  max_position_size: 0.25
  max_leverage: 10
  min_risk_reward: 1.5
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| max_position_size | 最大仓位比例 (0-1) | 0.25 |
| max_leverage | 最大杠杆倍数 | 10 |
| min_risk_reward | 最小风险回报比 | 1.5 |

### 7. Telegram通知配置

```yaml
telegram:
  token: "YOUR_BOT_TOKEN"
  chat_id: "YOUR_CHAT_ID"
  enabled: false
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| token | Telegram机器人Token | - |
| chat_id | 接收消息的聊天ID | - |
| enabled | 是否启用Telegram通知 | false |

### 8. 日志配置

```yaml
logging:
  level: "INFO"
  file: "crypto_bot.log"
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| level | 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO |
| file | 日志文件名 | crypto_bot.log |

### 9. 高级设置

```yaml
advanced:
  data_update_interval: 60
  max_lookback_bars: 500
  enable_cloud_sync: false
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| data_update_interval | 数据更新间隔(秒) | 60 |
| max_lookback_bars | 最大回溯K线数量 | 500 |
| enable_cloud_sync | 是否启用云同步 | false |

## 配置示例

以下是一个完整的配置文件示例，针对比特币和以太坊的4小时和1天图进行分析：

```yaml
# 交易所配置
exchanges:
  gateio:
    api_key: "YOUR_API_KEY"
    secret_key: "YOUR_SECRET_KEY"
    use_testnet: true

# 交易对配置
symbols:
  - "BTC/USDT"
  - "ETH/USDT"

# 时间周期配置
timeframes:
  - "4h"
  - "1d"

# 分析参数配置
analysis_params:
  ma_periods:
    - 10
    - 20
    - 50
    - 200
  rsi:
    period: 14
    overbought: 70
    oversold: 30
  macd:
    fast_period: 12
    slow_period: 26
    signal_period: 9
  bollinger:
    period: 20
    std_dev: 2

# 信号生成参数
signal_params:
  thresholds:
    strong_buy: 75
    buy: 60
    neutral: 40
    sell: 25
    strong_sell: 0
  weights:
    trend: 0.4
    oscillators: 0.3
    volume: 0.1
    sentiment: 0.2

# 风险管理参数
risk_management:
  max_position_size: 0.2
  max_leverage: 5
  min_risk_reward: 2.0

# Telegram通知配置
telegram:
  token: "YOUR_BOT_TOKEN"
  chat_id: "YOUR_CHAT_ID"
  enabled: true

# 日志配置
logging:
  level: "INFO"
  file: "crypto_bot.log"

# 高级设置
advanced:
  data_update_interval: 60
  max_lookback_bars: 500
  enable_cloud_sync: false
```

## 配置建议

### 初学者配置

如果您是加密货币交易的初学者，建议使用以下配置：

- 仅分析主流币种（BTC/USDT, ETH/USDT）
- 使用较长时间周期（4h, 1d）避免短期噪音
- 降低最大仓位比例（0.1-0.15）
- 降低最大杠杆倍数（3-5）
- 提高最小风险回报比（2.5-3.0）

### 中级交易者配置

中级交易者可以考虑：

- 扩展分析币种范围
- 添加中等时间周期（1h, 4h）
- 适度增加最大仓位（0.15-0.25）
- 根据市场情况调整杠杆（5-10）
- 降低风险回报比要求（1.5-2.0）

### 高级交易者配置

高级交易者可以更加个性化：

- 调整技术指标参数以适应个人交易风格
- 修改指标权重优化信号质量
- 自定义信号阈值适应不同市场环境

## 配置调优

系统参数的调优是一个持续过程，建议：

1. 保存初始配置作为基准
2. 每次只修改少量参数
3. 记录参数变化对信号质量的影响
4. 定期回测评估参数效果

希望本配置指南能帮助您更好地定制系统以满足您的交易需求。