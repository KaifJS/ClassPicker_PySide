# core.py
import random
from datetime import datetime
from typing import List
import json
import os
from PySide6.QtWidgets import QMessageBox

class DrawCore:
    def __init__(self):
        self.students = []                # 原始完整学生列表（永不修改）
        self.available_students = []      # 可重复+排除模式下的剩余学生列表
        self.random_permutation = []      # 不重复模式下的预随机排列
        self.current_permutation_index = 0
        self.draw_history = []
        self.student_stats = {}
        self.total_draws_count = 0
        
        self.allow_repeat = False
        self.exclude_after_draw = True
        
        self.cheat_commands = {}
        self.yj_mode = False
        self.yj_target = None
        self.yj_position = None

        self.archive_dir = "saves"
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)

    def load_students(self, students: List[str]):
        self.students = students.copy()
        self.available_students = students.copy()
        self.generate_random_permutation()

    def generate_random_permutation(self):
        if self.students:
            self.random_permutation = self.students.copy()
            random.shuffle(self.random_permutation)
            self.current_permutation_index = 0
            self._apply_cheats_to_permutation()
            self.save_archive()

    def _apply_cheats_to_permutation(self):
        if not self.random_permutation:
            return
        for position, student in self.cheat_commands.items():
            try:
                pos_idx = position - 1
                if 0 <= pos_idx < len(self.random_permutation) and student in self.random_permutation:
                    current_idx = self.random_permutation.index(student)
                    self.random_permutation[pos_idx], self.random_permutation[current_idx] = \
                        self.random_permutation[current_idx], self.random_permutation[pos_idx]
            except:
                pass
        if self.yj_mode and self.yj_target and self.yj_position and self.yj_target in self.random_permutation:
            try:
                target_idx = self.random_permutation.index(self.yj_target)
                self.random_permutation.pop(target_idx)
                insert_pos = self.yj_position - 1 if self.yj_position <= len(self.random_permutation) else len(self.random_permutation)
                self.random_permutation.insert(insert_pos, self.yj_target)
            except:
                pass

    def draw(self, count: int, parent_window=None) -> List[str]:
        if not self.students:
            return []
        if not self.allow_repeat:
            return self._draw_without_repeat(count, parent_window)
        if self.exclude_after_draw:
            return self._draw_repeat_exclude(count, parent_window)
        return self._draw_repeat_include(count)

    def _draw_without_repeat(self, count: int, parent_window=None) -> List[str]:
        if not self.random_permutation:
            self.generate_random_permutation()
        remaining = len(self.random_permutation) - self.current_permutation_index
        if remaining < count:
            if parent_window:
                ret = QMessageBox.question(parent_window, "提示", f"剩余人数不足 ({remaining}/{count})，是否重新生成随机排列？",
                                          QMessageBox.Yes | QMessageBox.No)
                if ret == QMessageBox.Yes:
                    self.reset()
                    remaining = len(self.random_permutation)
                else:
                    return []
            else:
                self.reset()
                remaining = len(self.random_permutation)
            if remaining < count:
                return []
        selected = []
        for i in range(count):
            if self.current_permutation_index < len(self.random_permutation):
                student = self.random_permutation[self.current_permutation_index]
                selected.append(student)
                self.current_permutation_index += 1
        self._record_draw(selected)
        return selected

    def _draw_repeat_exclude(self, count: int, parent_window=None) -> List[str]:
        """可重复+排除模式：使用 available_students 作为剩余池"""
        if not self.students:
            return []
        # 确保 available_students 不为空（若为空，提示重置）
        if not self.available_students:
            if parent_window:
                ret = QMessageBox.question(parent_window, "提示", "所有学生已被抽完，是否重置？",
                                          QMessageBox.Yes | QMessageBox.No)
                if ret == QMessageBox.Yes:
                    self.reset_available_students()
                else:
                    return []
            else:
                self.reset_available_students()
            if not self.available_students:
                return []
        if len(self.available_students) < count:
            if parent_window:
                ret = QMessageBox.question(parent_window, "提示", f"剩余学生不足 ({len(self.available_students)}/{count})，是否重置？",
                                          QMessageBox.Yes | QMessageBox.No)
                if ret == QMessageBox.Yes:
                    self.reset_available_students()
                else:
                    # 抽走剩余的全部
                    count = len(self.available_students)
            else:
                self.reset_available_students()
        # 从 available_students 中随机抽取并移除
        selected = []
        for i in range(min(count, len(self.available_students))):
            idx = random.randrange(len(self.available_students))
            student = self.available_students.pop(idx)
            selected.append(student)
        self._record_draw(selected)
        # 注意：不修改 self.students
        return selected

    def _draw_repeat_include(self, count: int) -> List[str]:
        if not self.students:
            return []
        selected = random.choices(self.students, k=count)
        self._record_draw(selected)
        return selected

    def _record_draw(self, selected: List[str]):
        for student in selected:
            self.draw_history.append(student)
            self.student_stats[student] = self.student_stats.get(student, 0) + 1
        self.total_draws_count += len(selected)

    def reset(self):
        """完全重置：清空历史、统计，恢复不重复模式的排列，恢复可重复+排除模式的剩余池"""
        self.draw_history.clear()
        self.student_stats.clear()
        self.total_draws_count = 0
        self.current_permutation_index = 0
        self.generate_random_permutation()
        self.reset_available_students()

    def reset_available_students(self):
        """重置可重复+排除模式下的剩余学生池（为原始学生列表的副本）"""
        self.available_students = self.students.copy()

    # ---------- 存档功能 ----------
    def save_archive(self):
        if not self.random_permutation:
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"archive_{timestamp}.json"
        filepath = os.path.join(self.archive_dir, filename)
        data = {
            "timestamp": timestamp,
            "students": self.students,
            "random_permutation": self.random_permutation,
            "current_permutation_index": self.current_permutation_index,
            "cheat_commands": self.cheat_commands,
            "yj_mode": self.yj_mode,
            "yj_target": self.yj_target,
            "yj_position": self.yj_position,
            "draw_history": self.draw_history,
            "student_stats": self.student_stats,
            "allow_repeat": self.allow_repeat,
            "exclude_after_draw": self.exclude_after_draw,
            "available_students": self.available_students
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filepath

    def load_archive(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.random_permutation = data["random_permutation"]
        self.current_permutation_index = data["current_permutation_index"]
        if "students" in data:
            self.students = data["students"]
            self.available_students = data.get("available_students", self.students.copy())
        if "cheat_commands" in data:
            self.cheat_commands = data["cheat_commands"]
        if "yj_mode" in data:
            self.yj_mode = data["yj_mode"]
            self.yj_target = data.get("yj_target")
            self.yj_position = data.get("yj_position")
        if "draw_history" in data:
            self.draw_history = data["draw_history"]
        if "student_stats" in data:
            self.student_stats = data["student_stats"]
        if "allow_repeat" in data:
            self.allow_repeat = data["allow_repeat"]
            self.exclude_after_draw = data.get("exclude_after_draw", True)
        # 不重新应用作弊指令，保持存档顺序
        return True

    def list_archives(self):
        if not os.path.exists(self.archive_dir):
            return []
        files = [f for f in os.listdir(self.archive_dir) if f.endswith('.json')]
        files.sort(reverse=True)
        return [os.path.join(self.archive_dir, f) for f in files]

    def get_archive_info(self, filepath: str):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            timestamp = data.get("timestamp", "未知")
            student_count = len(data.get("students", []))
            remaining = len(data.get("random_permutation", [])) - data.get("current_permutation_index", 0)
            return {
                "timestamp": timestamp,
                "student_count": student_count,
                "remaining": remaining,
                "filepath": filepath
            }
        except:
            return None

    # ---------- 作弊指令 ----------
    def process_cheat_command(self, command: str) -> str:
        try:
            cmd = command.strip()
            if cmd.startswith('/set(') and cmd.endswith(')'):
                return self._set_command(cmd)
            elif cmd == '/ys1':
                return self._ys1_command()
            elif cmd == '/ys2':
                return self._ys2_command()
            elif cmd == '/ys3':
                return self._ys3_command()
            elif cmd == '/yj':
                return self._yj_command()
            elif cmd == '/clear':
                return self._clear_command()
            elif cmd.startswith('/swap(') and cmd.endswith(')'):
                return self._swap_command(cmd)
            elif cmd.startswith('/move(') and cmd.endswith(')'):
                return self._move_command(cmd)
            elif cmd == '/shuffle':
                return self._shuffle_command()
            elif cmd == 'v':
                return self._view_command()
            else:
                return "未知命令"
        except Exception as e:
            return f"执行失败: {str(e)}"

    def _set_command(self, command: str) -> str:
        content = command[5:-1]
        parts = content.split(',')
        if len(parts) != 2:
            return "格式错误，应为 /set(位置,学号)"
        try:
            position = int(parts[0].strip())
            student = parts[1].strip()
            if position <= 0:
                return "位置必须大于0"
            self.cheat_commands[position] = student
            if self.random_permutation:
                self.generate_random_permutation()
            return "状态已更新"
        except ValueError:
            return "参数错误"

    def _ys1_command(self) -> str:
        self.cheat_commands[2] = '3'
        self.cheat_commands[5] = '13'
        self.generate_random_permutation()
        return "状态已更新"

    def _ys2_command(self) -> str:
        self.cheat_commands[4] = '3'
        self.cheat_commands[3] = '13'
        self.generate_random_permutation()
        return "状态已更新"

    def _ys3_command(self) -> str:
        self.cheat_commands[6] = '3'
        self.cheat_commands[1] = '13'
        self.generate_random_permutation()
        return "状态已更新"

    def _yj_command(self) -> str:
        if not self.students or '54' not in self.students:
            return "执行失败：没有学号54"
        self.yj_mode = True
        self.yj_target = '54'
        self.yj_position = len(self.students)
        self.generate_random_permutation()
        return "状态已更新"

    def _clear_command(self) -> str:
        self.cheat_commands.clear()
        self.yj_mode = False
        self.yj_target = None
        self.yj_position = None
        self.generate_random_permutation()
        return "状态已重置"

    def _swap_command(self, command: str) -> str:
        if not self.random_permutation:
            return "请先生成随机排列列表"
        content = command[6:-1]
        parts = content.split(',')
        if len(parts) != 2:
            return "格式错误，应为 /swap(位置1,位置2)"
        try:
            pos1 = int(parts[0].strip()) - 1
            pos2 = int(parts[1].strip()) - 1
            if 0 <= pos1 < len(self.random_permutation) and 0 <= pos2 < len(self.random_permutation):
                self.random_permutation[pos1], self.random_permutation[pos2] = \
                    self.random_permutation[pos2], self.random_permutation[pos1]
                return f"已交换位置 {pos1+1} 和 {pos2+1}"
            return "位置超出范围"
        except ValueError:
            return "参数错误"

    def _move_command(self, command: str) -> str:
        if not self.random_permutation:
            return "请先生成随机排列列表"
        content = command[6:-1]
        parts = content.split(',')
        if len(parts) != 2:
            return "格式错误，应为 /move(原位置,新位置)"
        try:
            from_pos = int(parts[0].strip()) - 1
            to_pos = int(parts[1].strip()) - 1
            if 0 <= from_pos < len(self.random_permutation) and 0 <= to_pos < len(self.random_permutation):
                student = self.random_permutation.pop(from_pos)
                self.random_permutation.insert(to_pos, student)
                return f"已将位置 {from_pos+1} 的学号移动到位置 {to_pos+1}"
            return "位置超出范围"
        except ValueError:
            return "参数错误"

    def _shuffle_command(self) -> str:
        if not self.random_permutation:
            return "请先生成随机排列列表"
        current_index = self.current_permutation_index
        remaining = self.random_permutation[current_index:]
        random.shuffle(remaining)
        self.random_permutation = self.random_permutation[:current_index] + remaining
        self._apply_cheats_to_permutation()
        return "已重新洗牌剩余学号"

    def _view_command(self) -> str:
        if not self.random_permutation:
            return "当前没有随机排列列表，请先设置学生名单"
        lines = [f"随机排列列表 (共{len(self.random_permutation)}个学号)",
                 f"当前抽取位置: {self.current_permutation_index + 1}",
                 f"已抽取: {self.current_permutation_index} 个",
                 f"剩余: {len(self.random_permutation) - self.current_permutation_index} 个",
                 "=" * 50]
        for i, student in enumerate(self.random_permutation, 1):
            prefix = "-> " if i == self.current_permutation_index + 1 else "   "
            lines.append(f"{prefix}{i:3d}. {student}")
        return "\n".join(lines)

    # ---------- 统计与导出 ----------
    def get_statistics_info(self) -> str:
        if not self.student_stats:
            return "暂无统计信息\n\n请先进行抽取操作"
        total_draws = sum(self.student_stats.values())
        info = f"统计概览\n{'='*40}\n"
        info += f"总抽取次数: {total_draws}\n"
        info += f"总学生数量: {len(self.students)}\n"
        info += f"已抽取学生: {len(self.student_stats)}\n"
        info += f"未抽取学生: {len(self.students) - len(self.student_stats)}\n"
        info += f"随机排列列表长度: {len(self.random_permutation) if self.random_permutation else 0}\n"
        info += f"当前抽取位置: {self.current_permutation_index}\n"
        info += f"剩余学号(不重复模式): {len(self.random_permutation) - self.current_permutation_index if self.random_permutation else 0}\n\n"
        info += "抽取频率排行:\n" + "-"*40 + "\n"
        sorted_stats = sorted(self.student_stats.items(), key=lambda x: x[1], reverse=True)
        for student, count in sorted_stats[:15]:
            percentage = (count / total_draws * 100) if total_draws > 0 else 0
            info += f"{student}: {count}次 ({percentage:.1f}%)\n"
        if len(sorted_stats) > 15:
            info += f"\n... 还有 {len(sorted_stats) - 15} 个学生\n"
        return info

    def export_results(self, filename: str = None) -> str:
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"抽号结果_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("抽号系统导出结果\n")
            f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总抽取次数: {self.total_draws_count}\n")
            f.write(f"随机排列列表: {self.random_permutation}\n")
            f.write(f"当前抽取位置: {self.current_permutation_index}\n")
            f.write("=" * 50 + "\n")
            if self.draw_history:
                f.write("抽取历史:\n")
                for i, student in enumerate(self.draw_history, 1):
                    f.write(f"{i}. {student}\n")
            f.write("\n统计信息:\n")
            total = sum(self.student_stats.values())
            for student, count in sorted(self.student_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total * 100) if total > 0 else 0
                f.write(f"{student}: {count}次 ({percentage:.1f}%)\n")
        return filename

    # ---------- 人员管理 ----------
    def add_student(self, name: str) -> str:
        max_num = 0
        for stu in self.students:
            if '.' in stu:
                try:
                    num = int(stu.split('.')[0])
                    if num > max_num:
                        max_num = num
                except:
                    pass
        new_num = max_num + 1
        new_stu = f"{new_num:02d}.({name})"
        self.students.append(new_stu)
        self.available_students.append(new_stu)
        self.generate_random_permutation()
        return new_stu

    def delete_student(self, student: str) -> bool:
        if student in self.students:
            self.students.remove(student)
            if student in self.available_students:
                self.available_students.remove(student)
            self.generate_random_permutation()
            return True
        return False

    def edit_student(self, old_student: str, new_name: str) -> str:
        if '.' in old_student and '(' in old_student:
            stu_num = old_student.split('.')[0]
            new_stu = f"{stu_num}.({new_name})"
        else:
            new_stu = new_name
        idx = self.students.index(old_student)
        self.students[idx] = new_stu
        # 同步更新 available_students
        if old_student in self.available_students:
            idx2 = self.available_students.index(old_student)
            self.available_students[idx2] = new_stu
        self.generate_random_permutation()
        return new_stu

    def get_students(self):
        return self.students