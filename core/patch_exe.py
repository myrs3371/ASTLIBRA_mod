#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import shutil

def patch_exe(exe_path):
    # 要搜索的字节序列
    search_bytes = bytes([0x89, 0x41, 0xF8, 0x8B, 0x41, 0xFC, 0xC1, 0xC8, 0x04, 0x89, 0x41, 0xFC])
    # 要替换成的字节序列
    replace_bytes = bytes([0x90, 0x90, 0x90, 0x8B, 0x41, 0xFC, 0xC1, 0xC8, 0x04, 0x90, 0x90, 0x90])

    # 备份原文件
    base, ext = os.path.splitext(exe_path)
    backup_path = base + '_back' + ext
    print(f"备份原文件到: {backup_path}")
    shutil.copy2(exe_path, backup_path)

    # 读取文件
    with open(exe_path, 'rb') as f:
        data = f.read()

    # 查找字节序列
    offset = data.find(search_bytes)

    if offset == -1:
        print("错误：未找到目标字节序列")
        return False

    print(f"找到目标位置，偏移: 0x{offset:X}")

    # 替换字节
    modified_data = data[:offset] + replace_bytes + data[offset+len(replace_bytes):]

    # 写入修改后的文件
    with open(exe_path, 'wb') as f:
        f.write(modified_data)

    print("修改成功！")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python patch_exe.py <游戏.exe路径>")
        print("示例: python patch_exe.py ASTLIBRA.exe")
        sys.exit(1)
    patch_exe(sys.argv[1])
