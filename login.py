from tkinter import *
import tkinter.messagebox
from tkinter import ttk
import pymysql
import time


def center(window, w, h):  # 设置窗口大小且居中
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)
    window.geometry("{:.0f}x{:.0f}+{:.0f}+{:.0f}".format(w, h, x, y))


def get_connect():  # 获取连接
    connect = pymysql.Connect(host='localhost', port=3306, user='root', passwd='n3483226', db='psms', charset='utf8')
    return connect


def execute_sql(sql):  # 执行SQL语句并返回执行结果的游标
    connect = get_connect()
    cursor = connect.cursor()
    cursor.execute(sql)
    connect.commit()
    return cursor


class Main(Frame):
    """主窗口"""
    flag = None

    def __init__(self, master):
        Frame.__init__(self, master)
        self.pack(fill=BOTH, expand=YES)
        self.master.geometry("1200x800")
        self.master.title("宠物销售管理系统")
        self.frame_top = Frame(self)
        self.frame_top.pack(side="top", fill=X)
        Label(self.frame_top, text="宠物销售管理系统", font=("微软雅黑", 30), fg='black', bg='beige').pack(fill=X)
        self.frame_bottom = Frame(self)  # 下方frame
        self.frame_bottom.pack(side="bottom", fill=BOTH, expand=YES)
        frame_left = FrameLeft(self.frame_bottom)  # 下方左边
        frame_left.pack(side="left", fill=Y)
        self.frame_right = Home(self.frame_bottom)  # 下方右边
        self.frame_right.pack(side="right", fill=BOTH, expand=YES)


def go_home(win):  # 返回主页
    win.frame_right.destroy()
    win.frame_right = Home(Main.flag.frame_bottom)
    win.frame_right.pack(side="right", fill=BOTH, expand=YES)


def search_client(window):  # 查询， 统计客户信息
    window.frame_right.destroy()
    window.frame_right = Frame(Main.flag.frame_bottom)
    window.frame_right.pack(side="right", fill=BOTH, expand=YES)
    frame_top = Frame(window.frame_right)
    frame_top.pack(side='top', fill=BOTH)
    frame_bottom = Frame(window.frame_right)
    frame_bottom.pack(side='bottom', fill=BOTH, expand=YES)
    Label(frame_top, text='查询统计顾客信息：', font=('楷体', 18), fg='blue').pack(side='left', fill=BOTH, expand=YES)
    label_list = [Label(frame_top, text='顾客编号:'), Entry(frame_top), Label(frame_top, text='顾客姓名:'),
                  Entry(frame_top)]
    for label in label_list:
        label.pack(side="left", fill=X, expand=YES, padx=3, pady=2)
    scrollbar = Scrollbar(frame_bottom)
    scrollbar.pack(side='right', fill=Y)
    tree = ttk.Treeview(frame_bottom, columns=list(range(5)), show='headings', yscrollcommand=scrollbar.set)
    column_name = ["顾客编号", "姓名", "性别", "住址", "联系电话"]
    for i in range(5):
        tree.column(str(i), anchor='w')
        tree.heading(str(i), text=column_name[i], anchor='w')
    tree.pack(fill=BOTH, expand=YES)
    for row in execute_sql("SELECT * FROM psms.client;"):
        tree.insert('', 'end', values=row)
    scrollbar.config(command=tree.yview)

    def show_all():
        [tree.delete(item) for item in tree.get_children()]
        for new_row in execute_sql("SELECT * FROM psms.client;"):
            tree.insert('', 'end', values=new_row)

    def no_search(event):
        [tree.delete(item) for item in tree.get_children()]
        sql = "SELECT * FROM psms.client where cno={}"
        for row_search in execute_sql(sql.format(label_list[1].get())):
            tree.insert('', 'end', values=row_search)

    def name_search(event):
        [tree.delete(item) for item in tree.get_children()]
        sql = "SELECT * FROM psms.client where cname like '%{}%'"
        for row_search in execute_sql(sql.format(label_list[3].get())):
            tree.insert('', 'end', values=row_search)

    popup_menu = Menu(frame_bottom, tearoff=0)

    def is_select():  # 判断Treeview中是否有行被选中
        flag = False
        for elem in tree.selection():
            flag = True
        return flag

    def alter():  # 修改顾客信息
        if is_select():
            for elem in tree.selection():
                win = Toplevel()
                win.grab_set()  # 模态
                win.focus()
                center(win, 300, 400)
                labels = [Label(win, text='修改顾客信息', fg='blue', font=('楷体', 14)),
                          Label(win, text='顾客编号：' + tree.item(elem, 'values')[0]),
                          Label(win, text="姓名"), Entry(win),
                          Label(win, text="性别"), Entry(win),
                          Label(win, text="住址"), Entry(win),
                          Label(win, text="联系电话"), Entry(win)]
                for l in labels:
                    l.pack()

                def confirm():  # 确认添加事件
                    sql = "update client set cname='%s', csex='%s', caddress='%s', cphone='%s' where cno='%s'"
                    data = []
                    for text in labels[3::2]:  # 切片 获取Entry， 再将其上面的文本内容添加到data里
                        data.append(text.get())
                    data.append(tree.item(elem, 'values')[0])
                    try:
                        execute_sql(sql % tuple(data))  # 字符串格式化
                        tkinter.messagebox.showinfo("SUCCEED", "修改成功！")
                        show_all()
                        win.destroy()
                    except pymysql.Error:
                        tkinter.messagebox.showerror("ERROR", "输入有误！")
                        win.focus()

                Button(win, text='确认修改', command=lambda: confirm()).pack()
        else:
            tkinter.messagebox.showerror("ERROR", "未选择顾客！")

    def delete():  # 删除顾客信息
        if is_select():
            if tkinter.messagebox.askokcancel('警告', '确认删除该顾客信息吗？'):
                for elem in tree.selection():
                    try:
                        execute_sql("delete from client where cno='{}'".format(tree.item(elem, 'values')[0]))
                        tkinter.messagebox.showinfo('Succeed', '删除成功！')
                        show_all()
                    except pymysql.Error:
                        tkinter.messagebox.showerror('Failed', '删除失败，请先删除该顾客的销售记录!')
        else:
            tkinter.messagebox.showerror('ERROR', '未选择顾客！')

    def popup(event):  # 弹出右键菜单
        popup_menu.post(event.x_root, event.y_root)
    popup_menu.add_command(label='修改', command=lambda: alter())
    popup_menu.add_separator()
    popup_menu.add_command(label='删除', command=lambda: delete())
    label_list[1].bind('<Key-Return>', no_search)
    label_list[3].bind('<Key-Return>', name_search)
    button = Button(frame_top, text='显示所有', font=('楷体', 14), command=show_all)
    button.pack(side='left', fill=X, expand=YES, padx=3, pady=5)
    tree.bind("<Button-3>", popup)


