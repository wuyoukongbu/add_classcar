import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests


class CourseSelectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("课程选择系统")
        self.root.geometry("1200x700")

        # 固定的userId
        self.user_id = "xdf006889962"

        # 用户输入的studentCode
        self.student_code = ""

        # 存储已选课程的goodsCode
        self.selected_goods_codes = []

        # 存储课程数据（已处理成适合显示的格式）
        self.course_data = []

        # 存储所有课程按钮的引用
        self.course_buttons = {}

        # 创建界面组件
        self.create_widgets()

        # 加载内置课程数据
        self.load_hardcoded_data()

        # 自动显示课程表
        self.root.after(100, self.display_courses)

    def create_widgets(self):
        # 创建标题标签
        title_label = tk.Label(self.root, text="课程选择系统", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 创建studentCode输入框
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        student_code_label = tk.Label(input_frame, text="输入学生代码 (StudentCode):")
        student_code_label.pack(side=tk.LEFT, padx=5)

        self.student_code_entry = tk.Entry(input_frame, width=20)
        self.student_code_entry.pack(side=tk.LEFT, padx=5)

        # 更新按钮
        update_button = tk.Button(input_frame, text="更新学生代码", command=self.update_student_code)
        update_button.pack(side=tk.LEFT, padx=10)

        # 创建课程表框架（使用Canvas和Scrollbar使其可滚动）
        schedule_container = tk.Frame(self.root)
        schedule_container.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # 创建Canvas
        self.canvas = tk.Canvas(schedule_container)
        scrollbar_y = tk.Scrollbar(schedule_container, orient="vertical", command=self.canvas.yview)
        scrollbar_x = tk.Scrollbar(schedule_container, orient="horizontal", command=self.canvas.xview)

        self.schedule_frame = tk.Frame(self.canvas)

        # 配置Canvas
        self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 在Canvas上创建窗口来容纳课程表
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.schedule_frame, anchor="nw")

        # 绑定事件来调整滚动区域
        self.schedule_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        # 创建已选课程显示区域
        selection_frame = tk.Frame(self.root)
        selection_frame.pack(pady=10, fill=tk.X)

        selection_label = tk.Label(selection_frame, text="已选课程:")
        selection_label.pack(anchor=tk.W, padx=10)

        self.selected_courses_display = tk.Text(selection_frame, height=5, width=80)
        self.selected_courses_display.pack(padx=10, pady=5, fill=tk.X)

        # 创建提交按钮
        submit_frame = tk.Frame(self.root)
        submit_frame.pack(pady=10)

        # 增加两个按钮：一个用于生成JSON，一个用于发送HTTP请求
        json_button = tk.Button(submit_frame, text="生成选课JSON", command=self.submit_selection)
        json_button.pack(side=tk.LEFT, padx=10, pady=10)

        send_request_button = tk.Button(submit_frame, text="发送选课请求", command=self.send_http_request)
        send_request_button.pack(side=tk.LEFT, padx=10, pady=10)

        # 创建结果显示区域
        result_label = tk.Label(self.root, text="选课结果:")
        result_label.pack(anchor=tk.W, padx=10)

        self.result_display = tk.Text(self.root, height=5, width=80)
        self.result_display.pack(padx=10, pady=5, fill=tk.X)

    def on_frame_configure(self, event):
        # 更新Canvas的滚动区域以匹配Frame的大小
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        # 调整内部Frame的宽度以匹配Canvas
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def load_hardcoded_data(self):
        # 从JSON加载课程表数据
        raw_data = {
            "课程表": [
                {
                    "年级": "高二",
                    "季度": "暑假",
                    "日期": "7月21日",
                    "班型": "志高",
                    "时间段": [
                        {
                            "时间": "8:00-10:00",
                            "课程名": "实验C 陈思鑫",
                            "课程号": "2GCB12061"
                        },
                        {
                            "时间": "10:20-12:20",
                            "课程名": "益智 于晨",
                            "课程号": "2GMB12082"
                        },
                        {
                            "时间": "13:30-15:30",
                            "课程名": "双语 蔡晓棋",
                            "课程号": "2GYB12061"
                        },
                        {
                            "时间": "15:50-17:50",
                            "课程名": "实验P 陈展鸿",
                            "课程号": "2GPB12085"
                        }
                    ]
                },
                {
                    "年级": "高二",
                    "季度": "暑假",
                    "日期": "7月21日",
                    "班型": "志高",
                    "时间段": [
                        {
                            "时间": "10:20-12:20",
                            "课程名": "益智 付亚婷",
                            "课程号": "2GMB12084"
                        }
                    ]
                },
                {
                    "年级": "高二",
                    "季度": "暑假",
                    "日期": "8月4日",
                    "班型": "行远",
                    "时间段": [
                        {
                            "时间": "8:00-10:00",
                            "课程名": "益智 付亚婷",
                            "课程号": "2GMA12030"
                        },
                        {
                            "时间": "10:20-12:20",
                            "课程名": "双语 蔡晓棋",
                            "课程号": "2GYA12025"
                        },
                        {
                            "时间": "13:30-15:30",
                            "课程名": "实验P 陈展鸿",
                            "课程号": "2GPA12024"
                        },
                        {
                            "时间": "15:50-17:50",
                            "课程名": "益智 于晨",
                            "课程号": "2GMA12029"
                        }
                    ]
                },
                {
                    "年级": "高二",
                    "季度": "暑假",
                    "日期": "8月4日",
                    "班型": "行远",
                    "时间段": [
                        {
                            "时间": "10:20-12:20",
                            "课程名": "实验C 王秋锐",
                            "课程号": "2GCA12025"
                        }
                    ]
                },
                {
                    "年级": "高二",
                    "季度": "暑假",
                    "日期": "8月4日",
                    "班型": "志高",
                    "时间段": [
                        {
                            "时间": "8:00-10:00",
                            "课程名": "实验P 陈展鸿",
                            "课程号": "2GPB12083"
                        },
                        {
                            "时间": "10:20-12:20",
                            "课程名": "益智 于晨",
                            "课程号": "2GMB12083"
                        },
                        {
                            "时间": "13:30-15:30",
                            "课程名": "实验C 陈思鑫",
                            "课程号": "2GCB12060"
                        },
                        {
                            "时间": "15:50-17:50",
                            "课程名": "双语 余雅静",
                            "课程号": "2GYB12062"
                        }
                    ]
                },
                {
                    "年级": "高二",
                    "季度": "暑假",
                    "日期": "8月4日",
                    "班型": "志高",
                    "时间段": [
                        {
                            "时间": "13:30-15:30",
                            "课程名": "益智 付亚婷",
                            "课程号": "2GMB12081"
                        },
                        {
                            "时间": "15:50-17:50",
                            "课程名": "实验P 曾德瑞",
                            "课程号": "2GPB12084"
                        }
                    ]
                },
                {
                    "年级": "高二",
                    "季度": "秋季周六",
                    "日期": "9月6日",
                    "班型": "行远",
                    "时间段": [
                        {
                            "时间": "8:00-10:00",
                            "课程名": "益智 付亚婷",
                            "课程号": "2GMA12032"
                        },
                        {
                            "时间": "10:20-12:20",
                            "课程名": "双语 蔡晓棋",
                            "课程号": "2GYA12026"
                        },
                        {
                            "时间": "13:30-15:30",
                            "课程名": "实验P 陈展鸿",
                            "课程号": "2GPA12025"
                        },
                        {
                            "时间": "15:50-17:50",
                            "课程名": "益智 于晨",
                            "课程号": "2GMB12086"
                        },
                        {
                            "时间": "18:30-20:30",
                            "课程名": "实验C 王秋锐",
                            "课程号": "2GCA12026"
                        }
                    ]
                },
                {
                    "年级": "高二",
                    "季度": "秋季周六",
                    "日期": "9月6日",
                    "班型": "志高",
                    "时间段": [
                        {
                            "时间": "8:00-10:00",
                            "课程名": "实验P 陈展鸿",
                            "课程号": "2GPB12086"
                        },
                        {
                            "时间": "10:20-12:20",
                            "课程名": "益智 于晨",
                            "课程号": "2GMB12086"
                        },
                        {
                            "时间": "13:30-15:30",
                            "课程名": "双语 蔡晓棋",
                            "课程号": "2GYB12063"
                        },
                        {
                            "时间": "15:50-17:50",
                            "课程名": "实验C 陈思鑫",
                            "课程号": "2GCB12063"
                        },
                        {
                            "时间": "18:30-20:30",
                            "课程名": "双语 余雅静",
                            "课程号": "2GYB12064"
                        }
                    ]
                }
            ]
        }

        # 将数据转换为适合显示的格式
        self.course_data = []
        for schedule_item in raw_data["课程表"]:
            date = schedule_item["日期"]
            grade = schedule_item["年级"]
            quarter = schedule_item["季度"]
            class_type = schedule_item["班型"]

            for time_slot_item in schedule_item["时间段"]:
                time_slot = time_slot_item["时间"]

                course_info = {
                    "date": date,
                    "timeSlot": time_slot,
                    "courseName": time_slot_item["课程名"],
                    "goodsCode": time_slot_item["课程号"],
                    "grade": grade,
                    "quarter": quarter,
                    "classType": class_type
                }

                self.course_data.append(course_info)

        print("已加载内置课程数据")

    def update_student_code(self):
        # 更新学生代码
        self.student_code = self.student_code_entry.get().strip()
        if not self.student_code:
            messagebox.showwarning("警告", "请输入学生代码 (StudentCode)")
        else:
            messagebox.showinfo("成功", f"学生代码已更新为: {self.student_code}")

    def display_courses(self):
        if not self.course_data:
            messagebox.showerror("错误", "课程数据未成功加载")
            return

        # 清空之前的课程表显示
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()

        # 创建时间段和日期的唯一列表
        time_slots = sorted(set(course["timeSlot"] for course in self.course_data),
                            key=self.time_to_minutes)
        dates = sorted(set(course["date"] for course in self.course_data))

        # 创建表格标题
        tk.Label(self.schedule_frame, text="日期/时间段", font=("Arial", 10, "bold"),
                 borderwidth=1, relief="solid", width=12, height=2).grid(row=0, column=0, sticky="nsew")

        # 创建时间段列标签
        for col, time_slot in enumerate(time_slots, start=1):
            tk.Label(self.schedule_frame, text=time_slot, font=("Arial", 10, "bold"),
                     borderwidth=1, relief="solid", width=12, height=2).grid(row=0, column=col, sticky="nsew")

        # 创建日期行标签
        for row, date in enumerate(dates, start=1):
            tk.Label(self.schedule_frame, text=date, font=("Arial", 10, "bold"),
                     borderwidth=1, relief="solid", width=12, height=2).grid(row=row, column=0, sticky="nsew")

        # 创建课程单元格容器的二维字典
        course_cells = {}
        for date in dates:
            course_cells[date] = {}
            for time_slot in time_slots:
                course_cells[date][time_slot] = []

        # 将课程添加到对应的单元格列表中
        for course in self.course_data:
            date = course["date"]
            time_slot = course["timeSlot"]
            course_cells[date][time_slot].append(course)

        # 填充课程表
        for row, date in enumerate(dates, start=1):
            for col, time_slot in enumerate(time_slots, start=1):
                courses_in_cell = course_cells[date][time_slot]

                if not courses_in_cell:
                    # 如果单元格没有课程，使用空白帧占位
                    empty_frame = tk.Frame(self.schedule_frame, height=80, width=120)
                    empty_frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
                    continue

                # 创建单元格框架来容纳多个课程
                cell_frame = tk.Frame(self.schedule_frame, borderwidth=1, relief="solid")
                cell_frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

                # 在单元格中添加每个课程按钮
                for i, course in enumerate(courses_in_cell):
                    class_info = f"{course['grade']} {course['quarter']} {course['classType']}"
                    course_name = course["courseName"]
                    course_id = course["goodsCode"]

                    # 修改这里：添加课程号到按钮文本中
                    button_text = f"{course_name}\n{class_info}\n课程号: {course_id}"
                    button = tk.Button(cell_frame, text=button_text,
                                       wraplength=120, height=4, width=12,  # 增加高度以适应更多文本
                                       command=lambda c=course: self.select_course(c))
                    button.pack(fill=tk.X, padx=1, pady=1)

                    # 存储按钮引用
                    self.course_buttons[course_id] = button

                    # 如果该课程已被选中，改变按钮颜色
                    if course_id in self.selected_goods_codes:
                        button.config(bg="lightblue")

        # 配置网格的权重，使其能够随窗口大小调整
        for i in range(len(dates) + 1):
            self.schedule_frame.grid_rowconfigure(i, weight=1)
        for i in range(len(time_slots) + 1):
            self.schedule_frame.grid_columnconfigure(i, weight=1)

    def time_to_minutes(self, time_str):
        # 将时间字符串转换为分钟数，用于排序
        start_time = time_str.split("-")[0]
        hours, minutes = map(int, start_time.split(":"))
        return hours * 60 + minutes

    def select_course(self, course):
        goods_code = course.get("goodsCode", "")
        if not goods_code:
            messagebox.showerror("错误", "课程号不存在")
            return

        # 检查是否已经选择了这门课
        if goods_code in self.selected_goods_codes:
            # 如果已选择，则取消选择
            self.selected_goods_codes.remove(goods_code)
            self.course_buttons[goods_code].config(bg="SystemButtonFace")  # 恢复默认颜色
        else:
            # 如果未选择，则选择
            self.selected_goods_codes.append(goods_code)
            self.course_buttons[goods_code].config(bg="lightblue")  # 改变颜色表示已选中

        # 更新已选课程显示
        self.update_selected_courses_display()

    def update_selected_courses_display(self):
        self.selected_courses_display.delete(1.0, tk.END)

        if not self.selected_goods_codes:
            self.selected_courses_display.insert(tk.END, "尚未选择任何课程")
            return

        for i, goods_code in enumerate(self.selected_goods_codes, start=1):
            # 找到对应的课程名称
            course_name = ""
            class_info = ""
            for course in self.course_data:
                if course.get("goodsCode") == goods_code:
                    course_name = course.get("courseName", "")
                    class_info = f"{course.get('grade', '')} {course.get('quarter', '')} {course.get('classType', '')}"
                    break

            self.selected_courses_display.insert(tk.END, f"{i}. {course_name} ({class_info}) - 课程号: {goods_code}\n")

    def submit_selection(self):
        self.student_code = self.student_code_entry.get().strip()
        if not self.student_code:
            messagebox.showwarning("警告", "请输入学生代码 (StudentCode)")
            return

        if not self.selected_goods_codes:
            messagebox.showwarning("警告", "请至少选择一门课程")
            return

        # 构造最终的JSON数据
        result_data = {
            "userId": self.user_id,
            "studentCode": self.student_code,
            "selectedGoodsCodes": self.selected_goods_codes
        }

        # 显示结果
        result_json = json.dumps(result_data, indent=2, ensure_ascii=False)
        self.result_display.delete(1.0, tk.END)
        self.result_display.insert(tk.END, result_json)

        # 也可以选择将结果保存到文件
        try:
            with open("selection_result.json", "w", encoding="utf-8") as file:
                file.write(result_json)
            messagebox.showinfo("成功", "选课信息已保存到selection_result.json文件")
        except Exception as e:
            messagebox.showerror("错误", f"保存选课信息失败: {str(e)}")

    def send_http_request(self):
        self.student_code = self.student_code_entry.get().strip()
        if not self.student_code:
            messagebox.showwarning("警告", "请输入学生代码 (StudentCode)")
            return

        if not self.selected_goods_codes:
            messagebox.showwarning("警告", "请至少选择一门课程")
            return

        # 根据curl命令构造请求数据
        url = 'https://gateway.xdf.cn/web_reg_eapi/assistCart/assistAdd'

        headers = {
            'Host': 'gateway.xdf.cn',
            'Content-Type': 'application/json',
            'Origin': 'https://xubantool.xdf.cn',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': 'U2AT=; accessToken=; appVersion=5.2.45; e2e=E9EA4CE45CFDC27561245F32249BAF1A; e2mf=cea4105669b349579f48590691069546; email=chenzhanhong@xdf.cn; teacherCode=U0000289451; XDFUUID=489f5bb5-144d-805e-ea29-2865f2264bf0',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 XdfWoXueApp/5.2.45 XdfWoXueRia/3.5 XdfWoXueFullScreen/false XdfWoXueTeacher/5.2.45 xdfBridge/3.5 xdfAppVer/5.2.45 xdfAppName/woxue xdfAppOther/teacher',
            'Referer': f'https://xubantool.xdf.cn/purchaseStudent?appId=xdfTeacherApp&systemSource=xdfTeacher&schoolId=3&studentCode={self.student_code}',
            'Accept-Language': 'zh-cn'
        }

        # 构造请求Body
        list_items = []
        for goods_code in self.selected_goods_codes:
            item = {
                "goodsCode": goods_code,
                "goodsType": 1,
                "students": [
                    {
                        "studentCode": self.student_code,
                        "userId": self.user_id
                    }
                ]
            }
            list_items.append(item)

        data = {
            "marketingSources": "",
            "marketingSourcesExt": "",
            "systemSource": "xdfTeacher",
            "appId": "xdfTeacherApp",
            "agentName": "",
            "schoolId": "3",
            "list": list_items
        }

        # 将请求数据显示在结果区域
        request_json = json.dumps(data, indent=2, ensure_ascii=False)
        self.result_display.delete(1.0, tk.END)
        self.result_display.insert(tk.END, f"即将发送的请求数据:\n{request_json}\n\n")

        try:
            # 发送HTTP请求
            response = requests.post(url, headers=headers, json=data)

            # 显示响应结果
            self.result_display.insert(tk.END, f"响应状态码: {response.status_code}\n")
            self.result_display.insert(tk.END, f"响应内容:\n{response.text}")

            if response.status_code == 200:
                messagebox.showinfo("成功", "选课请求已成功发送")
            else:
                messagebox.showwarning("警告", f"请求发送成功，但服务器返回状态码: {response.status_code}")

        except Exception as e:
            self.result_display.insert(tk.END, f"发送请求时出错: {str(e)}")
            messagebox.showerror("错误", f"发送请求失败: {str(e)}")


def main():
    root = tk.Tk()
    app = CourseSelectionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()