'''build the commands to run in Bsub'''
import re
import sys
import subprocess 

ENCODING = 'utf-8'

# get the command from cli
shell_command = sys.argv[1]
print(f'this is the input from cli: \n {shell_command}')

# run the command and grab the output
subprocess = subprocess.Popen([shell_command],
                        shell=True, stdout=subprocess.PIPE)
file_names = [byte.decode(ENCODING) for
              byte in subprocess.stdout.read().splitlines()]
print(f'these are some of the file names'\
      f'you asked for:\n{file_names[:10]}')


reg_expression = r'^\w+_\w+_\w+_R'
reg_compile = re.compile(reg_expression)
matched_strings = []

with open('cutadapt_commands', 'w') as output_file:
    for file_name in file_names:

        # match the regax expression
        match = reg_compile.match(file_name)
        matched_str = match.group()

        command_for_submission = f'cutadapt -a AGATCGGAAGAGCACACGTCTGAACTCCAGTCA -A AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT --times 2 -q 30 -m 20 -o 02_trimmed_reads/{matched_str}_R1_trimmed.fastq -p 02_trimmed_reads/{matched_str}_R2_trimmed.fastq 01.fastq/{matched_str}/_R1_001.fastq.gz 01.fastq\/{matched_str}_R2_001.fastq.gz/'
        output_file.write(command_for_submission)
        output_file.write('\n')