def search_pet(window):  # 查询， 统计宠物信息
    window.frame_right.destroy()
    window.frame_right = Frame(Main.flag.frame_bottom)
    window.frame_right.pack(side="right", fill=BOTH, expand=YES)
    frame_top = Frame(window.frame_right)
    frame_top.pack(side='top', fill=BOTH)
    frame_bottom = Frame(window.frame_right)
    frame_bottom.pack(side='bottom', fill=BOTH, expand=YES)
    Label(frame_top, text='查询统计宠物信息：', font=('楷体', 18), fg='blue').pack(side='left', fill=BOTH, expand=YES)
    label_list = [Label(frame_top, text='宠物编号'), Entry(frame_top, width=7), Label(frame_top, text='选择宠物类型')]
    for label in label_list:
        label.pack(side="left", fill=X, expand=YES, padx=3, pady=2)
    scrollbar = Scrollbar(frame_bottom)
    scrollbar.pack(side='right', fill=Y)
    tree = ttk.Treeview(frame_bottom, columns=list(range(7)), show='headings', yscrollcommand=scrollbar.set)
    column_name = ["宠物编号", "宠物类型", "单价", "年龄", "品种", "颜色", "是否售出"]
    for i in range(7):
        tree.column(str(i), width=100, anchor='w')
        tree.heading(str(i), text=column_name[i], anchor='w')
    tree.column('3', width=120)
    tree.pack(fill=BOTH, expand=YES)
    for row in execute_sql("SELECT * FROM psms.pet;"):
        tree.insert('', 'end', values=row)
    scrollbar.config(command=tree.yview)

    def show_all():
        [tree.delete(item) for item in tree.get_children()]
        for new_row in execute_sql("SELECT * FROM psms.pet;"):
            tree.insert('', 'end', values=new_row)

    def no_search(event):
        [tree.delete(item) for item in tree.get_children()]
        sql = "SELECT * FROM psms.pet where pno={}"
        for row_search in execute_sql(sql.format(label_list[1].get())):
            tree.insert('', 'end', values=row_search)

    def show_no():
        [tree.delete(item) for item in tree.get_children()]
        for new_row in execute_sql("SELECT * FROM psms.pet where psaled='否'"):
            tree.insert('', 'end', values=new_row)

    def show_yes():
        [tree.delete(item) for item in tree.get_children()]
        for new_row in execute_sql("SELECT * FROM psms.pet where psaled='是';"):
            tree.insert('', 'end', values=new_row)

    popup_menu = Menu(frame_bottom, tearoff=0)

    def is_select():  # 判断Treeview中是否有行被选中
        flag = False
        for elem in tree.selection():
            flag = True
        return flag

    def alter():  # 修改宠物信息
        if is_select():
            for elem in tree.selection():
                win = Toplevel()
                win.grab_set()  # 模态
                win.focus()
                center(win, 300, 400)
                labels = [Label(win, text='修改宠物信息', fg='blue', font=('楷体', 14)),
                          Label(win, text='宠物编号：' + tree.item(elem, 'values')[0]),
                          Label(win, text="类型"), Entry(win),
                          Label(win, text="单价"), Entry(win),
                          Label(win, text="年龄"), Entry(win),
                          Label(win, text="品种"), Entry(win),
                          Label(win, text="颜色"), Entry(win)]
                for l in labels:
                    l.pack()

                def confirm():  # 确认添加事件
                    sql = "update psms.pet set ptype='%s', pprice=%s, page=%s, pbreed='%s', pcolor='%s' where pno='%s'"
                    data = []
                    for text in labels[3::2]:  # 切片 获取Entry， 再将其上面的文本内容添加到data里
                        data.append(text.get())
                    data.append(tree.item(elem, 'values')[0])
                    try:
                        execute_sql(sql % tuple(data))  # 字符串格式化
                        tkinter.messagebox.showinfo("SUCCEED", "修改成功！")
                        show_all()
                        win.destroy()
                    except pymysql.Error:
                        tkinter.messagebox.showerror("ERROR", "输入有误！")
                        win.focus()
                Button(win, text='确认修改', command=lambda: confirm()).pack()
        else:
            tkinter.messagebox.showerror("ERROR", "未选择宠物！")

    def delete():  # 删除宠物信息
        if is_select():
            if tkinter.messagebox.askokcancel('警告', '确认删除该宠物信息吗？'):
                for elem in tree.selection():
                    try:
                        execute_sql("delete from pet where pno='{}'".format(tree.item(elem, 'values')[0]))
                        tkinter.messagebox.showinfo('Succeed', '删除成功！')
                        show_all()
                    except pymysql.Error:
                        tkinter.messagebox.showerror('Failed', '删除失败，请先删除该宠物的销售记录!')
        else:
            tkinter.messagebox.showerror('ERROR', '未选择宠物！')

    def popup(event):  # 弹出右键菜单
        popup_menu.post(event.x_root, event.y_root)

    def price_sort():
        [tree.delete(item) for item in tree.get_children()]
        for new_row in execute_sql("SELECT * FROM psms.pet order by pprice"):
            tree.insert('', 'end', values=new_row)

    def age_sort():
        [tree.delete(item) for item in tree.get_children()]
        for new_row in execute_sql("SELECT * FROM psms.pet order by page"):
            tree.insert('', 'end', values=new_row)

    tree.heading("0", text="宠物编号", command=lambda: show_all())  # 点击表头排序
    tree.heading("2", text="单价", command=lambda: price_sort())  # 点击表头排序
    tree.heading("3", text="年龄", command=lambda: age_sort())  # 点击表头排序

    popup_menu.add_command(label='修改', command=lambda: alter())
    popup_menu.add_separator()
    popup_menu.add_command(label='删除', command=lambda: delete())

    label_list[1].bind('<Key-Return>', no_search)  # 回车 按宠物编号查询

    def show(event):
        [tree.delete(item) for item in tree.get_children()]
        for new_row in execute_sql("select * from pet where ptype='{}'".format(cmb.get())):
            tree.insert('', 'end', values=new_row)

    type_p = []
    for result in execute_sql("select distinct ptype from pet"):
        type_p.append(result)
    cmb = ttk.Combobox(frame_top, value=type_p, state='readonly', width=5)   # 添加选择宠物类型的下拉列表
    cmb.pack(side="left", fill=X, expand=YES, padx=3, pady=2)
    cmb.bind("<<ComboboxSelected>>", show)
    Label(frame_top, text='价格区间').pack(side="left", fill=X, expand=YES, padx=3, pady=2)
    left = Entry(frame_top, width=8)
    left.pack(side="left", fill=X, expand=YES, padx=0, pady=2)
    Label(frame_top, text='至').pack(side="left", fill=X, expand=YES, padx=0, pady=2)
    right = Entry(frame_top, width=8)
    right.pack(side="left", fill=X, expand=YES, padx=0, pady=2)

    def range_search(event):
        [tree.delete(item) for item in tree.get_children()]
        sql = "SELECT * FROM psms.pet where pprice>={} and pprice<={};"
        for new_row in execute_sql(sql.format(left.get(), right.get())):
            tree.insert('', 'end', values=new_row)
    right.bind('<Key-Return>', range_search)
    button_no = Button(frame_top, text='未售出', font=('楷体', 12), command=show_no)
    button_yes = Button(frame_top, text='已售出', font=('楷体', 12), command=show_yes)
    button = Button(frame_top, text='显示所有', font=('楷体', 12), command=show_all)
    button_no.pack(side='left', fill=X, expand=YES, padx=3, pady=5)
    button_yes.pack(side='left', fill=X, expand=YES, padx=3, pady=5)
    button.pack(side='left', fill=X, expand=YES, padx=3, pady=5)
    tree.bind("<Button-3>", popup)


