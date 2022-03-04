# file: JavaHelper.py
import subprocess
javaPath = "E:\\Java\\jdk-11.0.14+9\\bin\\javac"

'''
Compiles a single java file
'''
def compileJava(filePath):
    javaArgs = f"{javaPath} {filePath}"
    # shell=True?
    procContext = subprocess.Popen(javaArgs, shell=True,env = {"PATH": "."},stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    procContext.wait()
    print(f"Exit-Code={procContext.returncode}")
    javaCOutput = procContext.stdout.read()
    print(javaCOutput)
