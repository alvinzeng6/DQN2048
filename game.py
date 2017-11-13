#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Gabriele Cirulli's 2048 puzzle game.

    Python3/tkinter port by Raphaël Seban <motus@laposte.net>

    Copyright (c) 2014+ Raphaël Seban for the present code.

    This program is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of
    the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.

    If not, see http://www.gnu.org/licenses/
"""

import random
import copy
import numpy as np
import time
import pickle

try:
    import tkinter as tk
    import ttk
    import tkMessageBox as messagebox
except:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import messagebox
# end try

from src import game2048_score as GS
from src import game2048_grid as GG


class GabrieleCirulli2048(tk.Tk):
    PADDING = 10  # 控制界面的
    START_TILES = 2  # 初始化几个方格

    def __init__(self, **kw):
        tk.Tk.__init__(self)
        self.train = kw.get("train", 0)
        self.ai_time = 100
        self.train = 1
        self.initialize(**kw)

    def center_window(self, tk_event=None, *args, **kw):
        self.update_idletasks()
        _width = self.winfo_reqwidth()
        _height = self.winfo_reqheight()
        _screen_width = self.winfo_screenwidth()
        _screen_height = self.winfo_screenheight()
        _left = (_screen_width - _width) // 2
        _top = (_screen_height - _height) // 2
        self.geometry("+{x}+{y}".format(x=_left, y=_top))

    def initialize(self, **kw):
        self.title("2048")  # 标题
        self.protocol("WM_DELETE_WINDOW", self.quit_app)  # 退出协议
        self.resizable(width=False, height=False)  # 设置不可调
        self.withdraw()
        ttk.Style().configure(".", font="sans 10")  # 样式
        _pad = self.PADDING
        self.hint = ttk.Label(
            self, text="Hint: use keyboard arrows to move tiles."
        )
        self.grid = GG.Game2048Grid(self, **kw)  # 窗格
        self.score = GS.Game2048Score(self, **kw)
        self.hiscore = GS.Game2048Score(self, label="Highest:", **kw)
        self.grid.pack(side=tk.TOP, padx=_pad, pady=_pad)
        self.hint.pack(side=tk.TOP)
        self.score.pack(side=tk.LEFT)
        self.hiscore.pack(side=tk.LEFT)
        ttk.Button(
            self, text="Quit!", command=self.quit_app,
        ).pack(side=tk.RIGHT, padx=_pad, pady=_pad)
        ttk.Button(
            self, text="New Game", command=self.new_game,
        ).pack(side=tk.RIGHT)
        ttk.Button(
            self, text="AI Game", command=self.ai_new_game,
        ).pack(side=tk.RIGHT)
        self.grid.set_score_callback(self.update_score)

        # define your AI variable here

    def new_game(self, *args, **kw):
        self.unbind_all("<Key>")
        self.score.reset_score()
        self.grid.reset_grid()
        for n in range(self.START_TILES):
            self.after(
                100 * random.randrange(3, 7), self.grid.pop_tile
            )
        self.bind_all("<Key>", self.on_keypressed)

    def quit_app(self, **kw):
        if messagebox.askokcancel("Question", "Quit game?"):
            self.quit()
            self.destroy()

    def run(self, **kw):
        if self.train:
            self.ai_train()
        else:
            self.center_window()
            self.deiconify()
            self.new_game(**kw)
            self.mainloop()

    def on_keypressed(self, tk_event=None, *args, **kw):
        # old = self.score.get_score()
        _event_handler = {
            "left": self.grid.move_tiles_left,
            "right": self.grid.move_tiles_right,
            "up": self.grid.move_tiles_up,
            "down": self.grid.move_tiles_down,
            "escape": self.quit_app,
        }.get(tk_event.keysym.lower())
        try:
            _event_handler()
            self.hint.pack_forget()
        except:
            pass

        tiles = self.grid.tiles  # 包含的窗格的地方和值
        # print("tiles = {}".format(tiles))
        for t in tiles:
            print("Tile id = {}, tile row = {}, tile column = {}, value = {}".
                  format(t, tiles[t].row, tiles[t].column, tiles[t].value))
        print("--------------------------")
        # new = self.score.get_score() # 读取总分数
        # print(new - old)
        # end try

    def update_score(self, value, mode="add"):
        if str(mode).lower() in ("add", "inc", "+"):
            self.score.add_score(value)
        else:
            self.score.set_score(value)

        self.hiscore.high_score(self.score.get_score())

    def ai_new_game(self, *args, **kw):
        self.unbind_all("<Key>")
        self.score.reset_score()
        self.grid.reset_grid()
        for n in range(self.START_TILES):
            self.after(
                10 * random.randrange(3, 7), self.grid.pop_tile
            )

        self.playloops = 0
        self.after(self.ai_time, self.ai_pressed)  # 多长时间后调用下一次ai_pressed
        self.bind_all("<Key>", self.on_keypressed)

    # 定义一个AI程序，按了界面上的ai运行按钮后会定时触发
    # 在这个子程序里面运行一次AI操作
    def ai_pressed(self, tk_event=None, *args, **kw):
        if not self.train:
            matrix = self.grid.matrix.matrix
        # get the values of cells
        self.playloops = self.playloops + 1
        mat2048 = np.zeros((4, 4))
        tiles = self.grid.tiles
        for t in tiles:
            # put values into a matrix
            mat2048[tiles[t].row, tiles[t].column] = np.log2(tiles[t].value)
            # print("Tile id = {}, tile row = {}, tile column = {}, value = {}".
            #       format(t, tiles[t].row, tiles[t].column, tiles[t].value))
        # print(mat2048)
        # print("--------------------------")
        # add your AI program here to control the game
        # the control input is a number from 1-4
        # 1 move to left
        # 2 move to right
        # 3 move to up
        # 4 move to down
        # pressed = int(random.choice((1, 2, 3, 4)))
        pressed = self.ai_move(mat2048)  # this is random control
        if self.playloops == 1 and self.train:
            start = time.clock()
        if pressed == 1:
            if not self.train:
                print("Move left\n")
            self.grid.move_tiles_left()
        elif pressed == 2:
            if not self.train:
                print("Move right\n")
            self.grid.move_tiles_right()
        elif pressed == 3:
            if not self.train:
                print("Move up\n")
            self.grid.move_tiles_up()
        elif pressed == 4:
            if not self.train:
                print("Move down\n")
            self.grid.move_tiles_down()
        else:
            pass
        if self.playloops == 1 and self.train:
            end = time.clock()
            print("时间：", (end - start) * 100, 's')
        if self.grid.no_more_hints():  # game over
            # self.ai_new_game()  # play ai again
            pass
        else:
            if not self.train:
                self.after(self.ai_time, self.ai_pressed)  # ai press again after 200 ms
            else:
                self.ai_pressed()

    # 修改这个子程序
    def ai_move(self, mat2048):
        # 输入是2048表格的2对数，输出1~4，表示上下左右
        return random.randint(1, 4)

    def ai_train(self, epi=1000):
        for i in range(epi):
            self.playloops = 0
            if i == 5:
                print("woshiyixia")
                pass
            self.score.reset_score()
            self.grid.clear_all()
            for n in range(self.START_TILES):
                self.grid.pop_tile()  # 对象加1
            self.ai_pressed()
            print(i + 1, '循环次数：', self.playloops)
        print("训练结束")
        self.train = 0


if __name__ == "__main__":
    GabrieleCirulli2048(train=1).run()
