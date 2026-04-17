import tkinter as tk
from tkinter import ttk, messagebox
import copy
import argparse

print("Setup complete! Python + Tkinter is working.")

# ─────────────────────────────────────────────
#  ALGORITHMS
# ─────────────────────────────────────────────
def fifo(ref_string, num_frames):
    frames, queue, faults, history = [], [], 0, []
    for page in ref_string:
        fault = page not in frames
        if fault:
            faults += 1
            if len(frames) < num_frames:
                frames.append(page)
            else:
                old = queue.pop(0)
                frames[frames.index(old)] = page
            queue.append(page)
        history.append((list(frames), fault))
    return history, faults


def lru(ref_string, num_frames):
    frames, faults, history = [], 0, []
    for i, page in enumerate(ref_string):
        fault = page not in frames
        if fault:
            faults += 1
            if len(frames) < num_frames:
                frames.append(page)
            else:
                def last_used(p):
                    for j in range(i - 1, -1, -1):
                        if ref_string[j] == p:
                            return j
                    return -1
                lru_page = min(frames, key=last_used)
                frames[frames.index(lru_page)] = page
        history.append((list(frames), fault))
    return history, faults


def optimal(ref_string, num_frames):
    frames, faults, history = [], 0, []
    for i, page in enumerate(ref_string):
        fault = page not in frames
        if fault:
            faults += 1
            if len(frames) < num_frames:
                frames.append(page)
            else:
                def next_use(p):
                    for j in range(i + 1, len(ref_string)):
                        if ref_string[j] == p:
                            return j
                    return float('inf')
                victim = max(frames, key=next_use)
                frames[frames.index(victim)] = page
        history.append((list(frames), fault))
    return history, faults


# ─────────────────────────────────────────────
#  COLORS
# ─────────────────────────────────────────────
BG        = "#0B1220"
PANEL_BG  = "#111827"
ACCENT    = "#3B82F6"
FAULT_CLR = "#3A1F2B"
FAULT_TXT = "#FCA5A5"
HIT_CLR   = "#132E2A"
HIT_TXT   = "#86EFAC"
EMPTY_CLR = "#1F2937"
HDR_FG    = "#9CA3AF"
TEXT_FG   = "#E5E7EB"
TABLE_HDR = "#1D4ED8"
BORDER    = "#334155"


