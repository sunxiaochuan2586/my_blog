print("--- 启动最终诊断脚本 ---")

# 这是一个独立的脚本，所以我们需要手动添加项目路径
# 以确保 'from my_app import ...' 能够正常工作
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("--- 步骤 1: 尝试从 my_app 导入 create_app 函数 ---")
try:
    from my_app import create_app
    print(">>> 成功: 成功导入 create_app 函数。")
except Exception as e:
    print(f"\n!!! 致命错误: 在导入 create_app 时发生错误 !!!")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {e}")
    print("--- 详细错误追踪 (Traceback) ---")
    import traceback
    traceback.print_exc()
    sys.exit(1)  # 如果导入失败，立即退出

print("\n--- 步骤 2: 尝试调用 create_app() 来创建 Flask 应用实例 ---")
try:
    app = create_app()
    print(">>> 成功: 成功创建了 Flask 应用实例。")
except Exception as e:
    print(f"\n!!! 致命错误: 在执行 create_app() 函数时发生错误 !!!")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {e}")
    print("--- 详细错误追踪 (Traceback) ---")
    import traceback
    traceback.print_exc()
    sys.exit(1)  # 如果创建失败，立即退出

print("\n--- 步骤 3: 检查 'make-admin' 命令是否已成功注册 ---")
# Flask 应用的命令存储在 app.cli.commands 这个字典里
registered_commands = list(app.cli.commands.keys())
print(f"在应用中找到的已注册命令: {registered_commands}")

if 'make-admin' in registered_commands:
    print("\n>>> 最终结论: 'make-admin' 命令已正确注册！问题可能与你的 Shell 环境有极特殊的关系。")
else:
    print("\n>>> 最终结论: 'make-admin' 命令未能注册。")
    print("    这几乎可以肯定是因为在加载 my_app/commands.py 文件或其依赖项时发生了错误。")
    print("    请仔细检查上面步骤 1 和步骤 2 的输出，那里应该有真正的错误信息。")

print("\n--- 诊断脚本执行完毕 ---")