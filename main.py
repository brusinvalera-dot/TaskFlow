import flet as ft
import json
from pathlib import Path
from datetime import datetime

DATA = Path(__file__).with_name('tasks.json')

def main(page: ft.Page):
    page.title = 'TaskFlow | Менеджер задач'
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = '#0B1220'
    page.padding = 28
    page.window_width = 920
    page.window_height = 720
    tasks = []
    if DATA.exists():
        try:
            tasks.extend(json.loads(DATA.read_text(encoding='utf-8')))
        except (ValueError, OSError):
            pass

    title = ft.TextField(hint_text='Например: закончить презентацию', expand=True, border_radius=12)
    category = ft.Dropdown(value='Работа', width=150, options=[ft.dropdown.Option(x) for x in ['Работа', 'Учёба', 'Личное']])
    search = ft.TextField(hint_text='Поиск задач...', prefix_icon=ft.Icons.SEARCH, expand=True, border_radius=12)
    task_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    stats = ft.Text(color='#94A3B8')
    current_filter = ['Все']

    def save():
        DATA.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding='utf-8')

    def toggle(task):
        task['done'] = not task['done']
        save()
        render()

    def delete(task):
        tasks.remove(task)
        save()
        render()

    def render(e=None):
        q = (search.value or '').lower().strip()
        shown = [t for t in tasks if q in t['title'].lower() and (current_filter[0] == 'Все' or (current_filter[0] == 'Активные' and not t['done']) or (current_filter[0] == 'Готово' and t['done']))]
        task_list.controls.clear()
        for task in shown:
            task_list.controls.append(ft.Container(
                bgcolor='#172338', border_radius=14, padding=ft.padding.symmetric(horizontal=14, vertical=8),
                content=ft.Row([
                    ft.Checkbox(value=task['done'], on_change=lambda e, t=task: toggle(t)),
                    ft.Column([ft.Text(task['title'], size=16, weight=ft.FontWeight.W_500, color='#94A3B8' if task['done'] else '#F8FAFC'), ft.Text(f"{task['category']}  •  {task['created']}", size=11, color='#94A3B8')], expand=True, spacing=3),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color='#FB7185', tooltip='Удалить', on_click=lambda e, t=task: delete(t))
                ])
            ))
        if not shown:
            task_list.controls.append(ft.Container(padding=35, alignment=ft.alignment.center, content=ft.Text('Задач пока нет ✨', color='#94A3B8', size=16)))
        done = sum(t['done'] for t in tasks)
        stats.value = f'Всего: {len(tasks)}   •   Выполнено: {done}   •   Осталось: {len(tasks) - done}'
        page.update()

    def add(e):
        value = (title.value or '').strip()
        if not value:
            title.error_text = 'Введите название задачи'
            page.update()
            return
        title.error_text = None
        tasks.insert(0, {'title': value, 'category': category.value or 'Личное', 'done': False, 'created': datetime.now().strftime('%d.%m.%Y')})
        title.value = ''
        save()
        render()

    def filter_changed(e):
        current_filter[0] = e.control.data
        render()

    search.on_change = render
    title.on_submit = add
    page.add(ft.Container(width=800, content=ft.Column([
        ft.Row([ft.Icon(ft.Icons.TASK_ALT, color='#818CF8', size=36), ft.Text('TaskFlow', size=32, weight=ft.FontWeight.BOLD)], spacing=12),
        ft.Text('Простой и красивый менеджер задач', size=15, color='#94A3B8'),
        ft.Container(height=14),
        ft.Row([title, category, ft.FilledButton('Добавить', icon=ft.Icons.ADD, on_click=add)], wrap=True),
        ft.Container(height=12),
        ft.Row([search]),
        ft.Row([ft.TextButton(x, data=x, on_click=filter_changed) for x in ['Все', 'Активные', 'Готово']]),
        stats,
        ft.Divider(color='#334155'),
        ft.Container(content=task_list, height=370),
        ft.Text('Данные автоматически сохраняются в tasks.json', size=12, color='#64748B')
    ], spacing=10)))
    render()

if __name__ == '__main__':
    ft.app(target=main)
