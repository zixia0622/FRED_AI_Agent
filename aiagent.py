import os, json
from datetime import datetime, timedelta
from dotenv import load_dotenv  # 读取.env文件的库
from fredapi import Fred        # 调用FRED数据的库
import requests  # 用于调用 DeepSeek API
from colorama import init, Fore, Style  # 美化输出（可选）

# 加载.env文件中的密钥（无需修改）
load_dotenv()
# 初始化colorama（可选，让输出颜色更清晰）
init(autoreset=True, convert=True, strip=False)

# 直接设置环境变量
os.environ['FRED_API_KEY'] = '输入你申请的FRED API KEY'
os.environ['DEEPSEEK_API_KEY'] = '输入你申请的DEEPSEEK API KEY'  # 替换为你的 DeepSeek API 密钥

class FREDAgent:
    def __init__(self):
        self.fred = Fred(api_key=os.getenv('FRED_API_KEY'))
        
    # 第一步：思考需要什么FRED数据（LLM自动识别指标）
    def think(self, question):
        prompt = f"""请告诉我哪个FRED指标代码能回答这个问题？
        问题：{question}
        常见FRED代码参考：UNRATE（美国失业率）、FPCPITOTLZGUSA（美国CPI通胀）、GDP（美国GDP）、DFF（联邦基金利率）
        仅返回JSON格式，不要多余内容：{{"explanation": "选择该指标的原因","series_code": "指标代码"}}"""
        
        # 调用 DeepSeek API 获取指标代码
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}"
        }
        payload = {
            "model": "deepseek-chat",  # 或其他支持的模型
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}  # 强制返回 JSON
        }
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()  # 检查请求是否成功
        
        # 解析 DeepSeek 返回的结果
        output = response.json()['choices'][0]['message']['content']
        plan = json.loads(output)
        return plan['series_code']  # 返回识别出的FRED指标代码
    
    # 第二步：行动：调用FRED API获取数据
    def act(self, series_code):
        # 获取指标的元数据（如单位：百分比）
        info = self.fred.get_series_info(series_code)
        units = info['units']
        
        # 获取近2年的数据（文档推荐的时间范围，可修改days=365为1年）
        end = datetime.now()
        start = end - timedelta(days=730)
        
        # 调用FRED API获取数据（无需修改）
        data = self.fred.get_series(series_code, start, end)
        return data, units  # 返回数据和单位
    
    # 第三步：观察：分析数据（提取最新值和日期）
    def observe(self, data, units):
        observations = {
            "current_value": float(data.iloc[-1]),  # 最新数据值
            "current_date": data.index[-1].strftime("%Y-%m-%d"),  # 最新数据日期
            "units": units  # 数据单位
        }
        return observations
    
    # 第四步：响应：生成自然语言回答
    def respond(self, question, observations):
        prompt = f"""用以下数据回答问题，要求简洁、引用具体数字：
        问题：{question}
        数据：{json.dumps(observations, indent=2)}"""
        
        # 调用LLM生成回答（无需修改）
        response = self.llm.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content  # 返回自然语言回答
    
    # 协调器：串联Think-Act-Observe-Respond四步（无需修改）
    def answer(self, question):
        print(f"\n{'='*60}")
        print(f"问题：{question}")
        print(f"{'='*60}")
        
        try:
            # 1. 思考：确定FRED指标
            series_code = self.think(question)
            print(f"\n识别出的FRED指标代码：{series_code}")
            
            # 2. 行动：获取数据
            data, units = self.act(series_code)
            print(f"获取数据范围：{data.index[0].date()} 至 {data.index[-1].date()}")
            print(f"最新数据：{data.iloc[-1]:.2f} {units}（{data.index[-1].date()}）")
            
            # 3. 观察：分析数据
            observations = self.observe(data, units)
            
            # 4. 响应：生成回答
            response = self.respond(question, observations)
            print(f"\n{'='*20} 最终回答 {'='*20}")
            print(response)
            return response
        
        # 错误处理（如API调用失败，显示错误信息）
        except Exception as e:
            error_msg = f"错误：{str(e)}"
            print(f"\n{Fore.RED}{error_msg}{Style.RESET_ALL}")
            return error_msg
        
dotenv_path = r'C:\Users\11760\.env'  
is_loaded = load_dotenv(dotenv_path=dotenv_path)


# 创建一个FRED代理对象
agent = FREDAgent()

# 交互式提问：运行后可手动输入问题
print("\n进入交互式模式，可输入经济问题：")
question = input("请输入你的问题：")
agent.answer(question)