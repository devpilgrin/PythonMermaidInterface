import gradio as gr
from mermaid_cli import render_mermaid
from pathlib import Path
import os

# Настройки
PLUGINS_DIR = Path("plugins")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

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
            print(f"Ошибка загрузки плагина {plugin_path}: {e}")
    return plugins

plugins = load_plugins()

def create_plugin_button(plugin):
    """Создает обработчик для кнопки плагина"""
    def add_code(current_code):
        separator = "\n\n" if current_code.strip() else ""
        return f"{current_code}{separator}{plugin.insert_code}"
    return add_code

async def generate_diagram(code, output_format):
    """Асинхронная генерация диаграммы с выбором формата"""
    try:
        # Определяем расширение и MIME-тип
        format_map = {
            "PNG": ("png", "image/png"),
            "SVG": ("svg", "image/svg+xml")
        }
        ext, mime = format_map.get(output_format, ("svg", "image/svg+xml"))
        
        # Генерируем уникальное имя файла
        output_file = OUTPUT_DIR / f"diagram.{ext}"
        
        # Рендерим диаграмму
        _, _, data = await render_mermaid(
            code,
            output_format=ext,
            background_color="white",
            mermaid_config={"theme": "forest"}
        )
        
        # Сохраняем файл
        with open(output_file, "wb") as f:
            f.write(data)
            
        return output_file, None
        
    except Exception as e:
        error_msg = f"Ошибка генерации: {str(e)}"
        print(error_msg)
        return None, error_msg

# Создаем интерфейс Gradio
with gr.Blocks(title="Mermaid Studio") as demo:
    
    gr.Markdown("# Mermaid Diagram Studio")
    format_selector = gr.Radio(
        ["SVG", "PNG"],
        label="Формат",
        value="PNG"
    )    
        
    with gr.Row():  
    
        # Основная рабочая область
        with gr.Column(scale=2):
            
            text_input = gr.TextArea(
                label="Mermaid код",
                placeholder="Введите код диаграммы здесь...",
                lines=15
            ) 
            with gr.Row():
                for plugin in plugins:
                    gr.Button(
                        plugin.button_text,
                        variant="huggingface",
                        size= 'sm',
                    ).click(
                        fn=create_plugin_button(plugin),
                        inputs=text_input,
                        outputs=text_input
                    )           
                   
        # Боковая панель с плагинами
        with gr.Column(scale=2):
            image_output = gr.Image(
                label="Результат",
                show_label=False,
                height=430
            )             
          
            
    with gr.Row():
        error_output = gr.Textbox(
            label="Сообщения об ошибках",
            placeholder="Здесь будут отображаться ошибки",
            lines=3,
            visible=False
        )


            
    visualize_btn = gr.Button("Визуализировать", variant="primary")
    clear_btn = gr.Button("Очистить", variant="secondary")
    
    
    
    # Привязка основных действий
    visualize_btn.click(
        fn=generate_diagram,
        inputs=[text_input, format_selector],
        outputs=[image_output, error_output]
    ).then(
        fn=lambda x: gr.update(visible=bool(x)),
        inputs=error_output,
        outputs=error_output
    )
    
    clear_btn.click(
        lambda: ("", "", ""),
        inputs=None,
        outputs=[text_input, image_output, error_output]
    )

# Запуск приложения
if __name__ == "__main__":
    demo.launch()