from Project.settings import RED_BG_COLOR, BLUE_ELEMENT_COLOR


def show_window(name, frames: dict, buttons: list = ()):
    for frame in frames.values():
        frame.grid_forget()
    frame = frames[name]
    frame.grid(row=0, column=1, padx=(3, 6), pady=5, sticky="NSEW")

    # перекрашиваем кнопки
    for button in buttons:
        color = RED_BG_COLOR
        button_state = 'normal'
        if button.name == name:
            color = BLUE_ELEMENT_COLOR
            button_state = 'disabled'
        button.configure(fg_color=color, state=button_state)
