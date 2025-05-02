import gradio as gr
from mermaid_cli import render_mermaid
from pathlib import Path
import os
import logging

# Настройки
PLUGINS_DIR = Path("plugins")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Настройка логирования
logging.basicConfig(filename="mermaid_app.log", level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def load_plugins():
    """Загружает плагины из папки plugins"""
    plugins = []
    if not PLUGINS_DIR.exists():
        PLUGINS_DIR.mkdir()
        return plugins
        
    for plugin_path in PLUGINS_DIR.glob("*.py"):
        try:
            plugin_spec = __import__(f"plugins.{plugin_path.stem}", fromlist=[''])
            if hasattr(plugin_spec, 'button_text') and hasattr(plugin_spec, 'insert_code'):
                plugins.append(plugin_spec)
        except Exception as e:
            logging.error(f"Ошибка загрузки плагина {plugin_path}: {e}", exc_info=True)
    return plugins

plugins = load_plugins()

def create_plugin_button(plugin):
    """Создает обработчик для кнопки плагина"""
    def add_code(current_code):
        separator = "\n\n" if current_code.strip() else ""
        return f"{current_code}{separator}{plugin.insert_code}"
    return add_code

async def generate_diagram(code, output_format, theme):
    """Асинхронная генерация диаграммы с выбором формата и темы"""
    try:
        format_map = {
            "SVG": ("svg", "image/svg+xml"),
            "PNG": ("png", "image/png"),
            "PDF": ("pdf", "application/pdf")
        }
        ext, mime = format_map.get(output_format, ("svg", "image/svg+xml"))
        
        output_file = OUTPUT_DIR / f"diagram.{ext}"
        
        _, _, data = await render_mermaid(
            code,
            output_format=ext,
            background_color="white",
            mermaid_config={"theme": theme}
        )
        
        if not data:
            raise ValueError("Пустые данные от рендера")
            
        with open(output_file, "wb") as f:
            f.write(data)
            
        return output_file, None
        
    except Exception as e:
        logging.error(f"Ошибка генерации: {str(e)}", exc_info=True)
        return None, f"Ошибка: {str(e)}. Проверьте логи для деталей."

def export_to_markdown(code):
    """Экспорт в Markdown"""
    return f"```mermaid\n{code}\n```"

def export_to_html(code):
    """Экспорт в HTML"""
    return f"<div class='mermaid'>{code}</div>"

def reload_plugins():
    """Динамическая перезагрузка плагинов"""
    global plugins
    plugins = load_plugins()
    return [gr.Button(plugin.button_text, icon=get_icon(plugin)) for plugin in plugins]

def get_icon(plugin):
    """Возвращает иконку для плагина (по умолчанию — дефолтная)"""
    if hasattr(plugin, 'button_icon'):
        return plugin.button_icon
    return "https://cdn-icons-png.flaticon.com/512/1163/1163661.png"  # Дефолтная иконка

# Создаем интерфейс Gradio
with gr.Blocks(title="Mermaid Studio") as demo:
    gr.HTML("<link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css'>")
    
    gr.Markdown("# Mermaid Diagram Studio")
    
    # Панель управления
    with gr.Row():
        format_selector = gr.Radio(
            ["SVG", "PNG", "PDF"],
            label="Формат",
            value="PNG"
        )
        
        theme_selector = gr.Dropdown(
            ["default", "dark", "forest", "neutral"],
            label="Тема",
            value="forest"
        )
        
        visualize_btn = gr.Button("Визуализировать", variant="primary")
        clear_btn = gr.Button("Очистить", variant="secondary")
        refresh_btn = gr.Button("Обновить плагины")

    # Основной контент
    with gr.Row():
        with gr.Column(scale=2):
            text_input = gr.Textbox(
                label="Mermaid код",
                placeholder="Введите код диаграммы здесь...",
                value=""
            )
            
            with gr.Row():
                # Кнопки плагинов
                plugin_buttons = []
                for plugin in plugins:
                    btn = gr.Button(plugin.button_text, icon=get_icon(plugin))
                    btn.click(
                        fn=create_plugin_button(plugin),
                        inputs=text_input,
                        outputs=text_input
                    )
                    plugin_buttons.append(btn)

        with gr.Column(scale=2):
            image_output = gr.Image(label="Результат", show_label=False, height=430)
            error_output = gr.Textbox(label="Сообщения об ошибках", placeholder="Здесь будут отображаться ошибки", lines=3, visible=False)
            markdown_output = gr.Textbox(label="Markdown", lines=5, visible=False)
            html_output = gr.Textbox(label="HTML", lines=5, visible=False)

    # Привязка действий
    visualize_btn.click(
        fn=generate_diagram,
        inputs=[text_input, format_selector, theme_selector],
        outputs=[image_output, error_output]
    ).then(
        fn=lambda x: gr.update(visible=bool(x)),
        inputs=error_output,
        outputs=error_output
    )

    # Экспорт в Markdown
    text_input.change(
        fn=export_to_markdown,
        inputs=text_input,
        outputs=markdown_output
    )

    # Экспорт в HTML
    text_input.change(
        fn=export_to_html,
        inputs=text_input,
        outputs=html_output
    )

    refresh_btn.click(fn=reload_plugins, outputs=plugin_buttons)
    
    clear_btn.click(
        lambda: ("", "", "", "", ""),
        inputs=None,
        outputs=[text_input, image_output, error_output, markdown_output, html_output]
    )

# Запуск приложения
if __name__ == "__main__":
    demo.launch()