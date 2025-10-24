# 修复密码保存问题

# 读取后端文件
with open('./api/index.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找注册端点
import re

# 查找注册函数
register_pattern = r'@app\.route\(\s*[\'"]/api/register[\'"]\s*,\s*methods=\[[\'"]POST[\'"]\]\s*\)\s*def register\(\):.*?return json\.response\(.*?\)'

match = re.search(register_pattern, content, re.DOTALL)
if match:
    print("找到注册端点")
    register_code = match.group(0)
    print("当前注册代码:")
    print(register_code[:500] + "..." if len(register_code) > 500 else register_code)
else:
    print("未找到注册端点，需要手动修复")
