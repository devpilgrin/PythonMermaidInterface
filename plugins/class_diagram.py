# Текст кнопки
button_text = "classDiagram"
# Иконка (URL или имя иконки из Font Awesome)
button_icon = './icon/11906260.png'  # Иконка гаечного ключа
# Код Mermaid, который будет вставлен в редактор
insert_code = """---
title: Animal example
---
classDiagram
    note "From Duck till Zebra"
    Animal <|-- Duck
    note for Duck "can fly\ncan swim\ncan dive\ncan help in debugging"
    Animal <|-- Fish
    Animal <|-- Zebra
    Animal : +int age
    Animal : +String gender
    Animal: +isMammal()
    Animal: +mate()
    class Duck{
        +String beakColor
        +swim()
        +quack()
    }
    class Fish{
        -int sizeInFeet
        -canEat()
    }
    class Zebra{
        +bool is_wild
        +run()
    }"""