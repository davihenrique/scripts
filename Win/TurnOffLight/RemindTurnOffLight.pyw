# -*- coding: utf-8 -*-
"""
RemindTurnOffLight.pyw
Lembrete visual para desligar a luz - somente interface gráfica.
Estilo: caixa de diálogo clássica do Windows (Win9x/2000) em modo escuro.
Sem dependências externas (apenas tkinter + winsound, ambos da stdlib).
"""

import os
import tkinter as tk
from datetime import datetime

try:
    import winsound
except ImportError:  # nao-Windows: apenas ignora o som
    winsound = None


# ----------------------------------------------------------------------------
# Paleta "Windows classico" adaptada para modo escuro
# ----------------------------------------------------------------------------
FACE        = "#3b3b3b"   # cor da "chapa" cinza classica, escurecida
LIGHT_EDGE  = "#5f5f5f"   # borda 3D clara (canto superior/esquerdo)
DARK_EDGE   = "#1c1c1c"   # borda 3D escura (canto inferior/direito)
DARKER_EDGE = "#101010"   # segundo nivel de borda escura
TEXT        = "#e6e6e6"   # texto principal
TITLE_A     = "#0a1f52"   # gradiente da barra de titulo (inicio)
TITLE_B     = "#245edb"   # gradiente da barra de titulo (fim)
TITLE_TXT   = "#ffffff"

TITLE      = "Lembrete - Desligar a Luz"
MESSAGE    = ("10 PM - Desligar a luz.\n\n"
             "Recomenda-se apagar as luzes agora para\n"
             "uma melhor noite de sono.")

# Fontes classicas (com fallback para Segoe UI se nao existirem)
FONT_TITLE = ("MS Sans Serif", 8, "bold")
FONT_BODY  = ("MS Sans Serif", 9)
FONT_BTN   = ("MS Sans Serif", 9)


# ----------------------------------------------------------------------------
# Widgets auxiliares com bordas 3D no estilo antigo
# ----------------------------------------------------------------------------
def bevel(parent, **kw):
    """Frame com borda 3D 'raised' de 2px como nas janelas antigas."""
    outer = tk.Frame(parent, bg=LIGHT_EDGE, bd=0, **kw)
    mid   = tk.Frame(outer, bg=DARK_EDGE, bd=0)
    mid.pack(fill="both", expand=True, padx=(0, 2), pady=(0, 2))
    inner = tk.Frame(mid, bg=FACE, bd=0)
    inner.pack(fill="both", expand=True, padx=(2, 0), pady=(2, 0))
    return outer, inner


class ClassicButton(tk.Frame):
    """Botao cinza com relevo que 'afunda' ao ser pressionado."""

    def __init__(self, parent, text, command):
        super().__init__(parent, bg=FACE)
        self.command = command
        self._top = tk.Frame(self, bg=LIGHT_EDGE)
        self._top.pack(fill="both", expand=True)
        self._bottom = tk.Frame(self._top, bg=DARK_EDGE)
        self._bottom.pack(fill="both", expand=True, padx=(0, 2), pady=(0, 2))
        self.label = tk.Label(self._bottom, text=text, bg=FACE, fg=TEXT,
                              font=FONT_BTN, padx=14, pady=3)
        self.label.pack(fill="both", expand=True, padx=(2, 0), pady=(2, 0))

        for w in (self, self._top, self._bottom, self.label):
            w.bind("<Button-1>", self._press)
            w.bind("<ButtonRelease-1>", self._release)

    def _press(self, _e):
        self._top.configure(bg=DARK_EDGE)
        self._bottom.configure(bg=LIGHT_EDGE)

    def _release(self, _e):
        self._top.configure(bg=LIGHT_EDGE)
        self._bottom.configure(bg=DARK_EDGE)
        self.command()


def draw_bulb(canvas):
    """Desenha uma lampada acesa (vetorial) no canvas de 48x48."""
    glow   = "#fff3a8"
    glass  = "#ffe15a"
    glass2 = "#e8b400"
    metal  = "#b8b8b8"
    metal2 = "#6f6f6f"
    ray    = "#ffd84a"

    # raios de luz
    rays = [(24, 1, 24, 8), (7, 8, 12, 13), (41, 8, 36, 13),
            (2, 20, 9, 20), (46, 20, 39, 20), (8, 33, 13, 29),
            (40, 33, 35, 29)]
    for x1, y1, x2, y2 in rays:
        canvas.create_line(x1, y1, x2, y2, fill=ray, width=2, capstyle="round")

    # bulbo (vidro)
    canvas.create_oval(12, 7, 36, 31, fill=glass, outline=glass2, width=1)
    canvas.create_arc(12, 7, 36, 31, start=55, extent=90, style="arc",
                      outline=glow, width=2)

    # filamento
    canvas.create_line(19, 22, 22, 16, 25, 22, fill="#d06b00", width=1,
                       joinstyle="round")

    # colarinho / rosca
    canvas.create_polygon(18, 29, 30, 29, 28, 34, 20, 34,
                          fill=metal, outline=metal2)
    canvas.create_rectangle(19, 34, 29, 37, fill=metal, outline=metal2)
    canvas.create_rectangle(20, 37, 28, 39, fill=metal2, outline=metal2)
    canvas.create_rectangle(21, 39, 27, 41, fill=metal, outline=metal2)
    canvas.create_polygon(22, 41, 26, 41, 24, 44, fill=metal2, outline=metal2)


