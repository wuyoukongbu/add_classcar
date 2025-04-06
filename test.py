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
        self.student_code = ""  # 用户输入的studentCode

        # 存储已选课程的goodsCode
        self.selected_courses = []

        # 创建界面组件
        self.create_widgets()

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

        # 创建goodsCode输入框部分
        self.goods_code_input_frame = tk.Frame(self.root)
        self.goods_code_input_frame.pack(pady=10)

        self.goods_code_label = tk.Label(self.goods_code_input_frame, text="输入课程代码 (goodsCode),多个用逗号分隔:")
        self.goods_code_label.pack(side=tk.LEFT, padx=5)

        self.goods_code_input = tk.Entry(self.goods_code_input_frame, width=60)
        self.goods_code_input.pack(side=tk.LEFT, padx=5)

        add_button = tk.Button(self.goods_code_input_frame, text="添加课程", command=self.add_course)
        add_button.pack(side=tk.LEFT, padx=10)

        # 显示已选课程的区域
        self.selected_courses_display = tk.Text(self.root, height=5, width=80)
        self.selected_courses_display.pack(padx=10, pady=5, fill=tk.X)

        # 创建提交按钮
        submit_frame = tk.Frame(self.root)
        submit_frame.pack(pady=10)

        json_button = tk.Button(submit_frame, text="生成选课JSON", command=self.submit_selection)
        json_button.pack(side=tk.LEFT, padx=10, pady=10)

        send_request_button = tk.Button(submit_frame, text="发送选课请求", command=self.send_http_request)
        send_request_button.pack(side=tk.LEFT, padx=10, pady=10)

        # 创建结果显示区域
        result_label = tk.Label(self.root, text="选课结果:")
        result_label.pack(anchor=tk.W, padx=10)

        self.result_display = tk.Text(self.root, height=5, width=80)
        self.result_display.pack(padx=10, pady=5, fill=tk.X)

    def update_student_code(self):
        # 更新学生代码
        self.student_code = self.student_code_entry.get().strip()
        if not self.student_code:
            messagebox.showwarning("警告", "请输入学生代码 (StudentCode)")
        else:
            messagebox.showinfo("成功", f"学生代码已更新为: {self.student_code}")

    def add_course(self):
        # 获取输入的goodsCode并处理
        goods_code_input = self.goods_code_input.get().strip()
        if not goods_code_input:
            messagebox.showwarning("警告", "请输入课程代码")
            return

        # 以逗号分割多个goodsCode
        goods_codes = [code.strip() for code in goods_code_input.split("、")]

        # 将课程代码添加到已选课程中
        for code in goods_codes:
            if code not in [course['goodsCode'] for course in self.selected_courses]:
                self.selected_courses.append({
                    "goodsCode": code,
                    "goodsType": 1,
                    "students": [{
                        "studentCode": self.student_code,
                        "userId": self.user_id
                    }]
                })
                self.selected_courses_display.insert(tk.END, f"课程代码: {code}\n")

        # 清空输入框
        self.goods_code_input.delete(0, tk.END)

    def submit_selection(self):
        # 构造符合格式的JSON请求数据
        selection_data = {
            "marketingSources": "",
            "marketingSourcesExt": "",
            "systemSource": "xdfTeacher",
            "appId": "xdfTeacherApp",
            "agentName": "",
            "schoolId": "3",
            "list": self.selected_courses
        }
        json_data = json.dumps(selection_data, ensure_ascii=False, indent=4)
        self.result_display.delete(1.0, tk.END)
        self.result_display.insert(tk.END, json_data)

    def send_http_request(self):
        # 发送HTTP请求（这里的URL需要根据实际情况修改）
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

        selection_data = {
            "marketingSources": "",
            "marketingSourcesExt": "",
            "systemSource": "xdfTeacher",
            "appId": "xdfTeacherApp",
            "agentName": "",
            "schoolId": "3",
            "list": self.selected_courses
        }
        try:
            response = requests.post(url, headers=headers,json=selection_data)
            if response.status_code == 200:
                messagebox.showinfo("成功", "选课请求已发送")
                self.result_display.delete(1.0, tk.END)
                self.result_display.insert(tk.END, response.text)
            else:
                messagebox.showerror("错误", f"请求失败，状态码: {response.status_code}")
        except Exception as e:
            messagebox.showerror("网络错误", f"请求失败: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CourseSelectionApp(root)
    root.mainloop()