def search_use(window):  # 查询， 统计宠物用品信息
    window.frame_right.destroy()
    window.frame_right = Frame(Main.flag.frame_bottom)
    window.frame_right.pack(side="right", fill=BOTH, expand=YES)
    frame_top = Frame(window.frame_right)
    frame_top.pack(side='top', fill=BOTH)
    frame_bottom = Frame(window.frame_right)
    frame_bottom.pack(side='bottom', fill=BOTH, expand=YES)
    Label(frame_top, text='查询统计宠物用品信息：', font=('楷体', 18), fg='blue').pack(side='left', fill=BOTH, expand=YES)
    label_list = [Label(frame_top, text='产品编号:'), Entry(frame_top), Label(frame_top, text='产品名称:'),
                  Entry(frame_top)]
    for label in label_list:
        label.pack(side="left", fill=X, expand=YES, padx=3, pady=2)
    scrollbar = Scrollbar(frame_bottom)
    scrollbar.pack(side='right', fill=Y)
    tree = ttk.Treeview(frame_bottom, columns=list(range(4)), show='headings', yscrollcommand=scrollbar.set)
    column_name = ["产品编号", "产品名称", "单价", "供货商"]
    for i in range(4):
        tree.column(str(i), anchor='w')
        tree.heading(str(i), text=column_name[i], anchor='w')
    tree.pack(fill=BOTH, expand=YES)
    for row in execute_sql("SELECT * FROM psms.use;"):
        tree.insert('', 'end', values=row)
    scrollbar.config(command=tree.yview)

    def show_all():
        [tree.delete(item) for item in tree.get_children()]
        for new_row in execute_sql("SELECT * FROM psms.use;"):
            tree.insert('', 'end', values=new_row)

    def no_search(event):
        [tree.delete(item) for item in tree.get_children()]
        sql = "SELECT * FROM psms.use where uno={}"
        for row_search in execute_sql(sql.format(label_list[1].get())):
            tree.insert('', 'end', values=row_search)

    def name_search(event):
        [tree.delete(item) for item in tree.get_children()]
        sql = "SELECT * FROM psms.use where uname like '%{}%'"
        for row_search in execute_sql(sql.format(label_list[3].get())):
            tree.insert('', 'end', values=row_search)

    popup_menu = Menu(frame_bottom, tearoff=0)

    def is_select():  # 判断Treeview中是否有行被选中
        flag = False
        for elem in tree.selection():
            flag = True
        return flag

    def alter():  # 修改宠物用品信息
        if is_select():
            for elem in tree.selection():
                win = Toplevel()
                win.grab_set()  # 模态
                win.focus()
                center(win, 300, 400)
                labels = [Label(win, text='修改宠物用品信息', fg='blue', font=('楷体', 14)),
                          Label(win, text='产品编号：' + tree.item(elem, 'values')[0]),
                          Label(win, text="产品名称"), Entry(win),
                          Label(win, text="价格"), Entry(win),
                          Label(win, text="供货商"), Entry(win)]
                for l in labels:
                    l.pack()

                def confirm():  # 确认添加事件
                    sql = "update psms.use set uname='%s', uprice='%s', uprovider='%s' where uno='%s'"
                    data = []
                    for text in labels[3::2]:  # 切片 获取Entry， 再将其上面的文本内容添加到data里
                        data.append(text.get())
                    data.append(tree.item(elem, 'values')[0])
                    try:
                        execute_sql(sql % tuple(data))  # 字符串格式化
                        tkinter.messagebox.showinfo("SUCCEED", "修改成功！")
                        show_all()
                        win.destroy()
                    except pymysql.Error:
                        tkinter.messagebox.showerror("ERROR", "输入有误！")
                        win.focus()

                Button(win, text='确认修改', command=lambda: confirm()).pack()
        else:
            tkinter.messagebox.showerror("ERROR", "未选择宠物用品！")

    def delete():  # 删除宠物用品信息
        if is_select():
            if tkinter.messagebox.askokcancel('警告', '确认删除该宠物用品吗？'):
                for elem in tree.selection():
                    try:
                        execute_sql("delete from psms.use where uno='{}'".format(tree.item(elem, 'values')[0]))
                        tkinter.messagebox.showinfo('Succeed', '删除成功！')
                        show_all()
                    except pymysql.Error:
                        tkinter.messagebox.showerror('Failed', '删除失败，请先删除该宠物用品的销售记录!')
        else:
            tkinter.messagebox.showerror('ERROR', '未选择宠物用品！')

    def popup(event):  # 弹出右键菜单
        popup_menu.post(event.x_root, event.y_root)

    def price_sort():
        [tree.delete(item) for item in tree.get_children()]
        for new_row in execute_sql("SELECT * FROM psms.use order by uprice"):
            tree.insert('', 'end', values=new_row)

    tree.heading("0", text="产品编号", command=lambda: show_all())  # 点击表头排序
    tree.heading("2", text="价格", command=lambda: price_sort())  # 点击表头排序

    popup_menu.add_command(label='修改', command=lambda: alter())
    popup_menu.add_separator()
    popup_menu.add_command(label='删除', command=lambda: delete())
    label_list[1].bind('<Key-Return>', no_search)
    label_list[3].bind('<Key-Return>', name_search)
    button = Button(frame_top, text='显示所有', font=('楷体', 14), command=show_all)
    button.pack(side='left', fill=X, expand=YES, padx=3, pady=5)
    tree.bind("<Button-3>", popup)