# ─────────────────────────────────────────────
#  APPLICATION
# ─────────────────────────────────────────────
class PageReplacementApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Smart Page Replacement Visualizer")
        self.geometry("1050x650")
        self.configure(bg=BG)
        self.resizable(True, True)
        # Start maximized for presentation/demo use.
        # On Windows, "zoomed" opens in maximized view.
        try:
            self.state("zoomed")
        except tk.TclError:
            # Fallback for platforms/window managers that don't support "zoomed".
            self.attributes("-zoomed", True)
        self.algo_var   = tk.StringVar(value="FIFO")
        self.frames_var = tk.IntVar(value=3)
        self.ref_var    = tk.StringVar(value="7 0 1 2 0 3 0 4 2 3 0 3 2")
        self._build_topbar()
        self._build_controls()
        self._build_stats_row()
        self._build_table_area()
        self._last_ref = []
        self._last_history = []
        self._last_nf = 0
        self.run_simulation()
        self.after(120, self._bring_to_front)

    def _bring_to_front(self):
        """Raise window so it appears on screen after web launch."""
        self.deiconify()
        self.lift()
        try:
            self.focus_force()
        except tk.TclError:
            pass
        # Briefly set topmost to force foreground, then restore normal behavior.
        self.attributes("-topmost", True)
        self.after(180, lambda: self.attributes("-topmost", False))

    # ── Top bar ──────────────────────────────
    def _build_topbar(self):
        bar = tk.Frame(self, bg="#0F172A", height=68)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(
            bar,
            text="  Smart Page Replacement Visualizer",
            bg="#0F172A",
            fg="#F8FAFC",
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left", pady=(10, 0))
        tk.Label(
            bar,
            text="  FIFO • LRU • Optimal",
            bg="#0F172A",
            fg="#93C5FD",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left", pady=(34, 8))

    # ── Controls ─────────────────────────────
    def _build_controls(self):
        ctrl = tk.Frame(self, bg=PANEL_BG, bd=0,
                        highlightthickness=1,
                        highlightbackground=BORDER)
        ctrl.pack(fill="x", padx=16, pady=(12, 6))

        # Reference string
        tk.Label(ctrl, text="Reference String:",
                 bg=PANEL_BG, fg=HDR_FG,
                 font=("Segoe UI", 9)).pack(side="left", padx=(12, 4), pady=10)
        tk.Entry(ctrl, textvariable=self.ref_var, width=35,
                 font=("Segoe UI", 10),
                 relief="solid", bd=1,
                 bg="#0F172A", fg=TEXT_FG,
                 insertbackground=TEXT_FG).pack(side="left", padx=(0, 16), pady=10)

        # Frames
        tk.Label(ctrl, text="Frames:",
                 bg=PANEL_BG, fg=HDR_FG,
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 4))
        tk.Spinbox(ctrl, from_=1, to=7, textvariable=self.frames_var,
                   width=4, font=("Segoe UI", 10),
                   relief="solid", bd=1,
                   bg="#0F172A", fg=TEXT_FG).pack(side="left", padx=(0, 16))

        # Algorithm
        tk.Label(ctrl, text="Algorithm:",
                 bg=PANEL_BG, fg=HDR_FG,
                 font=("Segoe UI", 9)).pack(side="left", padx=(0, 4))
        algo_menu = ttk.Combobox(ctrl, textvariable=self.algo_var,
                                 values=["FIFO", "LRU", "Optimal"],
                                 state="readonly", width=10,
                                 font=("Segoe UI", 10))
        algo_menu.pack(side="left", padx=(0, 16))

        # Run button
        tk.Button(ctrl, text="  Run Simulation  ",
                  bg=ACCENT, fg="white",
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2",
                  command=self.run_simulation).pack(side="left", pady=8)

        # Compare button
        tk.Button(ctrl, text="  Compare All  ",
                  bg="#0F6E56", fg="white",
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", cursor="hand2",
                  command=self.compare_all).pack(side="left", padx=8, pady=8)

    # ── Stats row ────────────────────────────
    def _build_stats_row(self):
        self.stats_frame = tk.Frame(self, bg=BG)
        self.stats_frame.pack(fill="x", padx=16, pady=(0, 6))

    def _update_stats(self, faults, hits, total):
        for w in self.stats_frame.winfo_children():
            w.destroy()
        ratio = (hits / total * 100) if total else 0
        data = [
            ("Page Faults",  str(faults),          "#2A1821", "#FCA5A5", "#4C1D2A"),
            ("Page Hits",    str(hits),            "#112B26", "#86EFAC", "#1C453C"),
            ("Total Refs",   str(total),           "#1A263C", "#93C5FD", "#23385A"),
            ("Hit Ratio",    f"{ratio:.1f}%",      "#112B26", "#86EFAC", "#1C453C"),
            ("Fault Ratio",  f"{100-ratio:.1f}%",  "#2A1821", "#FCA5A5", "#4C1D2A"),
        ]
        for label, value, bg, fg, border_bg in data:
            card = tk.Frame(self.stats_frame, bg=bg,
                            highlightthickness=1,
                            highlightbackground=border_bg)
            card.pack(side="left", expand=True, fill="x", padx=4)
            tk.Label(card, text=label, bg=bg, fg=HDR_FG,
                     font=("Segoe UI", 9)).pack(pady=(8, 0))
            tk.Label(card, text=value, bg=bg, fg=fg,
                     font=("Segoe UI", 15, "bold")).pack(pady=(0, 8))

    # ── Table area ───────────────────────────
    def _build_table_area(self):
        outer = tk.Frame(self, bg=PANEL_BG,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        outer.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Label
        tk.Label(outer, text="Memory Frame Visualization",
                 bg=PANEL_BG, fg=HDR_FG,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=14, pady=(12, 4))

        # Legend
        legend = tk.Frame(outer, bg=PANEL_BG)
        legend.pack(anchor="w", padx=14, pady=(0, 10))
        for color, txt in [(FAULT_CLR, "Page Fault"), (HIT_CLR, "Page Hit"), (EMPTY_CLR, "Empty")]:
            box = tk.Frame(legend, bg=color, width=18, height=18,
                           highlightthickness=1, highlightbackground=BORDER)
            box.pack(side="left", padx=(0, 4))
            tk.Label(legend, text=txt, bg=PANEL_BG, fg=HDR_FG,
                     font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 16))

        # Scrollable canvas
        container = tk.Frame(outer, bg=PANEL_BG)
        container.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self.h_scroll = tk.Scrollbar(container, orient="horizontal")
        self.h_scroll.pack(side="bottom", fill="x")

        self.canvas = tk.Canvas(container, bg=PANEL_BG,
                                highlightthickness=0,
                                xscrollcommand=self.h_scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.h_scroll.config(command=self.canvas.xview)

        self.table_frame = tk.Frame(self.canvas, bg=PANEL_BG)
        self.canvas_window = self.canvas.create_window((8, 8), window=self.table_frame, anchor="nw")
        self.table_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _on_canvas_resize(self, _event):
        # Redraw with scaled cell sizes so the table uses free space.
        if self._last_ref and self._last_history and self._last_nf:
            self._draw_table(self._last_ref, self._last_history, self._last_nf)

    # ── Draw table ───────────────────────────
    def _draw_table(self, ref_string, history, num_frames):
        for w in self.table_frame.winfo_children():
            w.destroy()

        # Cache last render input so resizing can scale the table.
        self._last_ref = list(ref_string)
        self._last_history = list(history)
        self._last_nf = num_frames

        total_cols = len(ref_string) + 1
        total_rows = num_frames + 2  # header + frame rows + fault row
        # Keep a small safety margin so scrollbars don't appear from 1-2 px overflow.
        avail_w = max(500, self.canvas.winfo_width() - 64)
        avail_h = max(280, self.canvas.winfo_height() - 56)

        # Pixel targets per cell, clamped so it still looks good with many columns.
        cell_px_w = max(32, min(84, avail_w // max(1, total_cols)))
        row_px_h = max(30, min(64, avail_h // max(1, total_rows)))

        # Approximate Label's character width and internal Y padding from pixel goals.
        left_col_w = max(7, int(cell_px_w * 1.25 // 10))
        cell_w = max(3, int(cell_px_w // 10))
        cell_ipady = max(3, (row_px_h - 20) // 2)

        label_font = ("Segoe UI", 12, "bold")
        row_label_font = ("Segoe UI", 11, "bold")

        # Let the grid consume all available table frame area.
        for c in range(total_cols):
            self.table_frame.grid_columnconfigure(c, weight=1, minsize=cell_px_w)
        for r in range(total_rows):
            self.table_frame.grid_rowconfigure(r, weight=1, minsize=row_px_h)

        # Header: page reference numbers
        tk.Label(self.table_frame, text="Frame", width=left_col_w,
                 bg=EMPTY_CLR, fg=TEXT_FG,
                 font=row_label_font,
                 relief="flat", bd=0).grid(row=0, column=0, padx=1, pady=1, ipady=cell_ipady, sticky="nsew")

        for col, page in enumerate(ref_string):
            tk.Label(self.table_frame, text=str(page), width=cell_w,
                     bg=TABLE_HDR, fg="#F8FAFC",
                     font=label_font,
                     relief="flat").grid(row=0, column=col + 1, padx=1, pady=1, ipady=cell_ipady, sticky="nsew")

        # Frame rows
        for row in range(num_frames):
            tk.Label(self.table_frame, text=f"F{row+1}", width=left_col_w,
                     bg=EMPTY_CLR, fg=TEXT_FG,
                     font=row_label_font,
                     relief="flat").grid(row=row + 1, column=0, padx=1, pady=1, ipady=cell_ipady, sticky="nsew")

            for col, (frames, fault) in enumerate(history):
                value = str(frames[row]) if row < len(frames) else ""
                if value == "":
                    bg, fg = EMPTY_CLR, HDR_FG
                elif fault and row < len(frames) and frames[row] == ref_string[col]:
                    bg, fg = FAULT_CLR, FAULT_TXT
                else:
                    bg, fg = HIT_CLR, HIT_TXT

                tk.Label(self.table_frame, text=value, width=cell_w,
                         bg=bg, fg=fg,
                         font=label_font,
                         relief="flat").grid(row=row + 1, column=col + 1,
                                             padx=1, pady=1, ipady=cell_ipady, sticky="nsew")

        # Fault indicator row
        tk.Label(self.table_frame, text="Fault?", width=left_col_w,
                 bg=EMPTY_CLR, fg=TEXT_FG,
                 font=row_label_font,
                 relief="flat").grid(row=num_frames + 1, column=0, padx=1, pady=1, ipady=cell_ipady, sticky="nsew")

        for col, (_, fault) in enumerate(history):
            text = "F" if fault else ""
            bg   = FAULT_CLR if fault else EMPTY_CLR
            fg   = FAULT_TXT if fault else HDR_FG
            tk.Label(self.table_frame, text=text, width=cell_w,
                     bg=bg, fg=fg,
                     font=row_label_font,
                     relief="flat").grid(row=num_frames + 1, column=col + 1,
                                         padx=1, pady=1, ipady=cell_ipady, sticky="nsew")

    # ── Run ──────────────────────────────────
    def run_simulation(self):
        try:
            ref = list(map(int, self.ref_var.get().split()))
            if not ref:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error",
                "Enter page numbers separated by spaces.\nExample: 7 0 1 2 0 3 0 4")
            return

        nf   = self.frames_var.get()
        algo = self.algo_var.get()

        if algo == "FIFO":
            history, faults = fifo(ref, nf)
        elif algo == "LRU":
            history, faults = lru(ref, nf)
        else:
            history, faults = optimal(ref, nf)

        hits = len(ref) - faults
        self._update_stats(faults, hits, len(ref))
        self._draw_table(ref, history, nf)

    # ── Compare all algorithms ────────────────
    def compare_all(self):
        try:
            ref = list(map(int, self.ref_var.get().split()))
            if not ref:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Enter valid page numbers first.")
            return

        nf = self.frames_var.get()
        results = {}
        results["FIFO"],    f1 = fifo(ref, nf),    fifo(ref, nf)[1]
        results["LRU"],     f2 = lru(ref, nf),     lru(ref, nf)[1]
        results["Optimal"], f3 = optimal(ref, nf), optimal(ref, nf)[1]
        _, f1 = fifo(ref, nf)
        _, f2 = lru(ref, nf)
        _, f3 = optimal(ref, nf)

        win = tk.Toplevel(self)
        win.title("Algorithm Comparison")
        win.geometry("760x330")
        win.minsize(700, 300)
        win.configure(bg=BG)
        win.resizable(True, True)

        tk.Label(win, text="Algorithm Comparison",
                 bg=BG, fg=TEXT_FG,
                 font=("Segoe UI", 13, "bold")).pack(pady=(16, 12))

        frame = tk.Frame(win, bg=PANEL_BG,
                         highlightthickness=1,
                         highlightbackground=BORDER)
        frame.pack(padx=20, pady=(0, 6), fill="x")

        headers = ["Algorithm", "Page Faults", "Page Hits", "Hit Ratio"]
        for col in range(len(headers)):
            frame.grid_columnconfigure(col, weight=1, uniform="cmp")
        for col, h in enumerate(headers):
            tk.Label(frame, text=h, bg=EMPTY_CLR, fg=TEXT_FG,
                     font=("Segoe UI", 9, "bold"),
                     relief="flat").grid(row=0, column=col, padx=1, pady=1, ipadx=12, ipady=4, sticky="nsew")

        best = min(f1, f2, f3)
        for row_i, (name, faults) in enumerate([("FIFO", f1), ("LRU", f2), ("Optimal", f3)]):
            hits  = len(ref) - faults
            ratio = f"{hits/len(ref)*100:.1f}%"
            bg    = HIT_CLR if faults == best else PANEL_BG
            fg    = HIT_TXT if faults == best else TEXT_FG
            star  = " ★" if faults == best else ""
            for col_i, val in enumerate([name + star, str(faults), str(hits), ratio]):
                tk.Label(frame, text=val, bg=bg, fg=fg,
                         font=("Segoe UI", 10, "bold" if faults == best else "normal"),
                         relief="flat").grid(row=row_i + 1, column=col_i,
                                             padx=1, pady=1, ipadx=12, ipady=5, sticky="nsew")

        tk.Label(win, text="★ Best algorithm for this input",
                 bg=BG, fg=HIT_TXT,
                 font=("Segoe UI", 9)).pack(pady=10)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
def _run_cli() -> int:
    """
    CLI mode for non-GUI environments (e.g., web button execution).
    Keeps the Tkinter UI behavior unchanged unless --cli is provided.
    """
    parser = argparse.ArgumentParser(
        description="Run paging page-replacement algorithms and print results."
    )
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode (no GUI).")
    parser.add_argument(
        "--algo",
        choices=["FIFO", "LRU", "Optimal", "ALL"],
        default="ALL",
        help="Algorithm to run.",
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=3,
        help="Number of frames (default: 3).",
    )
    parser.add_argument(
        "--ref",
        type=str,
        default="7 0 1 2 0 3 0 4 2 3 0 3 2",
        help="Reference string (space-separated integers).",
    )
    args = parser.parse_args()

    if not args.cli:
        return 2

    try:
        ref = list(map(int, args.ref.split()))
        if not ref:
            raise ValueError
    except ValueError:
        print("ERROR: --ref must be space-separated integers, e.g. '7 0 1 2 0 3 0 4'")
        return 1

    nf = args.frames
    if nf < 1:
        print("ERROR: --frames must be >= 1")
        return 1

    def summarize(name: str, run_fn):
        _, faults = run_fn(ref, nf)
        hits = len(ref) - faults
        hit_ratio = (hits / len(ref) * 100) if ref else 0.0
        fault_ratio = 100.0 - hit_ratio
        return {
            "name": name,
            "faults": faults,
            "hits": hits,
            "hit_ratio": hit_ratio,
            "fault_ratio": fault_ratio,
        }

    runs = []
    if args.algo in ("FIFO", "ALL"):
        runs.append(summarize("FIFO", fifo))
    if args.algo in ("LRU", "ALL"):
        runs.append(summarize("LRU", lru))
    if args.algo in ("Optimal", "ALL"):
        runs.append(summarize("Optimal", optimal))

    print("Page Replacement Algorithm (CLI)")
    print(f"Frames: {nf}")
    print(f"Reference string: {args.ref}")
    print("-" * 56)
    for r in runs:
        print(
            f"{r['name']:<8} | Faults: {r['faults']:<3} | Hits: {r['hits']:<3} "
            f"| Hit%: {r['hit_ratio']:.1f}% | Fault%: {r['fault_ratio']:.1f}%"
        )
    if runs:
        best = min(runs, key=lambda x: x["faults"])
        print("-" * 56)
        print(f"Best (fewest faults): {best['name']}")
    return 0

if __name__ == "__main__":
    exit_code = _run_cli()
    if exit_code == 2:
        app = PageReplacementApp()
        app.mainloop()
    else:
        raise SystemExit(exit_code)
