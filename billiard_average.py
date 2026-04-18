import tkinter as tk
from pathlib import Path
from tkinter import messagebox
import json
import os


class Match:
    def __init__(self, points, innings, game_type):
        self.points = points
        self.innings = innings
        self.game_type = game_type
        self.avg = points / innings if innings > 0 else 0


class AverageTracker:
    def __init__(self, max_matches=30):
        self.max_matches = max_matches
        self.matches = []
        self.save_file = Path(__file__).resolve().parent / "matches.json"
        self.load()

    def add_match(self, points, innings, game_type):
        if innings <= 0:
            raise ValueError("Innings must be greater than 0")

        match = Match(points, innings, game_type)
        self.matches.append(match)

        # enforce 30 per game type
        filtered = [m for m in self.matches if m.game_type == game_type]
        if len(filtered) > self.max_matches:
            for i, m in enumerate(self.matches):
                if m.game_type == game_type:
                    del self.matches[i]
                    break

    def remove_last_match(self, game_type):
        for i in range(len(self.matches) - 1, -1, -1):
            if self.matches[i].game_type == game_type:
                del self.matches[i]
                return

    def get_matches(self, game_type):
        return [m for m in self.matches if m.game_type == game_type]

    def overall_average(self, game_type):
        matches = self.get_matches(game_type)
        if not matches:
            return 0

        total_points = sum(m.points for m in matches)
        total_innings = sum(m.innings for m in matches)

        return total_points / total_innings

    def save(self):
        data = [
            {
                "points": m.points,
                "innings": m.innings,
                "game_type": m.game_type
            }
            for m in self.matches
        ]

        with open(self.save_file, "w") as f:
            json.dump(data, f)

    def load(self):
        if not os.path.exists(self.save_file):
            return

        with open(self.save_file, "r") as f:
            data = json.load(f)

        for item in data:
            game_type = item.get("game_type", "Straight Rail")
            self.matches.append(Match(item["points"], item["innings"], game_type))


class AverageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Billiard Average Tracker")
        self.root.geometry("450x450")
        self.root.configure(bg="black")

        self.tracker = AverageTracker()
        self.game_type_var = tk.StringVar(value="Straight Rail")

        self.create_widgets()
        self.bind_keys()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.update_display()

    def create_widgets(self):
        input_frame = tk.Frame(self.root, bg="black")
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Game", bg="black", fg="white").grid(row=0, column=0)

        game_menu = tk.OptionMenu(
            input_frame,
            self.game_type_var,
            "Straight Rail",
            "1 Cushion",
            "3 Cushion",
            command=lambda _: self.update_display()
        )
        game_menu.config(bg="black", fg="white")
        game_menu.grid(row=1, column=0, padx=5)

        tk.Label(input_frame, text="Points", bg="black", fg="white").grid(row=0, column=1)
        tk.Label(input_frame, text="Innings", bg="black", fg="white").grid(row=0, column=2)

        self.points_entry = tk.Entry(input_frame, width=8, bg="black", fg="white", insertbackground="white")
        self.innings_entry = tk.Entry(input_frame, width=8, bg="black", fg="white", insertbackground="white")

        self.points_entry.grid(row=1, column=1, padx=5)
        self.innings_entry.grid(row=1, column=2, padx=5)

        tk.Button(
            input_frame,
            text="Add",
            command=self.add_match,
            bg="black",
            fg="white"
        ).grid(row=1, column=3, padx=5)

        tk.Button(
            input_frame,
            text="Undo",
            command=self.undo_last,
            bg="black",
            fg="white"
        ).grid(row=1, column=4, padx=5)

        self.listbox = tk.Listbox(self.root, bg="black", fg="white", width=55)
        self.listbox.pack(pady=10, fill="both", expand=True)

        self.avg_label = tk.Label(
            self.root,
            text="Overall Avg: 0.00",
            bg="black",
            fg="white",
            font=("Arial", 14, "bold")
        )
        self.avg_label.pack(pady=10)

    def bind_keys(self):
        self.root.bind("<Return>", lambda e: self.add_match())
        self.root.bind("u", lambda e: self.undo_last())

    def add_match(self):
        try:
            points = int(self.points_entry.get())
            innings = int(self.innings_entry.get())
            game_type = self.game_type_var.get()

            self.tracker.add_match(points, innings, game_type)
            self.tracker.save()

            self.update_display()

            self.points_entry.delete(0, tk.END)
            self.innings_entry.delete(0, tk.END)

        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def undo_last(self):
        game_type = self.game_type_var.get()
        self.tracker.remove_last_match(game_type)
        self.tracker.save()
        self.update_display()

    def update_display(self):
        self.listbox.delete(0, tk.END)

        game_type = self.game_type_var.get()
        matches = self.tracker.get_matches(game_type)

        if not matches:
            self.avg_label.config(text=f"{game_type} Avg: 0.00")
            return

        avgs = [m.avg for m in matches]
        best = max(avgs)
        worst = min(avgs)

        for i, m in enumerate(matches):
            self.listbox.insert(
                tk.END,
                f"{i+1}: {m.points} pts / {m.innings} inn = {m.avg:.2f}"
            )

            if m.avg == best:
                self.listbox.itemconfig(i, fg="lime")
            elif m.avg == worst:
                self.listbox.itemconfig(i, fg="red")

        avg = self.tracker.overall_average(game_type)
        self.avg_label.config(text=f"{game_type} Avg: {avg:.2f}")

    def on_close(self):
        self.tracker.save()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AverageApp(root)
    root.mainloop()
