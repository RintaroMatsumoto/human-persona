with open(r'core\inner_shell\api.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for i in range(595, 610):
        print(f'{i+1}: {lines[i]}', end='')
