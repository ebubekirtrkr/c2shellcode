import os.path as path

class Syscall:
    def __init__(self, sys_number: int, name: str, argumentLength: int) -> None:
        self.sys_number = sys_number
        self.name = name
        self.syntax=""
        self.__argumentLength = argumentLength
        self.__setSyntax()

    def __setSyntax(self) -> None:
        tab = " "*4
        self.syntax += tab + f"mov rax, {self.sys_number}\n"
        if self.__argumentLength > 3:
            self.syntax += tab + "mov r10, rcx\n"
        self.syntax += tab + "syscall\n"

    def getSyntax(self) -> str:
        return self.syntax


class SyscallTable:
    def __init__(self) -> None:
        self.__syscallTable = []

    def getSyscallFromId(self, sys_number: int) -> Syscall:
        for syscall in self.__syscallTable:
            if syscall.sys_number == sys_number:
                return syscall
        else:
            return None

    def getSyscallFromName(self, name: str) -> Syscall:
        for syscall in self.__syscallTable:
            if syscall.name == name:
                return syscall
        else:
            return None

    def addSyscall(self, sys_number: int, name: str, argLength: int) -> None:
        self.__syscallTable.append(Syscall(sys_number, name, argLength))

    def addSyscallFromCsv(self, inputCsvFilename: str) -> None:
        inputCsv = open(inputCsvFilename, "r")
        lines = inputCsv.read().splitlines()[1:]
        for line in lines:
            name, sys_number, arg_len= list(map(str.strip, line.split(',')))[:3]
            self.addSyscall(int(sys_number), name, int(arg_len))

class asmParser:
    def __init__(self, inputFile: str, syscallTable: SyscallTable=None, outputFile: str = None) -> None:
        self.__labels = []
        self.output = ""
        self.__inputFile = open(inputFile, "r").read().splitlines()
        self.outputFile = outputFile
        if syscallTable==None:
            self.syscallTable = SyscallTable()
            self.syscallTable.addSyscallFromCsv(path.join(path.dirname(path.realpath(__file__)),"syscalls.csv"))
        self.process()

    def process(self):
        self.__getLabels()
        self.__addHeader()
        self.__getMainCode()
        self.__addLabels()

    def getShellcode(self) -> str:
        if self.outputFile == None:
            print(self.output)
        else:
            outputF = open(self.outputFile, "w+")
            outputF.write(self.output)
            outputF.close()

    def __getMainCode(self):
        codeLines = iter(self.__inputFile)
        tab = " "*4
        for codeLine in codeLines:
            if(codeLine != "main:"):
                continue
            else:
                while(not codeLine.strip().startswith(".")):
                    if "main" in codeLine:
                        codeLine = "_start:"
                    elif "call" in codeLine:
                        syscallName = codeLine.split('\t')[-1].split('@')[0]
                        codeLine = tab + "# "+codeLine.strip()+"\n"
                        syscall = self.syscallTable.getSyscallFromName(name=syscallName)
                        codeLine += syscall.getSyntax()
                    else:
                        codeLine = tab+codeLine
                    self.output += codeLine+"\n"
                    codeLine = next(codeLines, None).strip()

    def __getLabels(self) -> None:
        codeLines = iter(self.__inputFile)
        for codeLine in codeLines:
            if(codeLine == "main:"):
                break
            if(codeLine.startswith(".L")):
                self.__labels.append({
                    "label": codeLine,
                    "value": next(codeLines, None)
                })

    def __addLabels(self) -> None:
        for label in self.__labels:
            self.output += label['label']+"\n"
            self.output += label['value']+"\n"

    def __addHeader(self) -> None:
        header = ".global _start\n.intel_syntax noprefix"
        self.output += header+"\n"

if __name__=="__main__":
    import argparse,subprocess,os

    arg_parser = argparse.ArgumentParser(prog='python3 c2shellcode.py',
                                        usage='%(prog)s -[d] <input>.c <output>.s',
                                        description='Convert c code to shellcode assembly',
                                        prefix_chars='-')

    arg_parser.add_argument('-d',
                        help="do not delete intermediate files",
                        action='store_false')
    arg_parser.add_argument('input',
                        metavar='<input file>',
                        type=str,
                        help='input .c filename')
    arg_parser.add_argument('output',
                        metavar='<output file>',
                        type=str,
                        help='output .s filename')
    args = arg_parser.parse_args()
    input_file=os.path.realpath(args.input)
    output_file=os.path.realpath(args.output)
    process = subprocess.Popen(f"gcc  {input_file} -o {input_file[:-2]}_temp.s -O0  -nostdlib -fno-asynchronous-unwind-tables -fno-ident -finhibit-size-directive  -S -Wno-unused-result -masm=intel -m64", shell=True)
    process.wait()
    c2s = asmParser(f"{input_file[:-2]}_temp.s",outputFile=output_file)
    c2s.getShellcode()
    if not args.d:
        os.remove(f"{input_file[:-2]}_temp.s")
