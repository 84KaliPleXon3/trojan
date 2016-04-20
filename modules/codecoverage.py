#!/usr/bin/python
#-*- coding:utf-8 -*-
#简单逆向工程，分析计算器进程所有函数，插入断点
from immlib import *

class cc_hook(LogBpHook):

    def __init__(self):
        LogBpHook.__init__(self)
        self.imm = Debugger()

    def run(self, regs):
        self.imm.log("%08x" % regs['EIP'], regs['EIP'])
        self.imm.deleteBreakpoint(regs['EIP'])
        return


def main(args):
    #实例化Debugger
    imm = Debugger()
    #运行calc.exe
    calc = imm.getModule("calc.exe")
    #分析进程源代码
    imm.analyseCode(calc.getCodebase())
    #分析完成后获取全部函数
    functions = imm.getAllFunctions(calc.getCodebase())

    #断点设置
    hooker = cc_hook()
    for function in functions:
        hooker.add("%08x" % function, function)

    return "Tracking %d functions." % len(functions)

    Status API Training Shop Blog About 


