import tkinter as tk


class Tooltip:
    """Стандартный тултип"""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.scheduled_show = None
        self.scheduled_hide = None
        self.tooltip_visible = False

        # Bind events to the widget
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)  # Track mouse movement

    def on_enter(self, event):
        # Schedule tooltip to appear after 500ms
        self.scheduled_show = self.widget.after(100, self.show_tooltip, event)

    def on_leave(self, event):
        # Cancel any pending show and schedule hide
        if self.scheduled_show:
            self.widget.after_cancel(self.scheduled_show)
            self.scheduled_show = None
        self.schedule_hide()

    def on_motion(self, event):
        # Update tooltip position if visible
        if self.tooltip_visible and self.tooltip:
            x = event.x_root + 10
            y = event.y_root + 10
            self.tooltip.geometry(f"+{x}+{y}")

    def show_tooltip(self, event):
        # Create tooltip window using pure Tkinter
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.attributes("-topmost", True)

        # Position near the cursor
        x = event.x_root + 10
        y = event.y_root + 10
        self.tooltip.geometry(f"+{x}+{y}")

        # Add label with text
        label = tk.Label(
            self.tooltip,
            text=self.text,
            bg="white",
            fg="black",
            relief="solid",
            borderwidth=1,
            padx=5,
            pady=2
        )
        label.pack()

        # Track tooltip visibility and bind its events
        self.tooltip_visible = True
        self.tooltip.bind("<Enter>", self.on_tooltip_enter)
        self.tooltip.bind("<Leave>", self.on_tooltip_leave)

    def on_tooltip_enter(self, event):
        # Cancel hide if mouse enters tooltip
        if self.scheduled_hide:
            self.widget.after_cancel(self.scheduled_hide)
            self.scheduled_hide = None

    def on_tooltip_leave(self, event):
        # Schedule hide when mouse leaves tooltip
        self.schedule_hide()

    def schedule_hide(self):
        # Schedule tooltip destruction after 200ms
        if self.tooltip_visible:
            self.scheduled_hide = self.widget.after(50, self.hide_tooltip)

    def hide_tooltip(self):
        if self.tooltip_visible and self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
            self.tooltip_visible = False

    def change_text(self, new_text):
        self.text = new_text
