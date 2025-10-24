import re

with open('api/index.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("正在添加缺失的基礎 API 路由...")

# 添加缺失的基礎 API 路由
basic_routes = '''
# ==================== 基礎 API ====================
@app.route('/api/health', methods=['GET'])
def health():
    """健康檢查"""
    return jsonify({
        "status": "healthy",
        "service": "graduation-management-system",
        "timestamp": "2024-01-01T00:00:00Z"
    })

@app.route('/api/test', methods=['GET'])
def test():
    """測試 API"""
    return jsonify({
        "success": True,
        "message": "API 測試成功",
        "data": {"test": "ok"}
    })

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """檢查登入狀態"""
    return jsonify({
        "authenticated": False,
        "message": "請先登入",
        "user": None
    })
'''

# 在 register 路由之前插入基礎路由
if "@app.route('/api/register'" in content:
    content = content.replace(
        "@app.route('/api/register'",
        basic_routes + "\n@app.route('/api/register'"
    )
    print("✅ 基礎 API 路由已添加")
else:
    print("❌ 找不到插入位置")

with open('api/index.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("修復完成！")
