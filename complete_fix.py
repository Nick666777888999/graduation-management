import re

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到並修復問題區域
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # 修復 hideRegister 後的結構
    if 'hideRegister();' in line and i+3 < len(lines):
        # 檢查後面是否有問題
        if '}' in lines[i+1] and '}' in lines[i+2] and '// 載入內容' in lines[i+3]:
            fixed_lines.append(line)  # hideRegister();
            fixed_lines.append('    }\\n')  # 正確的結束括號
            fixed_lines.append('\\n')  # 空行
            fixed_lines.append('    // 載入內容\\n')  # 註解
            i += 4  # 跳過已處理的行
            continue
    
    fixed_lines.append(line)
    i += 1

# 寫回文件
with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("✅ 完整修復完成")