def search_sale(window):  # 查询， 统计销售信息
    window.frame_right.destroy()
    window.frame_right = Frame(Main.flag.frame_bottom)
    window.frame_right.pack(side="right", fill=BOTH, expand=YES)
    frame_top = Frame(window.frame_right)
    frame_top.pack(side='top', fill=BOTH)
    frame_bottom = Frame(window.frame_right)
    frame_bottom.pack(side='bottom', fill=BOTH, expand=YES)
    Label(frame_top, text='查询统计销售信息：', font=('楷体', 18), fg='blue').pack(side='left', fill=BOTH, expand=YES)
    label_list = [Label(frame_top, text='顾客编号'), Entry(frame_top, width=10),
                  Label(frame_top, text='顾客姓名'), Entry(frame_top, width=10),
                  Label(frame_top, text='宠物编号'), Entry(frame_top, width=10),
                  Label(frame_top, text='选择宠物类型')]
    for label in label_list:
        label.pack(side="left", fill=X, expand=YES, padx=3, pady=2)
    scrollbar = Scrollbar(frame_bottom)
    scrollbar.pack(side='right', fill=Y)
    tree = ttk.Treeview(frame_bottom, columns=list(range(13)), show='headings', yscrollcommand=scrollbar.set)
    column_name = ["顾客编号", "姓名", "性别", "住址", "联系电话", "宠物编号",
                   "宠物类型", "单价", "年龄", "品种", "颜色", "订单号", "销售日期"]
    for i in range(13):
        tree.column(str(i), width=50, anchor='w')
        tree.heading(str(i), text=column_name[i], anchor='w')
    tree.column('4', width=100)
    tree.column('3', width=80)
    tree.column('11', width=120)
    tree.column('12', width=80)
    tree.pack(fill=BOTH, expand=YES)
    select_all = "select client.cno, cname, csex, caddress, cphone, pet.pno, ptype, pprice, page, pbreed, " \
                 "pcolor, sno, sdate from client, pet, sale where client.cno = sale.cno and pet.pno = sale.pno"
    for row in execute_sql(select_all):
        tree.insert('', 'end', values=row)
    scrollbar.config(command=tree.yview)

    def show_all(): # 显示所有销售信息
        [tree.delete(item) for item in tree.get_children()]
        for new_row in execute_sql(select_all):
            tree.insert('', 'end', values=new_row)

    def cno_search(event):  # 按顾客编号查找
        [tree.delete(item) for item in tree.get_children()]
        sql = "select client.cno, cname, csex, caddress, cphone, pet.pno, ptype, pprice, page, pbreed, " \
                 "pcolor, sno, sdate from client, pet, sale where client.cno = sale.cno and " \
              "pet.pno = sale.pno and client.cno='{}'"
        for row_search in execute_sql(sql.format(label_list[1].get())):
            tree.insert('', 'end', values=row_search)

    def cname_search(event):  # 按顾客姓名查找
        [tree.delete(item) for item in tree.get_children()]
        sql = "select client.cno, cname, csex, caddress, cphone, pet.pno, ptype, pprice, page, pbreed, " \
                 "pcolor, sno, sdate from client, pet, sale where client.cno = sale.cno and " \
              "pet.pno = sale.pno and client.cname like '%{}%'"
        for row_search in execute_sql(sql.format(label_list[3].get())):
            tree.insert('', 'end', values=row_search)

    def pno_search(event):  # 按宠物编号查找
        [tree.delete(item) for item in tree.get_children()]
        sql = "select client.cno, cname, csex, caddress, cphone, pet.pno, ptype, pprice, page, pbreed, " \
                 "pcolor, sno, sdate from client, pet, sale where client.cno = sale.cno and " \
              "pet.pno = sale.pno and pet.pno='{}'"
        for row_search in execute_sql(sql.format(label_list[5].get())):
            tree.insert('', 'end', values=row_search)

    popup_menu = Menu(frame_bottom, tearoff=0)

    def is_select():  # 判断Treeview中是否有行被选中
        flag = False
        for elem in tree.selection():
            flag = True
        return flag

    def alter():  # 修改销售信息
        if is_select():
            for elem in tree.selection():
                win = Toplevel()
                win.grab_set()  # 模态
                win.focus()
                center(win, 300, 600)
                labels = [Label(win, text='修改销售信息', fg='blue', font=('楷体', 14)),
                          Label(win, text='订单编号：' + tree.item(elem, 'values')[0]),
                          Label(win, text="销售日期"), Entry(win)]
                for l in labels:
                    l.pack()
                Label(win, text="选择客户编号：", fg='MediumBlue', font=("楷体", 12)).pack(pady=10)
                cursor_c = execute_sql("SELECT cno FROM psms.client;")
                no_c = []
                for result in cursor_c.fetchall():  # 查询所有用户编号添加到下拉列表供用户选择
                    no_c.append(result[0])
                cmb_c = ttk.Combobox(win, value=no_c, state='readonly')
                cmb_c.pack(pady=2)
                string_show_c = [StringVar(), StringVar(), StringVar(), StringVar()]
                label_show_c = [Label(win), Label(win), Label(win), Label(win)]
                init_name_c = ['姓名:', '性别:', '家庭住址:', '电话:']
                for i in range(4):
                    string_show_c[i].set(init_name_c[i])
                    label_show_c[i]['textvariable'] = string_show_c[i]
                    label_show_c[i].pack(pady=2)

                def show_c(event):
                    sql_select = "SELECT * FROM psms.client where cno={};"
                    result_row = execute_sql(sql_select.format(cmb_c.get())).fetchone()
                    for j in range(4):
                        string_show_c[j].set(init_name_c[j] + result_row[j + 1])

                cmb_c.bind("<<ComboboxSelected>>", show_c)
                Label(win, fg='MediumBlue', font=("楷体", 12), text="选择宠物编号：").pack(pady=10)
                cursor_p = execute_sql("SELECT pno FROM psms.pet where psaled='否'")
                no_p = list()
                no_p.append(tree.item(elem, 'values')[5])
                for result in cursor_p.fetchall():  # 查询所有宠物编号名添加到下拉列表供用户选择
                    no_p.append(result[0])
                cmb_p = ttk.Combobox(win, value=no_p, state='readonly')
                cmb_p.pack(pady=2)
                string_show_p = [StringVar(), StringVar(), StringVar(), StringVar(), StringVar()]
                label_show_p = [Label(win), Label(win), Label(win), Label(win), Label(win)]
                init_name_p = ['宠物类型:', '单价:', '年龄:', '品种:', '颜色:']
                for i in range(5):
                    string_show_p[i].set(init_name_p[i])
                    label_show_p[i]['textvariable'] = string_show_p[i]
                    label_show_p[i].pack(pady=2)

                def show_p(event):
                    sql_select = "SELECT * FROM psms.pet where pno={};"
                    result_row = execute_sql(sql_select.format(cmb_p.get())).fetchone()
                    for j in range(5):
                        string_show_p[j].set(init_name_p[j] + str(result_row[j + 1]))

                cmb_p.bind("<<ComboboxSelected>>", show_p)

                def confirm():
                    sql_update = "update sale set sdate='%s', cno='%s', pno='%s' where sno= '%s'"
                    data = (labels[3].get(), cmb_c.get(), cmb_p.get(), tree.item(elem, 'values')[11])
                    try:
                        execute_sql(sql_update % data)
                        tkinter.messagebox.showinfo("SUCCEED", "修改成功")
                        execute_sql("update pet set psaled='是' where pno='{}'".format(cmb_p.get()))
                        win.destroy()
                        show_all()
                    except pymysql.Error:
                        tkinter.messagebox.showerror("Failed", "修改失败")
                        win.focus()

                Button(win, text='确认修改', command=lambda: confirm()).pack(pady=20)
        else:
            tkinter.messagebox.showerror("ERROR", "未选择销售信息！")

    def delete():  # 删除宠物信息
        if is_select():
            if tkinter.messagebox.askokcancel('警告', '确认删除该销售信息吗？'):
                for elem in tree.selection():
                    try:
                        execute_sql("delete from sale where sno='{}'".format(tree.item(elem, 'values')[11]))
                        tkinter.messagebox.showinfo('Succeed', '删除成功！')
                        show_all()
                    except pymysql.Error:
                        tkinter.messagebox.showerror('Failed', '删除失败!')
        else:
            tkinter.messagebox.showerror('ERROR', '未选择销售信息！')

    def popup(event):  # 弹出右键菜单
        popup_menu.post(event.x_root, event.y_root)

    def price_sort():
        [tree.delete(item) for item in tree.get_children()]
        for new_row in execute_sql(select_all + " order by pprice"):
            tree.insert('', 'end', values=new_row)

    def date_sort():
        [tree.delete(item) for item in tree.get_children()]
        for new_row in execute_sql(select_all + " order by sdate"):
            tree.insert('', 'end', values=new_row)

    tree.heading("7", text="单价", command=lambda: price_sort())  # 点击表头排序
    tree.heading("12", text="销售日期", command=lambda: date_sort())  # 点击表头排序

    popup_menu.add_command(label='修改', command=lambda: alter())
    popup_menu.add_separator()
    popup_menu.add_command(label='删除', command=lambda: delete())

    label_list[1].bind('<Key-Return>', cno_search)  # 回车 按顾客编号查询
    label_list[3].bind('<Key-Return>', cname_search)  # 回车 按顾客姓名查询
    label_list[5].bind('<Key-Return>', pno_search)  # 回车 按宠物编号查询

    def show(event):
        [tree.delete(item) for item in tree.get_children()]
        sql = "select client.cno, cname, csex, caddress, cphone, pet.pno, ptype, pprice, page, pbreed, " \
                 "pcolor, sno, sdate from client, pet, sale " \
              "where client.cno = sale.cno and pet.pno = sale.pno and pet.ptype='{}'"
        for new_row in execute_sql(sql.format(cmb.get())):
            tree.insert('', 'end', values=new_row)

    type_p = []
    sql = "select distinct ptype from client,pet,sale where client.cno=sale.cno and pet.pno=sale.pno"
    for result in execute_sql(sql):
        type_p.append(result)
    cmb = ttk.Combobox(frame_top, value=type_p, state='readonly', width=5)   # 添加选择宠物类型的下拉列表
    cmb.pack(side="left", fill=X, expand=YES, padx=3, pady=2)
    cmb.bind("<<ComboboxSelected>>", show)

    button = Button(frame_top, text='显示所有', font=('楷体', 14), command=show_all)
    button.pack(side='left', fill=X, expand=YES, padx=3, pady=5)
    tree.bind("<Button-3>", popup)


