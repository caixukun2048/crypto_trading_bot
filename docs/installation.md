# 加密货币合约分析交易系统安装指南

本文档将指导您完成加密货币合约分析交易系统的安装与配置过程。

## 系统要求

- Python 3.8或更高版本
- 稳定的互联网连接
- 至少1GB可用内存
- 至少500MB可用磁盘空间

## 安装步骤

### 1. 克隆或下载代码

您可以通过以下方式获取代码：

```bash
# 使用Git克隆
git clone https://github.com/yourusername/crypto_trading_bot.git

# 或者直接下载ZIP文件并解压
```

### 2. 创建虚拟环境（推荐）

```bash
# 进入项目目录
cd crypto_trading_bot

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖包

```bash
pip install -r requirements.txt
```

### 4. 安装TA-Lib

TA-Lib是一个技术分析库，用于计算各种技术指标。安装过程可能因操作系统而异：

#### Windows:

1. 下载适合您Python版本的预编译wheel文件：[下载链接](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)
2. 安装下载的wheel文件：
   ```
   pip install TA_Lib-0.4.24-cp38-cp38-win_amd64.whl
   ```
   （请替换为您下载的文件名）

#### Linux:

```bash
# 安装依赖
sudo apt-get install build-essential
sudo apt-get install libta-lib-dev

# 安装Python包
pip install ta-lib
```

#### macOS:

```bash
# 使用Homebrew安装
brew install ta-lib

# 安装Python包
pip install ta-lib
```

### 5. 配置交易所API

1. 在您要使用的交易所（如Gate.io、Binance等）创建API密钥
2. 编辑`config.yaml`文件，填入您的API信息：

```yaml
exchanges:
  gateio:
    api_key: "YOUR_API_KEY"
    secret_key: "YOUR_SECRET_KEY"
    use_testnet: true  # 建议先使用测试网络
```

### 6. 配置Telegram通知（可选）

如果您希望通过Telegram接收通知：

1. 使用BotFather创建一个Telegram机器人并获取token
2. 获取您的chat_id
3. 编辑`config.yaml`文件，填入Telegram信息：

```yaml
telegram:
  token: "YOUR_BOT_TOKEN"
  chat_id: "YOUR_CHAT_ID"
  enabled: true
```

## 验证安装

安装完成后，您可以运行以下命令验证系统是否正常工作：

```bash
python start.py -s BTC/USDT -t 1h
```

如果一切正常，您将看到系统分析BTC/USDT 1小时图的结果。

## 常见安装问题

### 1. TA-Lib安装失败

**问题**: 安装TA-Lib时出现编译错误

**解决方案**: 
- Windows用户：尝试使用预编译的wheel文件
- Linux/Mac用户：确保已安装所有必要的开发工具和库

### 2. 依赖冲突

**问题**: 安装某些依赖包时出现版本冲突

**解决方案**: 
- 使用虚拟环境避免与系统包冲突
- 可以尝试：`pip install -r requirements.txt --ignore-installed`

### 3. API连接问题

**问题**: 无法连接到交易所API

**解决方案**:
- 检查API密钥是否正确
- 确认您的网络能够访问交易所（某些地区可能需要代理）
- 验证交易所服务器是否正常运行

## 更新系统

当有新版本发布时，更新系统的步骤如下：

```bash
# 拉取最新代码
git pull

# 更新依赖
pip install -r requirements.txt --upgrade
```

## 后续步骤

安装完成后，请参考以下文档继续设置和使用系统：

- [配置指南](configuration.md) - 详细的系统配置说明
- [用户手册](user_manual.md) - 系统使用方法和功能介绍

如果您在安装过程中遇到任何问题，请查看我们的常见问题文档或在GitHub上提交Issue。