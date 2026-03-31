import sys
sys.stdout.reconfigure(encoding='utf-8')

import ast
import os
from pathlib import Path

# 分析対象ファイル
experiment_files = [
    'sim_metamorphose_society.py',
    'sim_society.py',
    'sim_large_scale_society.py',
    'sim_pairing.py',
    'sim_generation.py',
    'sim_inheritance.py',
    'sim_network_topology.py',
    'sim_precursor_encounter.py',
    'sim_coexistence.py',
    'sim_spontaneous_love.py',
    'sim_sleep_coexistence.py',
    'sim_loveless_lineage.py',
    'sim_antilove.py',
    'sim_antilove_density.py',
]

class ExperimentAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.docstring = ""
        self.class_defs = []
        self.function_defs = []
        self.param_assignments = []
        self.data_outputs = []
        self.initial_conditions = []
        
    def visit_Module(self, node):
        # モジュール全体のdocstringを取得
        if (node.body and isinstance(node.body[0], ast.Expr) and 
            isinstance(node.body[0].value, ast.Constant)):
            self.docstring = node.body[0].value.value
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        self.class_defs.append({
            'name': node.name,
            'lineno': node.lineno
        })
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        self.function_defs.append({
            'name': node.name,
            'lineno': node.lineno
        })
        self.generic_visit(node)

def analyze_file(filepath):
    """ファイルを読み込んで分析"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        analyzer = ExperimentAnalyzer()
        analyzer.visit(tree)
        
        return {
            'docstring': analyzer.docstring,
            'classes': analyzer.class_defs,
            'functions': analyzer.function_defs,
            'content': content
        }
    except Exception as e:
        return {'error': str(e)}

# 各ファイルを分析
print("=" * 80)
print("実験ファイル分析開始")
print("=" * 80)

for i, filename in enumerate(experiment_files, 1):
    filepath = os.path.join(os.getcwd(), filename)
    print(f"\n[{i}/{len(experiment_files)}] {filename}")
    print("-" * 80)
    
    if not os.path.exists(filepath):
        print(f"ファイルが見つかりません: {filepath}")
        continue
    
    result = analyze_file(filepath)
    
    if 'error' in result:
        print(f"エラー: {result['error']}")
        continue
    
    # ファイルの最初の20行を表示
    content_lines = result['content'].split('\n')[:30]
    print("\n--- ファイル冒頭 (最初の30行) ---")
    for j, line in enumerate(content_lines, 1):
        if j <= 30:
            print(f"{j:3d}: {line}")
    
    # クラス定義と関数定義を表示
    if result['classes']:
        print(f"\nクラス定義: {[c['name'] for c in result['classes']]}")
    if result['functions']:
        print(f"関数定義: {[f['name'] for f in result['functions'][:10]]}")  # 最初の10個のみ

print("\n" + "=" * 80)
print("分析完了")
print("=" * 80)