def add_sale(win):  # 添加订单信息
    win.frame_right.destroy()
    win.frame_right = Frame(Main.flag.frame_bottom)
    win.frame_right.pack(side='right', fill=BOTH, expand=YES)
    Label(win.frame_right, text="添  加   订   单   信   息：", fg='blue', font=('华文彩云', 16)).pack(pady=10)
    string_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
    Label(win.frame_right, text='订单号：' + string_time).pack(pady=10)
    Label(win.frame_right, text="销售日期：" + time.strftime("%Y-%m-%d", time.localtime())).pack(pady=10)
    Label(win.frame_right, text="选择客户编号：", fg='MediumBlue', font=("楷体", 14)).pack(pady=10)
    cursor_c = execute_sql("SELECT cno FROM psms.client;")
    no_c = []
    for result in cursor_c.fetchall():  # 查询所有用户编号添加到下拉列表供用户选择
        no_c.append(result[0])
    cmb_c = ttk.Combobox(win.frame_right, value=no_c, state='readonly')
    cmb_c.pack(pady=2)
    string_show_c = [StringVar(), StringVar(), StringVar(), StringVar()]
    label_show_c = [Label(win.frame_right), Label(win.frame_right), Label(win.frame_right), Label(win.frame_right)]
    init_name_c = ['姓名:', '性别:', '家庭住址:', '电话:']
    for i in range(4):
        string_show_c[i].set(init_name_c[i])
        label_show_c[i]['textvariable'] = string_show_c[i]
        label_show_c[i].pack(pady=2)

    def show_c(event):
        global string_time
        string_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        sql_select = "SELECT * FROM psms.client where cno={};"
        result_row = execute_sql(sql_select.format(cmb_c.get())).fetchone()
        for j in range(4):
            string_show_c[j].set(init_name_c[j] + result_row[j + 1])

    cmb_c.bind("<<ComboboxSelected>>", show_c)

    Label(win.frame_right, fg='MediumBlue', font=("楷体", 14), text="选择宠物编号：").pack(pady=10)
    cursor_p = execute_sql("SELECT pno FROM psms.pet where psaled='否';")
    no_p = []
    for result in cursor_p.fetchall():  # 查询所有未售出宠物编号名添加到下拉列表供用户选择
        no_p.append(result[0])
    cmb_p = ttk.Combobox(win.frame_right, value=no_p, state='readonly')
    cmb_p.pack(pady=2)
    string_show_p = [StringVar(), StringVar(), StringVar(), StringVar(), StringVar()]
    label_show_p = [Label(win.frame_right), Label(win.frame_right),
                    Label(win.frame_right), Label(win.frame_right), Label(win.frame_right)]
    init_name_p = ['宠物类型:', '单价:', '年龄:', '品种:', '颜色:']
    for i in range(5):
        string_show_p[i].set(init_name_p[i])
        label_show_p[i]['textvariable'] = string_show_p[i]
        label_show_p[i].pack(pady=2)

    def show_p(event):
        global string_time
        string_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        sql_select = "SELECT * FROM psms.pet where pno={};"
        result_row = execute_sql(sql_select.format(cmb_p.get())).fetchone()
        for j in range(5):
            string_show_p[j].set(init_name_p[j] + str(result_row[j + 1]))

    cmb_p.bind("<<ComboboxSelected>>", show_p)

    def confirm():
        global string_time
        sql = "insert into psms.sale values(%s, '%s', %s, %s);"
        data = (string_time, time.strftime("%Y-%m-%d", time.localtime()), cmb_c.get(), cmb_p.get())
        try:
            execute_sql(sql % data)
            tkinter.messagebox.showinfo("SUCCEED", "添加成功")
            execute_sql("update pet set psaled='是' where pno='{}'".format(cmb_p.get()))
        except pymysql.Error:
            tkinter.messagebox.showerror("Failed", "添加失败")

    Button(win.frame_right, text='确认添加', command=lambda: confirm()).pack(pady=20)