# ----------------------------------------------------------------------------
# Janela principal
# ----------------------------------------------------------------------------
class ReminderWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)          # remove a barra nativa
        self.root.configure(bg=DARKER_EDGE)
        self.root.attributes("-topmost", True)
        self._drag = (0, 0)

        # moldura externa 3D
        frame = tk.Frame(self.root, bg=LIGHT_EDGE, bd=0)
        frame.pack(padx=1, pady=1)
        inner = tk.Frame(frame, bg=FACE, bd=0)
        inner.pack(padx=(1, 2), pady=(1, 2))

        self._build_titlebar(inner)
        self._build_body(inner)

        self._center()
        self.root.bind("<Escape>", lambda e: self.close())
        self.root.bind("<Return>", lambda e: self.close())

        if winsound:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)

    # ---- barra de titulo com gradiente ------------------------------------
    def _build_titlebar(self, parent):
        bar = tk.Canvas(parent, height=20, highlightthickness=0, bd=0)
        bar.pack(fill="x")
        self._paint_gradient(bar)
        bar.bind("<Configure>", lambda e: self._paint_gradient(bar))

        bar.create_text(6, 10, anchor="w", text=TITLE, fill=TITLE_TXT,
                        font=FONT_TITLE, tags="t")

        # botao de fechar estilo classico
        btn = tk.Label(parent, text="x", bg=FACE, fg=TEXT, font=FONT_TITLE,
                       width=2, relief="raised", bd=1)
        btn.place(in_=bar, relx=1.0, x=-4, y=2, anchor="ne")
        btn.bind("<Button-1>", lambda e: self.close())

        for w in (bar,):
            w.bind("<Button-1>", self._start_move)
            w.bind("<B1-Motion>", self._on_move)

    def _paint_gradient(self, canvas):
        canvas.delete("grad")
        w = canvas.winfo_width() or 300
        steps = 64
        for i in range(steps):
            r = int(0x0a + (0x24 - 0x0a) * i / steps)
            g = int(0x1f + (0x5e - 0x1f) * i / steps)
            b = int(0x52 + (0xdb - 0x52) * i / steps)
            x0 = int(w * i / steps)
            x1 = int(w * (i + 1) / steps)
            canvas.create_rectangle(x0, 0, x1, 20, outline="",
                                    fill=f"#{r:02x}{g:02x}{b:02x}", tags="grad")
        canvas.tag_lower("grad")

    # ---- corpo: icone + texto + botao -----------------------------------
    def _build_body(self, parent):
        body = tk.Frame(parent, bg=FACE)
        body.pack(fill="both", expand=True, padx=16, pady=14)

        canvas = tk.Canvas(body, width=48, height=48, bg=FACE,
                           highlightthickness=0, bd=0)
        canvas.grid(row=0, column=0, rowspan=2, sticky="n", padx=(0, 16))
        draw_bulb(canvas)

        tk.Label(body, text=MESSAGE, bg=FACE, fg=TEXT, font=FONT_BODY,
                 justify="left").grid(row=0, column=1, sticky="w")

        now = datetime.now().strftime("%d/%m/%Y  %H:%M")
        tk.Label(body, text=now, bg=FACE, fg="#9a9a9a", font=FONT_BODY,
                 justify="left").grid(row=1, column=1, sticky="w", pady=(10, 0))

        sep = tk.Frame(parent, height=2, bg=DARK_EDGE)
        sep.pack(fill="x")
        tk.Frame(parent, height=1, bg=LIGHT_EDGE).pack(fill="x")

        btnrow = tk.Frame(parent, bg=FACE)
        btnrow.pack(fill="x", pady=10)
        ok = ClassicButton(btnrow, "OK", self.close)
        ok.pack()

    # ---- utilidades -----------------------------------------------------
    def _center(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw - w) // 2}+{(sh - h) // 3}")

    def _start_move(self, e):
        self._drag = (e.x_root, e.y_root)

    def _on_move(self, e):
        dx = e.x_root - self._drag[0]
        dy = e.y_root - self._drag[1]
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")
        self._drag = (e.x_root, e.y_root)

    def close(self):
        self.root.quit()      # encerra o mainloop
        self.root.destroy()   # libera os widgets

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    ReminderWindow().run()
    # garante que o processo termine (e a tarefa saia de "Em execucao")
    os._exit(0)
