button_text = "stateDiagram"
button_icon = "./icon/6863849.png"
insert_code = """---
title: Simple sample
---
stateDiagram-v2
    [*] --> Still
    Still --> [*]

    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]"""