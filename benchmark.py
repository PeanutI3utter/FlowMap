import subprocess
import re
import os

ABCLUTex = re.compile("nd\s*=\s*(\d+)")
MT2LUTex = re.compile("Post optimisation:\s*(\d+)")
CECex = re.compile("Networks are equivalent")

resultFile = open("benchmark_results.csv","w")
resultFile.write("file;equivalent;MT2_LUTs;ABC_LUTs\n")
error = False

inputfiles = list(filter(lambda x: x.endswith('.blif'), os.listdir('./benchmarks')))
i = 1

for f in inputfiles:
    inputfile = "./benchmarks/"+f
    
    print(f"\rbenchmarking file "+str(i)+" out of "+str(len(inputfiles))+" : "+f)
    i = i + 1

    try:
        error = False

        MT2output = subprocess.Popen(["wsl", "python3", "main.py", inputfile, "6"], stdout=subprocess.PIPE).communicate()[0]
        MT2output = MT2output.decode("utf-8")

        m = MT2LUTex.findall(MT2output)
        MT2numLUTs = m[0]

        MT2outputfile = "top_mapped_opt.blif"
        abcinput = "read_lut 6-lut-lib\nread_blif "+inputfile+"\nfpga\nprint_stats\nwrite_blif abcoutput.blif\ncec abcoutput.blif "+MT2outputfile
        scr = open("abcbench.scr", "w")
        scr.write(abcinput)
        scr.close()

        abcoutput = subprocess.Popen(["./abc.exe", "-f abcbench.scr"], stdout=subprocess.PIPE).communicate()[0]
        abcoutput = abcoutput.decode("utf-8")


        m = ABCLUTex.findall(abcoutput)
        ABCnumLUTs = m[0]

        equiv = CECex.search(abcoutput) != None
    except:
        error = True

    resultFile.write(inputfile+";")
    if (error):
        resultFile.write("-1;-1;-1\n")
    else:
        resultFile.write(("1;" if equiv else "0;")+str(MT2numLUTs)+";"+str(ABCnumLUTs)+"\n")
        
    
    
resultFile.close()
