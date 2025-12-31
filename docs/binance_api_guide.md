# 币安API配置指南

## 概述

本系统已集成币安交易所API,支持现货和期货交易功能。在使用币安交易功能前,需要先配置API密钥。

## 配置方式

系统支持两种配置方式:

### 方式1: 环境变量配置(推荐)

在运行环境的环境变量中设置以下变量:

```bash
export BINANCE_API_KEY="your_api_key_here"
export BINANCE_API_SECRET="your_api_secret_here"
export BINANCE_TESTNET="true"  # true表示使用测试网,false表示使用正式网
```

### 方式2: 配置文件配置

修改 `config/binance_config.json` 文件:

```json
{
  "api_key": "your_api_key_here",
  "api_secret": "your_api_secret_here",
  "testnet": true,
  "default_trade_type": "spot"
}
```

配置参数说明:
- `api_key`: 币安API Key(必填)
- `api_secret`: 币安API Secret Key(必填)
- `testnet`: 是否使用测试网,默认true(选填)
  - `true`: 使用测试网(推荐,不会产生真实交易)
  - `false`: 使用正式网(会进行真实交易,请谨慎)
- `default_trade_type`: 默认交易类型,默认"spot"(选填)
  - `spot`: 现货交易
  - `futures`: 期货交易

## 获取币安API密钥

### 测试网API密钥(推荐)

1. 访问币安测试网: https://testnet.binance.vision/
2. 注册并登录测试网账户
3. 进入API管理页面创建API Key
4. 启用"读取"和"交易"权限

### 正式网API密钥

1. 登录币安正式账户
2. 进入【API管理】页面
3. 创建新的API Key
4. 设置权限:
   - ✅ 启用读取权限
   - ✅ 启用现货交易/合约交易权限
5. 建议配置IP白名单限制访问
6. **重要**: 永远不要将API Secret Key泄露给他人

## 可用工具

### 1. binance_spot_open_position

在币安现货市场开仓

**参数:**
- `symbol`: 交易对符号(如: BTCUSDT、ETHUSDT)
- `direction`: 交易方向(BUY-做多/买入 或 SELL-做空/卖出)
- `amount`: 交易数量或金额(如: 0.001表示BTC数量,100表示USDT金额)
- `order_type`: 订单类型(MARKET-市价单 或 LIMIT-限价单,默认MARKET)
- `price`: 限价单价格(仅限价单需要,如: 90000)

**示例:**
```python
# 使用市价单买入0.001个BTC
binance_spot_open_position(
    symbol="BTCUSDT",
    direction="BUY",
    amount="0.001",
    order_type="MARKET"
)

# 使用限价单在90000价格买入
binance_spot_open_position(
    symbol="BTCUSDT",
    direction="BUY",
    amount="0.001",
    order_type="LIMIT",
    price="90000"
)
```

### 2. binance_futures_open_position

在币安期货市场开仓(USDT合约)

**参数:**
- `symbol`: 交易对符号(如: BTCUSDT、ETHUSDT)
- `direction`: 交易方向(BUY-做多/买入 或 SELL-做空/卖出)
- `amount`: 交易数量或金额(如: 0.001表示BTC数量,100表示USDT金额)
- `order_type`: 订单类型(MARKET-市价单 或 LIMIT-限价单,默认MARKET)
- `price`: 限价单价格(仅限价单需要,如: 90000)
- `leverage`: 杠杆倍数(如: 1、5、10、20,默认1倍)
- `position_side`: 持仓方向(LONG-多头 或 SHORT-空头,可选)

**示例:**
```python
# 使用市价单做多10倍杠杆BTC期货
binance_futures_open_position(
    symbol="BTCUSDT",
    direction="BUY",
    amount="100",
    order_type="MARKET",
    leverage="10"
)

# 使用限价单做空ETH期货
binance_futures_open_position(
    symbol="ETHUSDT",
    direction="SELL",
    amount="1",
    order_type="LIMIT",
    price="3500",
    leverage="5",
    position_side="SHORT"
)
```

### 3. binance_get_balance

查询币安账户余额

**参数:**
- `asset`: 资产符号(如: USDT、BTC,可选,不填则查询所有资产)

**示例:**
```python
# 查询USDT余额
binance_get_balance(asset="USDT")

# 查询所有资产余额
binance_get_balance()
```

## 使用建议

### 1. 测试网优先

强烈建议先在测试网环境测试:
- 测试网不会产生真实交易
- 测试网API密钥与正式网不通用
- 可以自由测试各种交易场景

### 2. 小额测试

在正式网使用时:
- 先用小额资金测试
- 确认功能正常后再加大资金
- 建议先使用市价单测试,再尝试限价单

### 3. 杠杆谨慎

期货交易使用杠杆会放大收益和风险:
- 1-3倍杠杆相对安全
- 10-20倍杠杆风险极高
- 新手建议不超过5倍杠杆

### 4. 安全措施

- 配置IP白名单限制API访问
- 定期轮换API密钥
- 不要将API密钥提交到代码仓库
- 及时禁用不再使用的API密钥

## 错误处理

### 常见错误

1. **API-key format invalid**
   - API密钥格式错误
   - 检查API Key和Secret Key是否正确

2. **Invalid signature**
   - API Secret Key错误
   - 确认Secret Key是否完整且正确

3. **API-key format invalid**
   - API密钥格式无效
   - 检查是否复制了多余的空格或换行

4. **Insufficient balance**
   - 账户余额不足
   - 检查账户是否有足够的资金

5. **Lot size filter failure**
   - 交易数量不符合规则
   - 币安对最小交易数量有要求

### 调试技巧

1. 先调用 `binance_get_balance` 确认配置正确
2. 使用测试网环境避免资金损失
3. 查看详细错误信息进行排查
4. 检查API权限是否正确配置

## 注意事项

⚠️ **重要提示**

1. **资金风险**: 加密货币交易存在较高风险,请谨慎操作
2. **测试先行**: 务必先在测试网充分测试
3. **小额开始**: 正式网使用时从小额开始
4. **权限控制**: 不要授予API不必要的权限
5. **安全保管**: 妥善保管API密钥,不要泄露
6. **及时止损**: 设置合理的止损点,控制风险

## 联系支持

如果遇到问题:
1. 查看币安官方API文档: https://binance-docs.github.io/apidocs/
2. 检查本文档的常见错误部分
3. 确认API密钥配置是否正确
4. 查看系统日志获取详细错误信息