class FrameLeft(Frame):  # 左侧菜单栏
    def __init__(self, master):
        Frame.__init__(self, master, bg='gray', width=180, borderwidth=2)
        self.pack_propagate(False)  # 如果Frame中添加了其它组件，frame大小会变化， 用此方法固定frame大小
        self.create()

    def create(self):
        Button(self, text="主      页", bg='#7fffd4', font=('华文琥珀', 16), command=lambda: go_home(Main.flag)).pack(fill=X)
        Label(self, text="统计信息", bg='maroon1', fg='blue', font=("楷体", 16)).pack(fill=X)
        Button(self, text="统计顾客信息", command=lambda: search_client(Main.flag)).pack(fill=X)
        Button(self, text="统计宠物信息", command=lambda: search_pet(Main.flag)).pack(fill=X)
        Button(self, text="统计宠物用品信息", command=lambda: search_use(Main.flag)).pack(fill=X)
        Button(self, text="统计销售信息", command=lambda: search_sale(Main.flag)).pack(fill=X)
        Label(self, text="录入信息", bg='maroon1', fg='blue', font=("楷体", 16)).pack(fill=X)
        Button(self, text="添加顾客", command=lambda: self.add_user()).pack(fill=X)
        Button(self, text="添加宠物", command=lambda: self.add_pet()).pack(fill=X)
        Button(self, text="添加宠物用品", command=lambda: self.add_use()).pack(fill=X)
        Button(self, text="添加销售信息", command=lambda: add_sale(Main.flag)).pack(fill=X)

        def quit_sys():
            if tkinter.messagebox.askokcancel('提示', '确认退出吗？'):
                sys.exit(0)

        Button(self, text="退出系统", fg='blue', font=('楷体', 14), command=lambda: quit_sys()).pack(fill=X)

    @staticmethod
    def add_user():  # 添加用户信息事件
        win = Toplevel()
        win.grab_set()
        win.focus()
        center(win, 300, 400)
        labels = [Label(win, text='顾客编号'), Entry(win),
                  Label(win, text="姓名"), Entry(win),
                  Label(win, text="性别"), Entry(win),
                  Label(win, text="住址"), Entry(win),
                  Label(win, text="联系电话"), Entry(win)]
        for label in labels:
            label.pack()

        def confirm():  # 确认添加事件
            sql = "insert into client values('%s', '%s', '%s', '%s', '%s');"
            data = []
            for text in labels[1::2]:  # 切片 获取Entry， 再将其上面的文本内容添加到data里
                data.append(text.get())
            try:
                execute_sql(sql % tuple(data))  # 字符串格式化
                tkinter.messagebox.showinfo("SUCCEED", "录入成功！")
                win.destroy()
            except pymysql.Error:
                tkinter.messagebox.showerror("ERROR", "输入有误！")
                win.focus()

        Button(win, text='确认', command=lambda: confirm()).pack()

    @staticmethod
    def add_pet():  # 添加宠物事件
        win = Toplevel()
        win.grab_set()
        win.focus()
        center(win, 300, 400)
        labels = [Label(win, text='宠物编号'), Entry(win),
                  Label(win, text="宠物类型"), Entry(win),
                  Label(win, text="单价"), Entry(win),
                  Label(win, text="年龄"), Entry(win),
                  Label(win, text="品种"), Entry(win),
                  Label(win, text="颜色"), Entry(win)]
        for label in labels:
            label.pack()

        def confirm():  # 确认添加事件
            sql = "insert into pet values('%s', '%s', '%s', '%s', '%s', '%s', '否')"
            data = []
            for text in labels[1::2]:
                data.append(text.get())
            try:
                execute_sql(sql % tuple(data))
                tkinter.messagebox.showinfo("SUCCEED", "录入成功！")
                win.destroy()
            except pymysql.Error:
                tkinter.messagebox.showerror("ERROR", "输入有误！")
                win.focus()

        Button(win, text='确认', command=lambda: confirm()).pack()

    @staticmethod
    def add_use():  # 添加宠物用品事件
        win = Toplevel()
        win.grab_set()
        win.focus()
        center(win, 300, 360)
        labels = [Label(win, text='产品编号'), Entry(win),
                  Label(win, text="产品名称"), Entry(win),
                  Label(win, text="单价"), Entry(win),
                  Label(win, text="供货商"), Entry(win)]
        for label in labels:
            label.pack()

        def confirm():  # 确认添加事件
            sql = "insert into psms.use values('%s', '%s', '%s', '%s')"
            data = []
            for text in labels[1::2]:
                data.append(text.get())
            try:
                execute_sql(sql % tuple(data))
                tkinter.messagebox.showinfo("SUCCEED", "录入成功！")
                win.destroy()
            except pymysql.Error:
                tkinter.messagebox.showerror("ERROR", "输入有误！")
                win.focus()

        Button(win, text='确认', command=lambda: confirm()).pack()


