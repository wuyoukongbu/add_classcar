import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests


class CourseSelectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("课程选择系统")
        self.root.geometry("800x500")

        # 固定的userId
        self.user_id = "xdf006889962"

        # 创建界面组件
        self.create_widgets()

    def create_widgets(self):
        # 创建标题标签
        title_label = tk.Label(self.root, text="购物车添加系统", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # 输入区域容器
        input_container = tk.Frame(self.root)
        input_container.pack(pady=20, padx=20, fill=tk.X)

        # 学生代码输入部分
        student_frame = tk.Frame(input_container)
        student_frame.pack(fill=tk.X, pady=5)

        tk.Label(student_frame, text="学员号:").pack(side=tk.LEFT)
        self.student_code_entry = tk.Entry(student_frame, width=40)
        self.student_code_entry.pack(side=tk.LEFT, padx=10)

        # 课程代码输入部分
        course_frame = tk.Frame(input_container)
        course_frame.pack(fill=tk.X, pady=5)

        tk.Label(course_frame, text="班号 (多个班级用中文顿号、分隔):").pack(side=tk.LEFT)
        self.goods_code_entry = tk.Entry(course_frame, width=60)
        self.goods_code_entry.pack(side=tk.LEFT, padx=10)

        # 按钮区域
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="生成选课列表", command=self.submit_selection).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="发送选课请求", command=self.send_http_request).pack(side=tk.LEFT, padx=10)

        # 结果显示区域
        result_frame = tk.Frame(self.root)
        result_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        tk.Label(result_frame, text="操作结果:").pack(anchor=tk.W)
        self.result_text = tk.Text(result_frame, height=15, wrap=tk.WORD)
        self.result_text.pack(fill=tk.BOTH, expand=True)

    def get_input_data(self):
        """验证并获取输入数据"""
        student_code = self.student_code_entry.get().strip()
        goods_codes = self.goods_code_entry.get().strip()

        if not student_code:
            messagebox.showwarning("警告", "请输入学生代码")
            return None, None

        if not goods_codes:
            messagebox.showwarning("警告", "请输入课程代码")
            return None, None

        return student_code, [code.strip() for code in goods_codes.split("、")]

    def build_request_data(self, student_code, goods_codes):
        """构建请求数据结构"""
        return {
            "marketingSources": "",
            "marketingSourcesExt": "",
            "systemSource": "xdfTeacher",
            "appId": "xdfTeacherApp",
            "agentName": "",
            "schoolId": "3",
            "list": [{
                "goodsCode": code,
                "goodsType": 1,
                "students": [{
                    "studentCode": student_code,
                    "userId": self.user_id
                }]
            } for code in goods_codes]
        }

    def submit_selection(self):
        """生成JSON数据"""
        student_code, goods_codes = self.get_input_data()
        if not student_code or not goods_codes:
            return

        try:
            request_data = self.build_request_data(student_code, goods_codes)
            json_data = json.dumps(request_data, ensure_ascii=False, indent=4)
            self.show_result("生成的JSON数据:\n" + json_data)
        except Exception as e:
            messagebox.showerror("错误", f"生成JSON失败: {str(e)}")

    def send_http_request(self):
        """发送HTTP请求"""
        student_code, goods_codes = self.get_input_data()
        if not student_code or not goods_codes:
            return

        url = 'https://gateway.xdf.cn/web_reg_eapi/assistCart/assistAdd'
        headers = {
            'Host': 'gateway.xdf.cn',
            'Content-Type': 'application/json',
            'Origin': 'https://xubantool.xdf.cn',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cookie': 'U2AT=; accessToken=; appVersion=5.2.45; e2e=E9EA4CE45CFDC27561245F32249BAF1A; e2mf=0353ed7df6bf4df7be7da24780c23e56; email=chenzhanhong@xdf.cn; teacherCode=U0000289451; XDFUUID=489f5bb5-144d-805e-ea29-2865f2264bf0',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 XdfWoXueApp/5.2.45 XdfWoXueRia/3.5 XdfWoXueFullScreen/false XdfWoXueTeacher/5.2.45 xdfBridge/3.5 xdfAppVer/5.2.45 xdfAppName/woxue xdfAppOther/teacher',
            'Referer': f'https://xubantool.xdf.cn/purchaseStudent?appId=xdfTeacherApp&systemSource=xdfTeacher&schoolId=3&studentCode={student_code}',
            'Accept-Language': 'zh-cn'
        }

        try:
            request_data = self.build_request_data(student_code, goods_codes)
            response = requests.post(url, json=request_data, headers=headers)

            result = f"状态码: {response.status_code}\n响应内容:\n{response.text}"
            self.show_result(result)

            if response.status_code == 200:
                messagebox.showinfo("成功", "请求已发送")
            else:
                messagebox.showerror("错误", f"请求失败: {response.status_code}")
        except Exception as e:
            messagebox.showerror("错误", f"请求异常: {str(e)}")
            self.show_result(f"请求异常: {str(e)}")

    def show_result(self, content):
        """显示操作结果"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, content)


if __name__ == "__main__":
    root = tk.Tk()
    app = CourseSelectionApp(root)
    root.mainloop()