class Home(Frame):  # 主页
    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, text=time.strftime('%Y-%m-%d %H:%M:%S %A', time.localtime(time.time()))
                           , font=("Arial Black", 24))
        self.label.after(1000, self.trickit)
        self.label.pack(pady=20)

    def trickit(self):
        currentTime = time.strftime('%Y-%m-%d %H:%M:%S %A', time.localtime(time.time()))
        self.label.config(text=currentTime)
        self.update()
        self.label.after(1000, self.trickit)


root = Tk()  # 登陆界面
center(root, 600, 440)
root.resizable(0, 0)
root.title("宠物销售管理系统")
frame = Frame(root)
frame.place(x=180, y=200)
label_1 = Label(frame, text="账号：", font=("宋体", 12))
label_1.grid(row=0, column=0, pady=5)
entry = Entry(frame, show=None, font=("Arial", 12))
entry.grid(row=0, column=1)
entry.focus()
label_2 = Label(frame, text="密码：", font=("宋体", 12))
label_2.grid(row=1, column=0)
entry_password = Entry(frame, show="*", font=("Arial", 12))
entry_password.grid(row=1, column=1, pady=5)


def sign_in(event):  # 登录
    cursor = get_connect().cursor()
    sql = "select password from admin where user=" + entry.get()
    try:
        cursor.execute(sql)
        password_input = entry_password.get()  # 获取用户输入的密码
        password_db = (cursor.fetchone())[0]  # 获取数据中的密码
        if password_input == password_db:  # 判断用户输入的密码与数据库中的是否一致
            tkinter.messagebox.showinfo(title="succeed", message="登陆成功")
            root.destroy()  # 销毁当前窗口
            new_win = Tk()  # 进入主界面
            # center(root, root.winfo_screenwidth(), root.winfo_screenheight())  # 最大化，效果不好
            center(new_win, 1200, 800)
            new_win.title("宠物销售管理系统")
            app = Main(new_win)
            Main.flag = app
            center(app.master, 1200, 800)
        else:
            tkinter.messagebox.showerror(title="failed", message="密码错误")
    except (pymysql.Error, TypeError):
        tkinter.messagebox.showerror(title="failed", message="密码错误")


entry_password.bind('<Key-Return>', sign_in)  # 密码输入框回车登录
button_sign_in = Button(frame, text='     登        录      ', fg='black', command=lambda: sign_in(None))
button_sign_in.grid(row=2, column=1)

root.mainloop()
